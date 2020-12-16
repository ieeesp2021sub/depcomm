import networkx as nx
import numpy as np
from utils.Multigraph2graph import Multigraph2graph
from utils.ExportResult import ExportResult

class Linepartition:

	def __init__(self,graph, is_weight):
		self.graph = Multigraph2graph(graph)
		self.is_weight = is_weight

	def linepar(self, filename, meth, issplit, ismergepath):

		edges, line_nodes, line_edges_one, line_edges_weight = self.linegraph(self.graph)
		
		if self.is_weight:
			lov = Louvain(line_nodes, line_edges_weight)
			line_coms,_ = lov.apply_method()
		else:
			lov = Louvain(line_nodes, line_edges_one)
			line_coms,_ = lov.apply_method()

		coms = []
		for line_com in line_coms:
			com = set()
			for i in line_com:
				com.add(edges[i][0])
				com.add(edges[i][1])
			coms.append(list(com))

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

	def linegraph(self,graph):
		edges = list(graph.edges())
		edge_one = []
		edge_weight = []
		edge_tmp = []
		for x, edge_x in enumerate(edges):
			for y, edge_y in enumerate(edges):
				share_node = set(edge_x).intersection(set(edge_y))
				if len(share_node) == 1:
					if ((x,y) in edge_tmp) or ((y,x) in edge_tmp):
						continue
					else:
						edge_one.append(((x,y),1))
						edge_weight.append(((x,y),1.0/(graph.degree(list(share_node)[0])-1)))
						edge_tmp.append((x,y))
			
		return edges, range(len(edges)), edge_one, edge_weight

class Louvain:

	def __init__(self, nodes, edges):
		self.nodes = nodes
		self.edges = edges

		self.m = 0
		self.k_i = [0 for n in nodes]
		self.edges_of_node = {}
		self.w = [0 for n in nodes]
		for e in edges:
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

		self.communities = [n for n in nodes]
		self.actual_partition = []

	def apply_method(self):
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
		return (self.actual_partition, best_q)
	
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
	

				
