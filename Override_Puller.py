#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import xml.etree.ElementTree as ET

file = ''
master = {}


def getVertexKey(_root, _top_function, _source_key):
    for obj in _root.findall(".//*[@vertexkey='{}']".format(_source_key)):
        if parent_map[parent_map[parent_map[parent_map[parent_map[obj]]]]].tag == 'structure' and parent_map[parent_map[parent_map[parent_map[parent_map[parent_map[obj]]]]]] == _top_function:
            return parent_map[parent_map[obj]].attrib['vertexkey']


def PrettyPrint(_dict):
    _lines = ''
    for k, v in sorted(_dict.items()):
        #print('\n{}'.format(k))
        _lines += '{}\n\n'.format(k)
        for kk, vv in sorted(v.items()):
            #print('\t{}\n\t\t{}'.format(kk, '\n\t\t'.join(str(x) for x in sorted(vv))))
            if vv:
                _lines += '\t{}\n\t\t{}\n\n'.format(kk, '\n\t\t'.join(str(x) for x in sorted(vv)))
            else:
                _lines += '\t{}\n\n'.format(kk)
        #print('----------------------------------------------------------')
        _lines += '----------------------------------------------------------\n'
    return _lines


def getDependencyTree(_path):
    version = ''
    dependencies = {}
    _dep_tree_dict = {}
    with open(_path, 'r') as pom:
        dep_lines = pom.readlines()
    for index in range(len(dep_lines)):
        if '<dependency>' in dep_lines[index] and 'com.cerner.pophealth.mappings.' in dep_lines[index + 1]:
            groupId = ''
            artifactId = ''
            version = ''
            type = ''
            dep_record = {}
            _index = index + 1
            while '</dependency>' not in dep_lines[_index]:
                label = dep_lines[_index].strip().split('>')[0].split('<')[-1]
                if label == 'groupId':
                    groupId = dep_lines[_index].strip().split('com.cerner.pophealth.mappings.')[-1].split('<')[0]
                elif label == 'artifactId':
                    artifactId = dep_lines[_index].strip().split('>')[1].split('<')[0]
                elif label == 'version':
                    version = dep_lines[_index].strip().split('>')[1].split('<')[0]
                elif label == 'type':
                    type = dep_lines[_index].strip().split('>')[1].split('<')[0]
                _index += 1

            if type == 'mfd':
                dep_record['dependency_mfd_name'] = artifactId
                dep_record['version'] = version

                if groupId not in dependencies.keys():
                    dependencies[groupId] = []
                dependencies[groupId] = dep_record
    m2 = 'C:\\m2\\repository\\com\\cerner\\pophealth\\mappings'
    dot_m2 = 'C:\\.m2\\repository\\com\\cerner\\pophealth\\mappings'
    for k, v in dependencies.items():
        dependency_path1 = 'C:\\m2\\repository\\com\\cerner\\pophealth\\mappings\\{}\\{}\\{}'.format(k, v['dependency_mfd_name'], v['version'])
        dependency_path2 = 'C:\\.m2\\repository\\com\\cerner\\pophealth\\mappings\\{}\\{}\\{}'.format(k, v['dependency_mfd_name'], v['version'])
        if os.path.exists(m2):
            # CHECK IF DEP IS THERE
            if os.path.exists(dependency_path1):
                # ALREADY PULLED
                print('\t{}-{} already exists, no need to pull'.format(v['dependency_mfd_name'], v['version']))
                for dep_file in os.listdir(dependency_path1):
                    if dep_file == v['dependency_mfd_name'] + '-' + v['version'] + '.mfd':
                        dep = '{}\\{}'.format(dependency_path1, dep_file)
                        tree = ET.parse(dep)
                        _dep_root = tree.getroot()
                        if version != '':
                            _dep_tree_dict[_dep_root] = v['dependency_mfd_name'] + "-" + version
                        else:
                            _dep_tree_dict[_dep_root] = 'local'
            # DEP IS NOT THERE
            else:
                wd = os.getcwd()
                os.chdir('\\'.join(str(x) for x in _path.split('\\')[:-1]))
                print('\t{}-{} not found, pulling dependencies...'.format(v['dependency_mfd_name'], v['version']))
                mci = os.system('mvn midas:mapforce-env')
                print(mci)
                os.chdir(wd)
                if mci == 0:
                    if os.path.exists(dependency_path1):
                        # ALREADY PULLED
                        for dep_file in os.listdir(dependency_path1):
                            if dep_file == v['dependency_mfd_name'] + '-' + v['version'] + '.mfd':
                                dep = '{}\\{}'.format(dependency_path1, dep_file)
                                tree = ET.parse(dep)
                                _dep_root = tree.getroot()
                                _dep_tree_dict[_dep_root] = v['dependency_mfd_name'] + "-" + version
                else:
                    print("COULD NOT COMPLETE mvn midas:mapforce-env command on {}\nTry to run the mvn clean install command on the master branch manually and see what went wrong".format(os.getcwd()))
                    r = raw_input("Hit enter to continue...")
                    quit()
        elif os.path.exists(dot_m2):
            # CHECK IF DEP IS THERE
            if os.path.exists(dependency_path2):
                # ALREADY PULLED
                print('\t{}-{} already exists, no need to pull'.format(v['dependency_mfd_name'], v['version']))
                for dep_file in os.listdir(dependency_path2):
                    if dep_file == v['dependency_mfd_name'] + '-' + v['version'] + '.mfd':
                        dep = '{}\\{}'.format(dependency_path2, dep_file)
                        tree = ET.parse(dep)
                        _dep_root = tree.getroot()
                        if version != '':
                            _dep_tree_dict[_dep_root] = v['dependency_mfd_name'] + "-" + version
                        else:
                            _dep_tree_dict[_dep_root] = 'local'
            # DEP IS NOT THERE
            else:
                wd = os.getcwd()
                os.chdir('\\'.join(str(x) for x in _path.split('\\')[:-1]))
                print('\t{}-{} not found, pulling dependencies...'.format(v['dependency_mfd_name'], v['version']))
                mci = os.system('mvn midas:mapforce-env')
                print(mci)
                os.chdir(wd)
                if mci == 0:
                    if os.path.exists(dependency_path2):
                        # ALREADY PULLED
                        for dep_file in os.listdir(dependency_path2):
                            if dep_file == v['dependency_mfd_name'] + '-' + v['version'] + '.mfd':
                                dep = '{}\\{}'.format(dependency_path2, dep_file)
                                tree = ET.parse(dep)
                                _dep_root = tree.getroot()
                                _dep_tree_dict[_dep_root] = v['dependency_mfd_name'] + "-" + version
                else:
                    print("COULD NOT COMPLETE mvn midas:mapforce-env command on {}\nTry to run the mvn clean install command on the master branch manually and see what went wrong".format(os.getcwd()))
                    r = raw_input("Hit enter to continue...")
                    quit()

    return _dep_tree_dict


