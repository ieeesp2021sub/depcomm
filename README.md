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
1. Log file. The log file need to be put in the folder input of depcomm_python
2. Parameters including log file name and POI. They should be written to run.py in depcomm_python
### Command
python ~/core/Start.py 

### Data
Due to the limit of Github, we can't upload the extreme large log file.
The folder input in the code has contained a small log for demo.
For the DARPA Attack used in evaluation, here is the [github link](https://github.com/darpa-i2o/Transparent-Computing). 
You can follow their instructions to download data.  
### Output
DepComm will output three different files in the folder output.
1. The community graph generated by community detection of DepComm
2. The community graph compressed by the community compression module
3. A file contains the prioritized InfoPaths
