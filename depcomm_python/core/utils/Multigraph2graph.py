import networkx as nx
import copy


def Multigraph2graph(graph):
	graph = graph.to_undirected()
	newgraph = nx.Graph()
	nodes = graph.nodes()
	for node in nodes:
		newgraph.add_node(node, data_node=nodes[node]['data_node'])
	for u,v in graph.edges():
		if not newgraph.has_edge(u,v):
			newgraph.add_edge(u, v, data_edge=graph[u][v][0]['data_edge'])

	#print newgraph.edges()

	return newgraph