def getDependencies(_dep_tree_dict):
    global lines
    _dep_record = {}
    for dep_root, dep_name in _dep_tree_dict.items():
        parent_map = {c: p for p in dep_root.iter() for c in p}
        for sources in dep_root.findall(".//*[@name='getKeyedValue']/sources"):
            x = parent_map[parent_map[parent_map[parent_map[sources]]]]
            source_key = sources[0].attrib['key']
            command = ".//*[@vertexkey='" + source_key + "']"
            for item in dep_root.findall(command):
                if parent_map[parent_map[item]].tag == 'vertex':
                    y = parent_map[parent_map[parent_map[parent_map[parent_map[parent_map[item]]]]]]
                    if y.tag == 'component':
                        vertex = parent_map[parent_map[item]]
                        if vertex.tag == 'vertex':
                            for component in dep_root.findall(".//*[@name='constant']"):
                                if (
                                        'key' in component[1][0].attrib
                                        and 'vertexkey' in vertex.attrib
                                        and component[1][0].attrib['key'] == vertex.attrib['vertexkey']
                                        and x.attrib['name'] == y.attrib['name']
                                        and 'value' in component[-1][0].attrib
                                ):
                                    for dep_component in dep_root.findall('./'):
                                        function_name = parent_map[parent_map[parent_map[component]]].attrib['name']
                                        library_name = parent_map[parent_map[parent_map[component]]].attrib['library']
                                        if (
                                                'name' in dep_component.attrib
                                                and x.attrib['name'] == dep_component.attrib['name']
                                                and x.attrib['library'] == dep_component.attrib['library']
                                                and function_name == x.attrib['name']
                                                and library_name == x.attrib['library']
                                        ):
                                            _dep_name = dep_name
                                            dep_name += ' : {}'.format(x.attrib['library'])
                                            if dep_name not in _dep_record.keys():
                                                _dep_record[dep_name] = {}
                                            if x.attrib['name'] not in _dep_record[dep_name].keys():
                                                _dep_record[dep_name][x.attrib['name']] = []
                                            _dep_record[dep_name][x.attrib['name']].append(component[-1][0].attrib['value'])
                                            dep_name = _dep_name
    return _dep_record


