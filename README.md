# depcomm
## Introduction
![Workflow of DepComm](https://github.com/ieeesp2021sub/depcomm/blob/main/DepComm%20overview.png)
Causality analysis on system auditing data has emerged as an important solution for attack investigation.
Given a POI (Point-Of-Interest) event (e.g. an alert fired on a  suspicious file creation), causality analysis constructs a dependency graph, in which nodes represent system entities (e.g. processes and files) and edges represent dependencies among entities, to reveal the attack sequence.
However, causality analysis often produce a huge graph.
we propose DEPCOMM, a graph summarization approach that generates a summary graph from a dependency graph by partitioning a large graph into process-centric communities and presenting summaries for each community. Specifically, each community contains a set of
intimate processes that cooperate with each other to accomplish
certain system activities (e.g., file compression), and the resources
(e.g., files) accessed by these processes. To further reduce the
community size, DEPCOMM identifies repetitive events inside
each community and perform compression on both the nodes
and the edges. Finally, for each community, DEPCOMM identifies
InfoPaths that represent information flows from the inputs of the
community to the outputs of the community, and priorities these
InfoPaths to rank the InfoPaths that are more likely to represent
attack-related information flows at the top.

## Requirements
Python Version：2.7  

Dependent packages:  
> networkx==2.2  
> numpy==1.15.1  
> scipy==1.0  
> pydot==1.4.1  
> python-louvain==0.14  
> igraph==0.7  
> pydot==1.4.1  
> gensim==3.8.1  
> pympler==0.7  
> scikit-fuzzy==0.4.2  
> sklearn==0.19.1  

## Usage
### Input
1. Log file path.
2. POI.
### Command
Execute the following command from the project home directory ``DEPCOMM``:<br/>

	./core/Start "log-file-path" "poi" 

For example, to run depcomm on the unzipped example log file, first put the unzipped example log file into the folder ``input`` in the project home directory ``DEPCOMM``, then execute the following command:

    ./core/Start "./input/leak_data.txt" "10.10.103.10:38772->159.226.251.11:25"

### Data

Due to the limit of Github, we can't upload the collected extreme large log files.
The folder example contains a small log that can be used for demo.
For this case, the POI event is a suspicious network connection.
For the DARPA Attack used in evaluation, here is the [github link](https://github.com/darpa-i2o/Transparent-Computing). 
You can follow their instructions to download data.  
### Output
DepComm will output several different files to the folder ``output`` in the project home directory ``DEPCOMM``.
1. Some dot files that are named as ``community_*.dot``. They are the graphs for each community. 
2. A dot file that is named as ``summary_graph.dot``. It is the summary graph, where the node denotes community and the edge denotes the data flow direction among communities.
3. A txt file that is named as ``summary.txt``. It contains the master process, time span and prioritized InfoPaths for each community.
4. Another txt file that is named as ``community.txt``. It records nodes attributes for each community (pid and pidname for process node, path and filename for file node, IP and Port for network node).  

Note that the dot files can be visualized by [Graphviz](https://github.com/xflr6/graphviz).
