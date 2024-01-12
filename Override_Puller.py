#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import xml.etree.ElementTree as ET

# Global variables
file = ""
master = {}


def get_vertex_key(root, top_function, source_key, parent_map):
    """
    Get the vertex key from the XML structure.
    """
    elements_with_vertexkey = root.findall(f".//*[@vertexkey='{source_key}']")

    for element in elements_with_vertexkey:
        current_element = element
        for _ in range(5):  # Traverse 5 levels up
            if current_element is None:
                break
            current_element = parent_map.get(current_element)

        if current_element is not None and current_element.tag == "structure":
            sixth_parent = parent_map.get(current_element)
            if sixth_parent == top_function:
                parent_of_element = parent_map.get(element)
                return parent_of_element.attrib.get("vertexkey")

    return None


def pretty_print(nested_dict):
    """
    Create a formatted string representation of the nested dictionary.
    """
    lines = []
    for key, sub_dict in sorted(nested_dict.items()):
        lines.append(f"{key}\n")
        for sub_key, values in sorted(sub_dict.items()):
            formatted_values = "\n\t\t".join(str(value) for value in sorted(values)) if values else ""
            lines.append(f"\t{sub_key}\n\t\t{formatted_values}\n")
        lines.append("----------------------------------------------------------\n")

    return "".join(lines)


def parse_dependency_block(dep_lines, start_index):
    """
    Parse a dependency block from the pom file lines.
    """
    dependency_info = {"groupId": "", "artifactId": "", "version": "", "type": ""}
    index = start_index + 1
    while "</dependency>" not in dep_lines[index]:
        label = dep_lines[index].strip().split(">")[0].split("<")[-1]
        if label in dependency_info:
            dependency_info[label] = dep_lines[index].strip().split(">")[1].split("<")[0]
        index += 1
    return dependency_info


def get_dependency_tree(path):
    """
    Get the dependency tree from the pom file.
    """
    dep_tree_dict = {}
    dependencies = {}
    try:
        with open(path, "r") as pom:
            dep_lines = pom.readlines()
            for index, line in enumerate(dep_lines):
                if "<dependency>" in line and "com.cerner.pophealth.mappings." in dep_lines[index + 1]:
                    dep_info = parse_dependency_block(dep_lines, index)
                    if dep_info["type"] == "mfd":
                        group_id = dep_info["groupId"]
                        dependencies[group_id] = {"dependency_mfd_name": dep_info["artifactId"], "version": dep_info["version"]}
    except IOError as e:
        print(f"Error reading file {path}: {e}")
        return None

    repository_paths = [
        "C:\\m2\\repository\\com\\cerner\\pophealth\\mappings",
        "C:\\.m2\\repository\\com\\cerner\\pophealth\\mappings",
    ]
    for group_id, dep in dependencies.items():
        for repo_path in repository_paths:
            dependency_path = os.path.join(repo_path, group_id, dep["dependency_mfd_name"], dep["version"])
            if handle_dependency_path(dependency_path, dep, dep_tree_dict, path):
                break

    return dep_tree_dict


def handle_dependency_path(dependency_path, dep, dep_tree_dict, original_path):
    """
    Handle the dependency path for the tree.
    """
    if os.path.exists(dependency_path):
        for dep_file in os.listdir(dependency_path):
            if dep_file.endswith(".mfd"):
                dep_full_path = os.path.join(dependency_path, dep_file)
                tree = ET.parse(dep_full_path)
                dep_root = tree.getroot()
                dep_tree_dict[dep_root] = f"{dep['dependency_mfd_name']}-{dep['version']}"
        return True
    else:
        pull_dependencies(original_path)
        return False


def pull_dependencies(path):
    """
    Pull dependencies using Maven.
    """
    try:
        os.chdir(os.path.dirname(path))
        mci = os.system("mvn midas:mapforce-env")
        if mci != 0:
            print("Error running mvn midas:mapforce-env command. Please check manually.")
            input("Hit enter to continue...")
            quit()
    finally:
        os.chdir(os.getcwd())


def get_dependencies(dep_tree_dict):
    """
    Get dependencies from the dependency tree.
    """
    dep_record = {}
    for dep_root, dep_name in dep_tree_dict.items():
        parent_map = {child: parent for parent in dep_root.iter() for child in parent}

        for sources in dep_root.findall(".//*[@name='getKeyedValue']/sources"):
            component_ancestor = get_ancestor(parent_map, sources, 4)
            source_key = sources[0].attrib["key"]
            vertex = find_vertex(dep_root, parent_map, source_key)

            if vertex and component_ancestor.tag == "component":
                for component in dep_root.findall(".//*[@name='constant']"):
                    if valid_dependency(component, vertex, component_ancestor):
                        update_dependency_record(dep_root, dep_record, dep_name, component, component_ancestor)

    return dep_record