def getOverrides(_local_root, _file, _dependency_dictionary=''):
    global parent_map
    dep_count = 0
    override_count = 0
    parent_map = {c: p for p in _local_root.iter() for c in p}
    for sources in _local_root.findall(".//*[@name='getKeyedValue']/sources"):
        top_function = parent_map[parent_map[parent_map[parent_map[sources]]]]
        source_key = sources[0].attrib['key']
        vertex_key = getVertexKey(_local_root, top_function, source_key)
        if top_function.findall(".//*[@name='constant']/targets/datapoint/[@key='{}']".format(vertex_key)):
            for datapoint in top_function.findall(".//*[@name='constant']/targets/datapoint/[@key='{}']".format(vertex_key)):
                override = parent_map[parent_map[datapoint]][-1][0].attrib['value']
                function_info = '{} : {}'.format(top_function.attrib['name'], 'local')
                override_count += 1
                if 'default' in function_info:
                    function_info = '*MAIN MAPPING* : local'
                if _file not in master.keys():
                    master[_file] = {}
                if function_info not in master[_file].keys():
                    master[_file][function_info] = []
                master[_file][function_info].append(override)
        elif top_function.findall(".//targets/datapoint/[@key='{}']".format(vertex_key)):
            for item in top_function.findall(".//targets/datapoint/[@key='{}']".format(vertex_key)):
                component_name = parent_map[parent_map[parent_map[parent_map[parent_map[item]]]]].attrib['name']
                component_library = parent_map[parent_map[parent_map[parent_map[parent_map[item]]]]].attrib['library']
                for jj in parent_map[parent_map[item]][-1]:
                    if jj.tag == 'parameter':
                        function_input_name = jj.attrib['name']
            for comp in _local_root.findall('./')[1][1][0]:
                top = parent_map[_local_root.findall('./')[1][1]]
                if 'name' in comp.attrib and 'library' in comp.attrib:
                    if comp.attrib['name'] == component_name and comp.attrib['library'] == component_library:
                        for subroot in comp[-1]:
                            for element in subroot:
                                if 'name' in element.attrib and element.attrib['name'] == function_input_name:
                                    if 'inpkey' in element.attrib:
                                        fxInputKey = element.attrib['inpkey']
                                        vertex_key = getVertexKey(_local_root, top, fxInputKey)
            if top.findall(".//*[@name='constant']/targets/datapoint/[@key='{}']".format(vertex_key)):
                for datapoint in top.findall(".//*[@name='constant']/targets/datapoint/[@key='{}']".format(vertex_key)):
                    override = parent_map[parent_map[datapoint]][-1][0].attrib['value']
                    function_info = '{} : {}'.format(top.attrib['name'], 'local')
                    override_count += 1
                    if 'default' in function_info:
                        function_info = '*MAIN MAPPING* : local'
                    if _file not in master.keys():
                        master[_file] = {}
                    if function_info not in master[_file].keys():
                        master[_file][function_info] = []
                    master[_file][function_info].append(override)
            else:
                for fx in _local_root.findall('./'):
                    if fx.tag == 'component':
                        for subchildren in fx[-1][0]:
                            if 'name' in subchildren.attrib and 'library' in subchildren.attrib and subchildren.attrib['name'] == component_name and subchildren.attrib['library'] == component_library:
                                for rooter in subchildren[-1]:
                                    for entries in rooter:
                                        if entries.tag == 'entry' and 'inpkey' in entries.attrib and 'name' in entries.attrib and entries.attrib['name'] == function_input_name:
                                            vertex_key = getVertexKey(_local_root,fx,entries.attrib['inpkey'])
                                            if fx.findall(".//*[@name='constant']/targets/datapoint/[@key='{}']".format(vertex_key)):
                                                for datapoint in fx.findall(".//*[@name='constant']/targets/datapoint/[@key='{}']".format(vertex_key)):
                                                    override = parent_map[parent_map[datapoint]][-1][0].attrib['value']
                                                    function_info = '{} : {}'.format(fx.attrib['name'], 'local')
                                                    override_count += 1
                                                    if 'default' in function_info:
                                                        function_info = '*MAIN MAPPING* : local'
                                                    if _file not in master.keys():
                                                        master[_file] = {}
                                                    if function_info not in master[_file].keys():
                                                        master[_file][function_info] = []
                                                    master[_file][function_info].append(override)

    if _dependency_dictionary:
        for x in _local_root.findall('.'):
            for local_function in x[1][-1][0]:
                for split, v in _dependency_dictionary.items():
                    dep_name = split.split(' : ')[0]
                    dep_library = split.split(' : ')[-1]
                    for dep_function_name, override_list in v.items():
                        for dep_override in override_list:
                            if local_function.attrib['name'] == dep_function_name and local_function.attrib['library'] == dep_library:
                                dep_count += 1
                                override_count += 1
                                function_info = '{} : {}'.format(dep_function_name, dep_name)
                                if _file not in master.keys():
                                    master[_file] = {}
                                if function_info not in master[_file].keys():
                                    master[_file][function_info] = []
                                master[_file][function_info].append(dep_override)
    function_frequency = 0
    f_freq = {}
    for item in _local_root.findall(".//*[@name='getKeyedValue']/sources"):
        f_freq[parent_map[parent_map[parent_map[parent_map[item]]]].attrib['name']] = 0
        for row in _local_root[1][-1][0]:
            if 'name' in row.attrib and 'library' in row.attrib:
                if row.attrib['name'] == parent_map[parent_map[parent_map[parent_map[item]]]].attrib['name'] and row.attrib['library'] == parent_map[parent_map[parent_map[parent_map[item]]]].attrib['library']:
                    function_frequency += 1
                    f_freq[parent_map[parent_map[parent_map[parent_map[item]]]].attrib['name']] = function_frequency

    local_count = 0
    info = ''
    if len(f_freq.keys()) == 1 and 'defaultmap' in f_freq.keys()[0]:
        local_count = len(_local_root.findall(".//*[@name='getKeyedValue']/sources"))

    else:
        # ADJUST OVERRIDE FREQUENCY
        for k,v in f_freq.items():
            if 'defaultmap' not in k and v == 0:
                f_freq[k] = 1

        for k,v in f_freq.items():
            if v > 1:
                info += '\t{} function contains getKeyedValue, and is called {} times in mapping\n'.format(k,v)
            local_count += v
    print('\t\t\tDEPENDENCY COUNT {} + LOCAL COUNT {} = OVERRIDE COUNT: {}'.format(dep_count, local_count, override_count))
    #
    # # Create output
    if override_count != dep_count + local_count:
        print('\t\t\t\t[WARN] OVERRIDES STILL EXIST IN MAPPING NOT LISTED HERE')
        if _file not in master.keys():
            master[_file] = {}
        if 'OVERRIDES STILL EXIST IN MAPPING NOT LISTED HERE' not in master[_file].keys():
            if info != '':
                master[_file]['!!! OVERRIDES STILL EXIST IN MAPPING NOT LISTED HERE !!!\n' + info] = []
            else:
                master[_file]['!!! OVERRIDES STILL EXIST IN MAPPING NOT LISTED HERE !!!'] = []
    elif dep_count == 0 and local_count == 0 and override_count == 0:
        print('\t\t\t\t[RESULTS] NO MATCHING OVERRIDES DETECTED')
        if _file not in master.keys():
            master[_file] = {}
        if 'NO MATCHING OVERRIDES DETECTED' not in master[_file].keys():
            master[_file]['NO MAPPING OVERRIDES DETECTED'] = []
    else:
        print('\t\t\t\t[RESULTS] FOUND OVERRIDES!')


