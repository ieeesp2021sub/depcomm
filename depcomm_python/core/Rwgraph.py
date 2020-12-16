import networkx as nx
import copy

class Rwgraph:

	def __init__(self, origingraph):
		print "Removing only-read file..."
		self.rwgraph = copy.deepcopy(origingraph)

	def getRwgraph(self):
		nodes = self.rwgraph.nodes()
		l = list(nodes)
		for node_id in l:
			if nodes[node_id]['data_node'].__class__.__name__ == 'FileNode':
				if self.rwgraph.in_degree(node_id) == 0:
					self.rwgraph.remove_node(node_id)
		return self.rwgraph


