import networkx as nx
import copy

class Noleafgraph:

	def __init__(self, rwgraph):
		self.rwgraph = rwgraph
		self.noleafgraph = copy.deepcopy(self.rwgraph)
		self.node_leaf = {}

	def getNoleafgraph(self):
		flag = 1
		while flag != 0:
			flag = 0
			nodes = self.noleafgraph.nodes()
			l = list(nodes)
			for node_id in l:
				if self.rwgraph.nodes()[node_id]['data_node'].__class__.__name__ != 'ProcessNode':
					neighbors = list(set(nx.all_neighbors(self.noleafgraph, node_id)))
					if len(neighbors) == 1:
						if self.node_leaf.has_key(neighbors[0]):
							if self.rwgraph.nodes()[node_id]['data_node'].__class__.__name__ != 'ProcessNode':
								self.node_leaf[neighbors[0]].append(node_id)
						else:
							if self.rwgraph.nodes()[node_id]['data_node'].__class__.__name__ != 'ProcessNode':
								self.node_leaf[neighbors[0]] = [node_id]
						self.noleafgraph.remove_node(node_id)
						flag = 1
		leaf_node_num_total, leaf_edge_num_total = self.write_node_leaf('./core/intermediatefiles/leaf.txt')

		return self.noleafgraph, leaf_node_num_total, leaf_edge_num_total

	def write_node_leaf(self,path):
		fw = open(path,'w')
		edges = self.rwgraph.edges()
		leaf_node_num_total = 0
		leaf_edge_num_total = 0
		for node_id in self.node_leaf:
			leaf_node_num_total += len(self.node_leaf[node_id])
			leaf_edge_num = 0
			for edge in edges:
				if ((edge[0] == node_id) and (edge[1] in self.node_leaf[node_id])) or ((edge[1] == node_id) and (edge[0] in self.node_leaf[node_id])):
					leaf_edge_num += 1
			leaf_edge_num_total += leaf_edge_num

			node_instance = self.rwgraph.nodes()[node_id]['data_node']
			fw.write(node_id+','+node_instance.unidname+',')
			for i in self.node_leaf[node_id]:
				#fw.write(i+','+self.rwgraph.nodes()[i]['data_node'].unidname+',')
				fw.write(i+',')
			fw.write(str(len(self.node_leaf[node_id]))+','+str(leaf_edge_num))

			fw.write('\n')
		return leaf_node_num_total, leaf_edge_num_total