print("Grabbing overrides...")
for walk_path, walk_dir, walk_file in os.walk(".", topdown=False):
    if 'pom.xml' in ' '.join(str(x) for x in walk_file) and '.mfd' in ' '.join(str(x) for x in walk_file):
        # POM AND MFD IN DIRECTORY
        print('\n[INFO] DEPENDENCY CHECK NEEDED FOR {}'.format(walk_path.split('\\')[-1]))
        for file in walk_file:
            if file == 'pom.xml':
                for file2 in walk_file:
                    if '.mfd' in file2:
                        dependencyTree = getDependencyTree('{}\\{}\\{}'.format(os.getcwd(), walk_path[2:], file))
                        root = ET.parse('{}\\{}\\{}'.format(os.getcwd(), walk_path[2:], file2)).getroot()
                        if dependencyTree:
                            dependency = getDependencies(dependencyTree)
                            if dependency != {}:
                                for k in dependency.keys():
                                    if k.split(':')[0].strip() != 'local':
                                        print('\t\tGetting overrides from {}'.format(k))
                                        getOverrides(root, file2, dependency)
                            else:
                                getOverrides(root, file2)
                        else:
                            # HAS POM BUT NO DEPENDENCIES
                            print('\t\tGetting overrides from {}'.format(file2))
                            getOverrides(root, file2)

    elif 'pom.xml' not in ' '.join(str(x) for x in walk_file) and '.mfd' in ' '.join(str(x) for x in walk_file):
        # ONLY MFD IN DIRECTORY
        print('[INFO] NO DEPENDENCY PULL NEEDED FOR {}'.format(walk_path.split('\\')[-1]))
        for file in walk_file:
            if '.mfd' in file:
                local_root = ET.parse('{}\\{}\\{}'.format(os.getcwd(), walk_path[2:], file)).getroot()
                getOverrides(local_root, file)

# Write output
with open("override_results.txt", 'w') as outputfile:
    if file != "":
        outputfile.writelines(PrettyPrint(master))
    else:
        outputfile.write("NO MFD FOUND IN DIRECTORY")

print("SUCCESS!")
# Start file
os.startfile("override_results.txt")
