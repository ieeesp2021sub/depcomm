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
1. Log file. The log file needs to be put in the folder ``input`` in the project home directory ``depcomm_python``
2. Parameters including log file name and POI. They should be written to ``run.py`` in the project home directory ``depcomm_python``
### Command
After configuring the input, directly execute the following command from the project home directory:<br/>
	``python run.py`` 

### Data
We adopt Sysdig to collect the system logs. This link shows how to install Sysdig: https://sysdig.com/opensource/sysdig/install/.   
We use the following command to collect logs:<br/>
``sudo sysdig -p"%evt.num %evt.rawtime.s.%evt.rawtime.ns %evt.cpu %proc.name (%proc.pid) %evt.dir %evt.type cwd=%proc.cwd %evt.args latency=%evt.latency" evt.type!=switch > fileName.txt``  
Due to the limit of Github, we can't upload the collected extreme large log files.
The folder example contains a small log and parameter file that can be used for demo.
For this case, the POI event is a suspicious network connection.
For the DARPA Attack used in evaluation, here is the [github link](https://github.com/darpa-i2o/Transparent-Computing). 
You can follow their instructions to download data.  
### Output
DepComm will output several different files in the folder ``output`` in the project home directory ``depcomm_python``.
1. Some dot files that be named as ``community_\*.dot``. They are the graphs for each community. 
2. A dot file that be named as ``summary_graph.dot``. It is the summary graph, where the node denotes community and the edge denotes the data flow direction among communities.
3. A txt file that be named as ``summary.txt``. It contains the master process, time span and prioritized InfoPaths for each community.
4. Another txt file. It records nodes attributes for each community (pid and pidname for process node, path and filename for file node, IP and Port for network node).
