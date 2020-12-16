import networkx as nx
from copy import copy
from collections import defaultdict
from heapq import heappush, heappop
from itertools import combinations, chain
from collections import defaultdict
from utils.Multigraph2graph import Multigraph2graph
from utils.ExportResult import ExportResult

class HLC:
	@staticmethod
	def get_sorted_pair(a, b):
		return tuple(sorted([a, b]))

	@staticmethod
	def HLC_read_edge_list_unweighted(g):
		adj_list_dict = defaultdict(set)
		edges = set()
		for e  in g.edges():
			ni, nj = e[0], e[1]
			edges.add(HLC.get_sorted_pair(ni, nj))
			adj_list_dict[ni].add(nj)
			adj_list_dict[nj].add(ni)
		return dict(adj_list_dict), edges

	@staticmethod
	def HLC_read_edge_list_weighted(g):
		adj = defaultdict(set)
		edges = set()
		ij2wij = {}
		for e in g.edges(data=True):
			ni, nj, wij = e[0], e[1], e[2]['weight']
			if ni != nj:
				ni, nj = HLC.get_sorted_pair(ni, nj)
				edges.add((ni, nj))
				ij2wij[ni, nj] = wij
				adj[ni].add(nj)
				adj[nj].add(ni)
		return dict(adj), edges, ij2wij

	@staticmethod
	def sort_edge_pairs_by_similarity(adj_list_dict):
		def cal_jaccard(left_set, right_set):
			return 1.0 * len(left_set & right_set) / len(left_set | right_set)

		inc_adj_list_dict = dict((n, adj_list_dict[n] | {n}) for n in adj_list_dict)
		min_heap = []
		for vertex in adj_list_dict:
			if len(adj_list_dict[vertex]) > 1:
				for i, j in combinations(adj_list_dict[vertex], 2):
					edge_pair = HLC.get_sorted_pair(HLC.get_sorted_pair(i, vertex), HLC.get_sorted_pair(j, vertex))
					similarity_ratio = cal_jaccard(inc_adj_list_dict[i], inc_adj_list_dict[j])
					heappush(min_heap, (1 - similarity_ratio, edge_pair))
		return [heappop(min_heap) for _ in range(len(min_heap))]

	@staticmethod
	def sort_edge_pairs_by_similarity_weighted(adj_list_dict, edge_weight_dict):
		inc_adj_list_dict = dict((n, adj_list_dict[n] | {n}) for n in adj_list_dict)

		def cal_jaccard(intersect_val, left_val, right_val):
			return intersect_val / (left_val + right_val - intersect_val)

		Aij = copy(edge_weight_dict)
		n2a_sqrd = {}
		for vertex in adj_list_dict:
			Aij[vertex, vertex] = float(
					sum(edge_weight_dict[HLC.get_sorted_pair(vertex, i)] for i in adj_list_dict[vertex]))
			Aij[vertex, vertex] /= len(adj_list_dict[vertex])
			n2a_sqrd[vertex] = sum(Aij[HLC.get_sorted_pair(vertex, i)] ** 2
					for i in inc_adj_list_dict[vertex])

		min_heap = []
		for vertex in adj_list_dict:
			if len(adj_list_dict[vertex]) > 1:
				for i, j in combinations(adj_list_dict[vertex], 2):
					edge_pair = HLC.get_sorted_pair(HLC.get_sorted_pair(i, vertex), HLC.get_sorted_pair(j, vertex))
					ai_dot_aj = float(sum(Aij[HLC.get_sorted_pair(i, x)] * Aij[HLC.get_sorted_pair(j, x)] for x in
						inc_adj_list_dict[i] & inc_adj_list_dict[j]))
					similarity_ratio = cal_jaccard(ai_dot_aj, n2a_sqrd[i], n2a_sqrd[j])
					heappush(min_heap, (1 - similarity_ratio, edge_pair))
		return [heappop(min_heap) for _ in range(len(min_heap))]


	def __init__(self,graph):
		self.graph = Multigraph2graph(graph)
		adj, edges = HLC.HLC_read_edge_list_unweighted(self.graph)
		self.adj_list_dict = adj
		self.edges = edges
		self.density_factor = 2.0 / len(edges)

		self.edge2cid = {}
		self.cid2nodes, self.cid2edges = {}, {}
		self.orig_cid2edge = {}
		self.curr_max_cid = 0
		self.linkage = []

		def initialize_edges():
			for cid, edge in enumerate(self.edges):
				edge = HLC.get_sorted_pair(*edge)
				self.edge2cid[edge] = cid
				self.cid2edges[cid] = {edge}
				self.orig_cid2edge[cid] = edge
				self.cid2nodes[cid] = set(edge)
			self.curr_max_cid = len(self.edges) - 1

		initialize_edges()

		self.D = 0.0
		self.list_D = [(1.0, 0.0)]
		self.best_D = 0.0
		self.best_S = 1.0
		self.best_P = None

	def hlc(self, threshold, w, dendro_flag, filename, meth, issplit, ismergepath):
		def merge_comms(edge1, edge2, S):
			def cal_density(edge_num, vertex_num):
				return edge_num * (edge_num - vertex_num + 1.0) / (
						(vertex_num - 2.0) * (vertex_num - 1.0)) if vertex_num > 2 else 0.0

			if not edge1 or not edge2:
				return
			cid1, cid2 = self.edge2cid[edge1], self.edge2cid[edge2]
			if cid1 == cid2:
				return
			m1, m2 = len(self.cid2edges[cid1]), len(self.cid2edges[cid2])
			n1, n2 = len(self.cid2nodes[cid1]), len(self.cid2nodes[cid2])
			Dc1, Dc2 = cal_density(m1, n1), cal_density(m2, n2)
			if m2 > m1:
				cid1, cid2 = cid2, cid1

			if dendro_flag:
				self.curr_max_cid += 1
				newcid = self.curr_max_cid
				self.cid2edges[newcid] = self.cid2edges[cid1] | self.cid2edges[cid2]
				self.cid2nodes[newcid] = set()
				for e in chain(self.cid2edges[cid1], self.cid2edges[cid2]):
					self.cid2nodes[newcid] |= set(e)
					self.edge2cid[e] = newcid
				del self.cid2edges[cid1], self.cid2nodes[cid1]
				del self.cid2edges[cid2], self.cid2nodes[cid2]
				m, n = len(self.cid2edges[newcid]), len(self.cid2nodes[newcid])
				self.linkage.append((cid1, cid2, S))
			else:
				self.cid2edges[cid1] |= self.cid2edges[cid2]
				for e in self.cid2edges[cid2]:
					self.cid2nodes[cid1] |= set(e)
					self.edge2cid[e] = cid1
				del self.cid2edges[cid2], self.cid2nodes[cid2]
				m, n = len(self.cid2edges[cid1]), len(self.cid2nodes[cid1])
			Dc12 = cal_density(m, n)
			self.D += (Dc12 - Dc1 - Dc2) * self.density_factor

		if w is None:
			sorted_edge_list = HLC.sort_edge_pairs_by_similarity(self.adj_list_dict)
		else:
			sorted_edge_list = HLC.sort_edge_pairs_by_similarity_weighted(self.adj_list_dict, w)

		prev_similarity = -1
		for oms, eij_eik in chain(sorted_edge_list, [(1.0, (None, None))]):
			cur_similarity = 1 - oms
			if threshold and cur_similarity < threshold:
				break
			if cur_similarity != prev_similarity:
				if self.D >= self.best_D:
					self.best_D = self.D
					self.best_S = cur_similarity
					self.best_P = copy(self.edge2cid)
				self.list_D.append((cur_similarity, self.D))
				prev_similarity = cur_similarity
			merge_comms(eij_eik[0], eij_eik[1], cur_similarity)

		self.best_P
		coms_edge = defaultdict(list)
		for e, com in self.best_P.items():
			coms_edge[com].append(e)

		coms_edge = [list(c) for c in coms_edge.values()]
		coms = []
		for c in coms_edge:
			c_set = set()
			for i in c:
				c_set.add(i[0])
				c_set.add(i[1])
			coms.append(list(c_set))
		print coms

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
		print a
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
		
		