def get_ancestor(parent_map, node, levels):
    """Get an ancestor of a given node in the XML tree at a specified level."""
    ancestor = node
    for _ in range(levels):
        ancestor = parent_map.get(ancestor, None)
        if ancestor is None:
            break
    return ancestor


def find_vertex(dep_root, parent_map, source_key):
    """Find a vertex in the dependency tree that matches a given source key."""
    command = ".//*[@vertexkey='" + source_key + "']"
    for item in dep_root.findall(command):
        if parent_map[parent_map[item]].tag == "vertex":
            return parent_map[parent_map[item]]
    return None



def valid_dependency(component, vertex, component_ancestor):
    """Check if a component is a valid dependency."""
    return (
        "key" in component[1][0].attrib
        and "vertexkey" in vertex.attrib
        and component[1][0].attrib["key"] == vertex.attrib["vertexkey"]
        and component_ancestor.attrib["name"] == component[1][0].attrib["name"]
        and "value" in component[-1][0].attrib
    )



def update_dependency_record(dep_root, dep_record, dep_name, component, component_ancestor):
    """Update the dependency record with information about a valid dependency."""
    function_name = get_ancestor(parent_map, component, 3).attrib["name"]
    library_name = get_ancestor(parent_map, component, 3).attrib["library"]

    for dep_component in dep_root.findall("./"):
        if (
            "name" in dep_component.attrib
            and component_ancestor.attrib["name"] == dep_component.attrib["name"]
            and component_ancestor.attrib["library"] == dep_component.attrib["library"]
            and function_name == component_ancestor.attrib["name"]
            and library_name == component_ancestor.attrib["library"]
        ):
            formatted_dep_name = f"{dep_name} : {component_ancestor.attrib['library']}"
            if formatted_dep_name not in dep_record:
                dep_record[formatted_dep_name] = {}
            if component_ancestor.attrib["name"] not in dep_record[formatted_dep_name]:
                dep_record[formatted_dep_name][component_ancestor.attrib["name"]] = []
            dep_record[formatted_dep_name][component_ancestor.attrib["name"]].append(
                component[-1][0].attrib["value"]
            )



def get_overrides(local_root, file, dependency_dictionary=""):
    """Process overrides within a local mapping and update the master record."""
    global master, parent_map

    parent_map = {c: p for p in local_root.iter() for c in p}
    master = {}  # Assuming 'master' is a global dictionary
    dep_count, override_count = 0, 0

    # Process the main mapping logic
    override_count += process_main_mappings(local_root, file)

    # Process the dependencies if provided
    if dependency_dictionary:
        dep_count += process_dependencies(local_root, dependency_dictionary, file)

    # Final calculations and logging
    function_frequency, local_count = calculate_function_frequency(local_root)
    check_override_counts(
        dep_count, local_count, override_count, file)



def process_main_mappings(local_root, file):
    """Process overrides within the main mappings of a local mapping file."""
    override_count = 0
    for sources in local_root.findall(".//*[@name='getKeyedValue']/sources"):
        top_function = get_ancestor(parent_map, sources, 4)
        source_key = sources[0].attrib["key"]
        vertex_key = get_vertex_key(local_root, top_function, source_key)
        override_count += process_vertex_key(top_function, vertex_key, file)
    return override_count



def process_dependencies(local_root, dependency_dictionary, file):
    """Process overrides within the dependencies of a local mapping file."""
    dep_count = 0
    for local_function in local_root.iter("component"):
        for split, override_list in dependency_dictionary.items():
            dep_name, dep_library = split.split(" : ")
            if (
                local_function.attrib["name"] in override_list
                and local_function.attrib["library"] == dep_library
            ):
                dep_count += 1
                update_master_record(
                    file, f'{dep_name} : {local_function.attrib["name"]}', override_list
                )
    return dep_count



def process_vertex_key(top_function, vertex_key, file):
    """Process overrides for a specific vertex key within a local mapping."""
    override_count = 0
    for datapoint in top_function.findall(
        f".//*[@name='constant']/targets/datapoint/[@key='{vertex_key}']"
    ):
        override = parent_map[parent_map[datapoint]][-1][0].attrib["value"]
        function_info = f"{top_function.attrib['name']} : local"
        override_count += 1
        update_master_record(file, function_info, [override])
    return override_count



