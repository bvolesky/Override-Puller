![Tree Image](tree.png)
# Override Puller
This tool uses resersive xml tree traversal to parse out deeply intertwined "mapping overrides" across N files from Altova Mapforce and dependencies (MFD).

## Learnings:
During the development of this tool, I acquired substantial knowledge and experience. My learning journey encompassed a deep understanding of recursion and the importance of establishing a solid foundation for tree traversal. Initially, I adopted an iterative approach, but soon realized the necessity of incorporating recursion to handle complex dependencies, which spanned across numerous files and nodes.

As I successfully implemented tree traversal, I gained insights into efficiently tracking dependencies and nodes across multiple files. This process involved exploring the use of dictionary data structures for storing references and keys, as well as parsing intricate text with precision. This endeavor was undeniably challenging and time-consuming.

One of the significant challenges I encountered was the possibility of nodes sharing the same name across various files, potentially referencing different entities. To address this issue, I devised a method to generate unique IDs by combining the node ID, the file location it was in, and the node name. In moments of difficulty, I took the proactive approach of creating diagrams and meticulously tracking vertex keys and target keys across all nodes and references.

By pausing to reflect on the overall concept and breaking down the problem into manageable steps, I was able to gain a comprehensive understanding of the task at hand. This, in turn, allowed me to tackle each issue methodically and ultimately achieve successful solution.

## Usage
1. Install Python from [Python Downloads](https://www.python.org/downloads/).
2. Clone the Repository - ```git clone https://github.com/bvolesky/Override-Puller.git```
3. Navigate to the Repository - ```cd <repository_folder>/Override-Puller```
5. Run the App - ```python Override-Puller.py```
