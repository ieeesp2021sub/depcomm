import igraph as ig
import networkx as nx

def nx2ig(g, directed=None):
	if directed is None:
		directed = g.is_directed()

	gi = ig.Graph(directed=directed)

	if type(list(g.nodes)[0]) is str:
		gi.add_vertices([n for n in g.nodes()])
		gi.add_edges([(u, v) for (u, v) in g.edges()])

	else:
		if set(range(len(g.nodes)))==set(g.nodes()):
			gi.add_vertices(len(g.nodes))
			gi.add_edges([(u, v) for (u, v) in g.edges()])
			gi.vs["name"]=["\\"+str(n) for n in g.nodes()]
		else:
			gi.add_vertices(["\\"+str(n) for n in g.nodes()])
			gi.add_edges([("\\"+str(u), "\\"+str(v)) for (u, v) in g.edges()])

	edgelist = nx.to_pandas_edgelist(g)
	for attr in edgelist.columns[2:]:
		gi.es[attr] = edgelist[attr]

	return gi
	