def calculate_function_frequency(local_root):
    """Calculate the frequency of each function in the local mapping."""
    function_frequency = {}
    for item in local_root.findall(".//*[@name='getKeyedValue']/sources"):
        function_name = get_ancestor(parent_map, item, 4).attrib["name"]
        function_frequency[function_name] = function_frequency.get(function_name, 0) + 1
    local_count = sum(function_frequency.values())
    return function_frequency, local_count



def check_override_counts(
    dep_count, local_count, override_count, file):
    """Check if the override counts match the expected counts and update the master record accordingly."""
    global master

    if override_count != dep_count + local_count:
        update_master_record(
            file, "!!! OVERRIDES STILL EXIST IN MAPPING NOT LISTED HERE !!!", []
        )
    elif dep_count == 0 and local_count == 0 and override_count == 0:
        update_master_record(file, "NO MAPPING OVERRIDES DETECTED", [])
    else:
        print("\t\t\t\t[RESULTS] FOUND OVERRIDES!")


def update_master_record(file, key, values):
    """Update the master record with the provided key and values."""
    global master

    if file not in master:
        master[file] = {}
    if key not in master[file]:
        master[file][key] = []
    master[file][key].extend(values)


def get_ancestor(parent_map, node, levels):
    """Get the ancestor of a node in the XML tree."""
    ancestor = node
    for _ in range(levels):
        ancestor = parent_map.get(ancestor, None)
        if ancestor is None:
            break
    return ancestor


def process_directory(walk_path, walk_files):
    """
    Process each directory found in os.walk.
    """
    if "pom.xml" in walk_files and any(file.endswith(".mfd") for file in walk_files):
        handle_pom_and_mfd(walk_path, walk_files)
    elif "pom.xml" not in walk_files and any(file.endswith(".mfd") for file in walk_files):
        handle_mfd_only(walk_path, walk_files)



def handle_pom_and_mfd(walk_path, walk_files):
    """
    Handle directories containing both pom.xml and .mfd files.
    """
    print(f"\n[INFO] DEPENDENCY CHECK NEEDED FOR {os.path.basename(walk_path)}")
    pom_path = os.path.join(walk_path, "pom.xml")
    for file in walk_files:
        if file.endswith(".mfd"):
            mfd_path = os.path.join(walk_path, file)
            process_files(pom_path, mfd_path)

def handle_mfd_only(walk_path, walk_files):
    """
    Handle directories containing only .mfd files.
    """
    print(f"[INFO] NO DEPENDENCY PULL NEEDED FOR {os.path.basename(walk_path)}")
    for file in walk_files:
        if file.endswith(".mfd"):
            mfd_path = os.path.join(walk_path, file)
            root = ET.parse(mfd_path).getroot()
            get_overrides(root, file)


def process_files(pom_path, mfd_path):
    """
    Process the files for dependency and override information.
    """
    dependency_tree = get_dependency_tree(pom_path)
    root = ET.parse(mfd_path).getroot()

    if not dependency_tree:
        handle_no_dependencies(root, mfd_path)
        return

    dependencies = get_dependencies(dependency_tree)
    if not dependencies:
        handle_no_dependencies(root, mfd_path)
        return

    handle_dependencies(root, mfd_path, dependencies)

def handle_no_dependencies(root, mfd_path):
    """
    Handle the case when no dependencies are found.
    """
    print(f"\t\tGetting overrides from {os.path.basename(mfd_path)}")
    get_overrides(root, os.path.basename(mfd_path))

def handle_dependencies(root, mfd_path, dependencies):
    """
    Handle dependencies for overrides.
    """
    for key in dependencies:
        if not key.startswith("local"):
            print(f"\t\tGetting overrides from {key}")
            get_overrides(root, os.path.basename(mfd_path), dependencies)


def pretty_print_and_write_output():
    """
    Pretty print the results and write to an output file.
    """
    with open("override_results.txt", "w") as outputfile:
        if master:
            outputfile.write(pretty_print(master))
        else:
            outputfile.write("NO MFD FOUND IN DIRECTORY")


print("Grabbing overrides...")
for walk_path, _, walk_files in os.walk(".", topdown=False):
    process_directory(walk_path, walk_files)

pretty_print_and_write_output()
print("SUCCESS!")
os.startfile("override_results.txt")
