import community
import networkx as nx
from collections import defaultdict
from utils.Multigraph2graph import Multigraph2graph
from utils.ExportResult import ExportResult

class EgoNetSplitter:
	
	def __init__(self, resolution=1.0):
		self.resolution = resolution

	def _create_egonet(self, node):
		ego_net_minus_ego = self.graph.subgraph(self.graph.neighbors(node))
		components = {i: n for i, n in enumerate(nx.connected_components(ego_net_minus_ego))}
		new_mapping = {}
		personalities = []
		for k, v in components.items():
			personalities.append(self.index)
			for other_node in v:
				new_mapping[other_node] = self.index
			self.index = self.index+1
		self.components[node] = new_mapping
		self.personalities[node] = personalities

	def _create_egonets(self):
		self.components = {}
		self.personalities = {}
		self.index = 0
		for node in self.graph.nodes():
			self._create_egonet(node)

	def _map_personalities(self):
		self.personality_map = {p: n for n in self.graph.nodes() for p in self.personalities[n]}

	def _get_new_edge_ids(self, edge):
		return (self.components[edge[0]][edge[1]], self.components[edge[1]][edge[0]])

	def _create_persona_graph(self):
		self.persona_graph_edges = [self._get_new_edge_ids(edge) for edge in self.graph.edges()]
		self.persona_graph = nx.from_edgelist(self.persona_graph_edges)

	def _create_partitions(self):
		self.partitions = community.best_partition(self.persona_graph, resolution=self.resolution)
		self.overlapping_partitions = {node: [] for node in self.graph.nodes()}
		for node, membership in self.partitions.items():
			self.overlapping_partitions[self.personality_map[node]].append(membership)

	def fit(self, graph):
		self.graph = self.graph = Multigraph2graph(graph)
		self._create_egonets()
		self._map_personalities()
		self._create_persona_graph()
		self._create_partitions()

	def get_memberships(self, filename, meth, issplit, ismergepath):
		coms_to_node = defaultdict(list)
		for n, cs in self.overlapping_partitions.items():
			for c in cs:
				coms_to_node[c].append(n)

		coms = [list(c) for c in coms_to_node.values()]

		nodes = self.graph.nodes()
		found = []
		a = []
		for x in coms:
			b = []
			for node in list(x):
				found.append(node)
				b.append(node)
			a.append(b)

		unfound = []
		for node in nodes:
			if node in found:
				continue
			else:
				unfound.append(node)
		if unfound:
			a.append(unfound)

		t = {}
		for index, com in enumerate(a):
			for node in com:
				if t.has_key(node):
					t[node].append(index)
				else:
					t[node] = [index]

		z = []
		for key in t:
			pr = ['0']*len(a)
			for i in t[key]:
				pr[i] = '1'
			z.append((key,pr))

		ExportResult.exportaffiliation(self.graph, z, filename, meth, issplit, ismergepath)
	
