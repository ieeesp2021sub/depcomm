import sys
sys.path.append("..")
import networkx as nx

def process2file(graph,path):
	fw = open(path,'w')
	nodes = graph.nodes()
	for nid in nodes:
		if nodes[nid]['data_node'].__class__.__name__ == 'ProcessNode':
			neighbors = sorted(set(nx.all_neighbors(graph, nid)))
			nbrs = []
			for nbr in neighbors:
				if nodes[nbr]['data_node'].__class__.__name__ != 'ProcessNode':
					nbrs.append(nbr)
			if nbrs:
				nbrs_str = ','.join(nbrs)
				fw.write(nid+','+nbrs_str)
				fw.write('\n')
	fw.close()


