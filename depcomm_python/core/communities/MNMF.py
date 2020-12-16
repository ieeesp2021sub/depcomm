import numpy as np
import networkx as nx
from collections import defaultdict
from scipy.sparse import coo_matrix
from utils.ExportResult import ExportResult
from utils.Multigraph2graph import Multigraph2graph

class MNMF:

	def __init__(self, dimensions=128, clusters=10, lambd=0.2, alpha=0.05, beta=0.05, iterations=200, lower_control=10**-15, eta=5.0):
		self.dimensions = dimensions
		self.clusters = clusters
		self.lambd = lambd
		self.alpha = alpha
		self.beta = beta
		self.iterations = iterations
		self.lower_control = lower_control
		self.eta = eta

	def _modularity_generator(self):
		degs = nx.degree(self._graph)
		e_count = self._graph.number_of_edges()
		n_count = self._graph.number_of_nodes()
		modularity_mat_shape = (n_count, n_count)
		indices_1 = np.array([self.nodelist.index(edge[0]) for edge in self._graph.edges()] + [self.nodelist.index(edge[1]) for edge in self._graph.edges()])
		indices_2 = np.array([self.nodelist.index(edge[1]) for edge in self._graph.edges()] + [self.nodelist.index(edge[0]) for edge in self._graph.edges()])
		scores = [1.0-(float(degs[e[0]]*degs[e[1]])/(2*e_count)) for e in self._graph.edges()]
		scores = scores + [1.0-(float(degs[e[1]]*degs[e[0]])/(2*e_count)) for e in self._graph.edges()]
		mod_matrix = coo_matrix((scores, (indices_1, indices_2)), shape=modularity_mat_shape)
		return mod_matrix

	def _setup_matrices(self):
		self.nodelist=list(self._graph.nodes())
		self._number_of_nodes = nx.number_of_nodes(self._graph)
		self._M = np.random.uniform(0, 1, (self._number_of_nodes, self.dimensions))
		self._U = np.random.uniform(0, 1, (self._number_of_nodes, self.dimensions))
		self._H = np.random.uniform(0, 1, (self._number_of_nodes, self.clusters))
		self._C = np.random.uniform(0, 1, (self.clusters, self.dimensions))
		self._B1 = nx.adjacency_matrix(self._graph, nodelist=self.nodelist)
		self._B2 = self._modularity_generator()
		self._X = np.transpose(self._U)
		overlaps = self._B1.dot(self._B1)
		self._S = self._B1 + self.eta*self._B1*(overlaps)

	def _update_M(self):
		enum = self._S.dot(self._U)
		denom = np.dot(self._M, np.dot(np.transpose(self._U), self._U))
		denom[denom < self.lower_control] = self.lower_control
		self._M = np.multiply(self._M, enum/denom)
		row_sums = self._M.sum(axis=1)
		self._M = self._M / row_sums[:, np.newaxis]

	def _update_U(self):
		enum = self._S.dot(self._M)+self.alpha*np.dot(self._H, self._C)
		denom = np.dot(self._U, np.dot(np.transpose(self._M), self._M)+self.alpha*np.dot(np.transpose(self._C), self._C))
		denom[denom < self.lower_control] = self.lower_control
		self._U = np.multiply(self._U, enum/denom)
		row_sums = self._U.sum(axis=1)
		self._U = self._U / row_sums[:, np.newaxis]

	def _update_C(self):
		enum = np.dot(np.transpose(self._H), self._U)
		denom = np.dot(self._C, np.dot(np.transpose(self._U), self._U))
		denom[denom < self.lower_control] = self.lower_control
		frac = enum/denom
		self._C = np.multiply(self._C, frac)
		row_sums = self._C.sum(axis=1)
		self._C = self._C / row_sums[:, np.newaxis]

	def _update_H(self):
		B1H = self._B1.dot(self._H)
		B2H = self._B2.dot(self._H)
		HHH = np.dot(self._H, (np.dot(np.transpose(self._H), self._H)))
		UC = np.dot(self._U, np.transpose(self._C))
		rooted = np.square(2*self.beta*B2H)+np.multiply(16*self.lambd*HHH, (2*self.beta*B1H+2*self.alpha*UC+(4*self.lambd-2*self.alpha)*self._H))
		rooted[rooted < 0] = 0
		sqroot_1 = np.sqrt(rooted)
		enum = -2*self.beta*B2H+sqroot_1
		denom = 8*self.lambd*HHH
		denom[denom < self.lower_control] = self.lower_control
		rooted = enum/denom
		rooted[rooted < 0] = 0
		sqroot_2 = np.sqrt(rooted)
		self._H = np.multiply(self._H, sqroot_2)
		row_sums = self._H.sum(axis=1)
		self._H = self._H / row_sums[:, np.newaxis]

	def get_memberships(self, filename, meth, issplit, ismergepath):
		indices = np.argmax(self._H, axis=1)
		memberships = {i: membership for i, membership in enumerate(indices)}

		coms_to_node = defaultdict(list)
		for n, c in memberships.items():
			coms_to_node[c].append(self.nodelist[int(n)])
		coms = [list(c) for c in coms_to_node.values()]

		nodes = self._graph.nodes()
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

		ExportResult.exportaffiliation(self._graph, z, filename, meth, issplit, ismergepath)

	def get_embedding(self):
		embedding = self._U
		return embedding

	def get_cluster_centers(self):
		centers = self._C
		return centers

	def fit(self, graph):
		self._graph = Multigraph2graph(graph)
		self._setup_matrices()
		for _ in range(self.iterations):
			self._update_M()
			self._update_U()
			self._update_C()
			self._update_H()


