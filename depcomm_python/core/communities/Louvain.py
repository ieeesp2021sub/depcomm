import community as louvain_modularity
import networkx as nx
from utils.ExportResult import ExportResult
from utils.Multigraph2graph import Multigraph2graph

class Louvain:

	def __init__(self,graph):
		self.graph = Multigraph2graph(graph)
		self.nodelist = list(self.graph.nodes())
		self.nodes = range(len(self.nodelist))
		edgelist = list(self.graph.edges())
		self.edges = [((self.nodelist.index(s),self.nodelist.index(v)),1) for s,v in edgelist]

		self.m = 0
		self.k_i = [0 for n in self.nodes]
		self.edges_of_node = {}
		self.w = [0 for n in self.nodes]
		for e in self.edges:
			self.m += e[1]
			self.k_i[e[0][0]] += e[1]
			self.k_i[e[0][1]] += e[1]
			if e[0][0] not in self.edges_of_node:
				self.edges_of_node[e[0][0]] = [e]
			else:
				self.edges_of_node[e[0][0]].append(e)
			if e[0][1] not in self.edges_of_node:
				self.edges_of_node[e[0][1]] = [e]
			elif e[0][0] != e[0][1]:
				self.edges_of_node[e[0][1]].append(e)
		self.communities = [n for n in self.nodes]
		self.actual_partition = []

	def apply_method(self, filename, meth, issplit, ismergepath):
		network = (self.nodes, self.edges)
		best_partition = [[node] for node in network[0]]
		best_q = -1
		i = 1
		while 1:
			i += 1
			partition = self.first_phase(network)
			q = self.compute_modularity(partition)
			partition = [c for c in partition if c]

			if self.actual_partition:
				actual = []
				for p in partition:
					part = []
					for n in p:
						part.extend(self.actual_partition[n])
					actual.append(part)
				self.actual_partition = actual
			else:
				self.actual_partition = partition
			if q == best_q:
				break
			network = self.second_phase(network, partition)
			best_partition = partition
			best_q = q

		coms = []
		for c in self.actual_partition:
			com = []
			for nodeid in c:
				com.append(self.nodelist[nodeid])
			coms.append(com)
		
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

	def compute_modularity(self, partition):
		q = 0
		m2 = self.m * 2
		for i in range(len(partition)):
			q += self.s_in[i] / m2 - (self.s_tot[i] / m2) ** 2
		return q

	def compute_modularity_gain(self, node, c, k_i_in):
		return 2 * k_i_in - self.s_tot[c] * self.k_i[node] / self.m

	def first_phase(self, network):
		best_partition = self.make_initial_partition(network)
		while 1:
			improvement = 0
			for node in network[0]:
				node_community = self.communities[node]
				best_community = node_community
				best_gain = 0
				best_partition[node_community].remove(node)
				best_shared_links = 0
				for e in self.edges_of_node[node]:
					if e[0][0] == e[0][1]:
						continue
					if e[0][0] == node and self.communities[e[0][1]] == node_community or e[0][1] == node and self.communities[e[0][0]] == node_community:
						best_shared_links += e[1]
				self.s_in[node_community] -= 2 * (best_shared_links + self.w[node])
				self.s_tot[node_community] -= self.k_i[node]
				self.communities[node] = -1
				communities = {}
				for neighbor in self.get_neighbors(node):
					community = self.communities[neighbor]
					if community in communities:
						continue
					communities[community] = 1
					shared_links = 0
					for e in self.edges_of_node[node]:
						if e[0][0] == e[0][1]:
							continue
						if e[0][0] == node and self.communities[e[0][1]] == community or e[0][1] == node and self.communities[e[0][0]] == community:
							shared_links += e[1]
					gain = self.compute_modularity_gain(node, community, shared_links)
					if gain > best_gain:
						best_community = community
						best_gain = gain                                                                                                                 
						best_shared_links = shared_links
				best_partition[best_community].append(node)
				self.communities[node] = best_community
				self.s_in[best_community] += 2 * (best_shared_links + self.w[node])
				self.s_tot[best_community] += self.k_i[node]
				if node_community != best_community:
					improvement = 1
			if not improvement:
				break
		return best_partition

	def get_neighbors(self, node):
		for e in self.edges_of_node[node]:
			if e[0][0] == e[0][1]:
				continue
			if e[0][0] == node:
				yield e[0][1]
			if e[0][1] == node:
				yield e[0][0]

	def make_initial_partition(self, network):
		partition = [[node] for node in network[0]]
		self.s_in = [0 for node in network[0]]
		self.s_tot = [self.k_i[node] for node in network[0]]
		for e in network[1]:
			if e[0][0] == e[0][1]:
				self.s_in[e[0][0]] += e[1]
				self.s_in[e[0][1]] += e[1]
		return partition

	def second_phase(self, network, partition):
		nodes_ = [i for i in range(len(partition))]
		communities_ = []
		d = {}
		i = 0
		for community in self.communities:
			if community in d:
				communities_.append(d[community])
			else:
				d[community] = i
				communities_.append(i)
				i += 1
		self.communities = communities_

		edges_ = {}
		for e in network[1]:
			ci = self.communities[e[0][0]]
			cj = self.communities[e[0][1]]
			try:
				edges_[(ci, cj)] += e[1]
			except KeyError:
				edges_[(ci, cj)] = e[1]
		edges_ = [(k, v) for k, v in edges_.items()]

		self.k_i = [0 for n in nodes_]
		self.edges_of_node = {}
		self.w = [0 for n in nodes_]
		for e in edges_:
			self.k_i[e[0][0]] += e[1]
			self.k_i[e[0][1]] += e[1]
			if e[0][0] == e[0][1]:
				self.w[e[0][0]] += e[1]
			if e[0][0] not in self.edges_of_node:
				self.edges_of_node[e[0][0]] = [e]
			else:
				self.edges_of_node[e[0][0]].append(e)
			if e[0][1] not in self.edges_of_node:
				self.edges_of_node[e[0][1]] = [e]
			elif e[0][0] != e[0][1]:
				self.edges_of_node[e[0][1]].append(e)

		self.communities = [n for n in nodes_]
		return (nodes_, edges_)



