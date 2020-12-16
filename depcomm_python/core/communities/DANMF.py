import numpy as np
import networkx as nx
from collections import defaultdict
from sklearn.decomposition import NMF
from utils.Multigraph2graph import Multigraph2graph
from utils.ExportResult import ExportResult

class DANMF:

	def __init__(self, layers=[54,26,13], pre_iterations=20, iterations=400, seed=42, lamb=0.2):
		self.layers = layers
		self.pre_iterations = pre_iterations
		self.iterations = iterations
		self.seed = seed
		self.lamb = lamb
		self._p = len(self.layers)

	def _setup_target_matrices(self, graph):
		self._graph = graph
		self.nodelist = list(self._graph.nodes())
		self._A = nx.adjacency_matrix(self._graph, nodelist=self.nodelist)
		self._L = nx.laplacian_matrix(self._graph, nodelist=self.nodelist)
		self._D = self._L+self._A

	def _setup_z(self, i):
		if i == 0:
			self._Z = self._A
		else:
			self._Z = self._V_s[i-1]

	def _sklearn_pretrain(self, i):
		nmf_model = NMF(n_components=self.layers[i],
				init="random",
				random_state=self.seed,
				max_iter=self.pre_iterations)

		U = nmf_model.fit_transform(self._Z)
		V = nmf_model.components_
		return U, V

	def _pre_training(self):
		self._U_s = []
		self._V_s = []
		for i in range(self._p):
			self._setup_z(i)
			U, V = self._sklearn_pretrain(i)
			self._U_s.append(U)
			self._V_s.append(V)

	def _setup_Q(self):
		self._Q_s = [None for _ in range(self._p+1)]
		self._Q_s[self._p] = np.eye(self.layers[self._p-1])
		for i in range(self._p-1, -1, -1):
			self._Q_s[i] = np.dot(self._U_s[i], self._Q_s[i+1])

	def _update_U(self, i):
		if i == 0:
			R = self._U_s[0].dot(self._Q_s[1].dot(self._VpVpT).dot(self._Q_s[1].T))
			R = R+self._A_sq.dot(self._U_s[0].dot(self._Q_s[1].dot(self._Q_s[1].T)))
			Ru = 2*self._A.dot(self._V_s[self._p-1].T.dot(self._Q_s[1].T))
			self._U_s[0] = (self._U_s[0]*Ru)/np.maximum(R, 10**-10)
		else:
			R = self._P.T.dot(self._P).dot(self._U_s[i]).dot(self._Q_s[i+1]).dot(self._VpVpT).dot(self._Q_s[i+1].T)
			R = R+self._A_sq.dot(self._P).T.dot(self._P).dot(self._U_s[i]).dot(self._Q_s[i+1]).dot(self._Q_s[i+1].T)
			Ru = 2*self._A.dot(self._P).T.dot(self._V_s[self._p-1].T).dot(self._Q_s[i+1].T)
			self._U_s[i] = (self._U_s[i]*Ru)/np.maximum(R, 10**-10)

	def _update_P(self, i):
		if i == 0:
			self._P = self._U_s[0]
		else:
			self._P = self._P.dot(self._U_s[i])

	def _update_V(self, i):
		if i < self._p-1:
			Vu = 2*self._A.dot(self._P).T
			Vd = self._P.T.dot(self._P).dot(self._V_s[i])+self._V_s[i]
			self._V_s[i] = self._V_s[i] * Vu/np.maximum(Vd, 10**-10)
		else:
			Vu = 2*self._A.dot(self._P).T+(self.lamb*self._A.dot(self._V_s[i].T)).T
			Vd = self._P.T.dot(self._P).dot(self._V_s[i])
			Vd = Vd + self._V_s[i]+(self.lamb*self._D.dot(self._V_s[i].T)).T
			self._V_s[i] = self._V_s[i] * Vu/np.maximum(Vd, 10**-10)

	def _setup_VpVpT(self):
		self._VpVpT = self._V_s[self._p-1].dot(self._V_s[self._p-1].T)

	def _setup_Asq(self):
		self._A_sq = self._A.dot(self._A.T)

	def get_embedding(self):
		embedding = [self._P, self._V_s[-1].T]
		embedding = np.concatenate(embedding, axis=1)
		return embedding

	def get_memberships(self, filename, meth, issplit, ismergepath):
		index = np.argmax(self._P, axis=1)
		memberships = {int(i): int(index[i]) for i in range(len(index))}
		coms_to_node = defaultdict(list)
		for n, c in memberships.items():
			coms_to_node[c].append(self.nodelist[n])
		
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

	def fit(self, graph):
		self.graph = Multigraph2graph(graph)
		self._setup_target_matrices(self.graph)
		self._pre_training()
		self._setup_Asq()
		for iteration in range(self.iterations):
			self._setup_Q()
			self._setup_VpVpT()
			for i in range(self._p):
				self._update_U(i)
				self._update_P(i)
				self._update_V(i)


