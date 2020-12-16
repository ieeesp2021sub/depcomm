import networkx as nx
import numpy as np
from collections import defaultdict
from utils.Multigraph2graph import Multigraph2graph
from utils.ExportResult import ExportResult

class Fuzzycom:

	def __init__(self,graph,theta,eps,r):
		self.graph = Multigraph2graph(graph)
		self.theta = theta
		self.eps = eps
		self.r = r

	def fuzzy_comm(self, filename, meth, issplit, ismergepath):
		nodelist = list(self.graph.nodes())
		adjacency_mat = nx.to_numpy_matrix(self.graph,nodelist=nodelist)

		theta_cores = []
		num_vertices = adjacency_mat.shape[0]

		dist = list(nx.all_pairs_shortest_path_length(self.graph))

		fuzz_d = np.zeros(shape=adjacency_mat.shape).astype(float)
		for i in range(num_vertices):
			nid, n_dist = dist[i]
			for j in nodelist:
				if j in n_dist and n_dist[j] <= self.r:
					fuzz_d[nodelist.index(nid)][nodelist.index(j)] = 1 / float(1 + n_dist[j])

		_sum = np.sum(fuzz_d, axis=1)

		for i in range(num_vertices):
			fuzz_d[i] = fuzz_d[i] / float(_sum[i])

		for i in range(num_vertices):
			if np.sum(fuzz_d[:, i]) >= self.theta:
				theta_cores.append(i)

		theta_cores = np.array(theta_cores)
		num_cores = len(theta_cores)
		_sum = np.sum(fuzz_d[:, theta_cores], axis=1)
		k = 0
		for i in range(num_vertices):
			fuzz_d[i] = fuzz_d[i] / _sum[k]
			k += 1

		communities = []
		visited = np.zeros(num_cores)

		for i in range(num_cores):
			if visited[i] == 0:
				c = [theta_cores[i]]
				visited[i] = 1
				reach = self.__reachable(i, theta_cores, fuzz_d, visited.copy())
				for core_ind in reach:
					if self.__gran_embed(theta_cores[core_ind], c, fuzz_d) > self.eps:
						c.append(theta_cores[core_ind])
						visited[core_ind] = 1
				communities.append(c)

		cms = []
		cmos = []
		for c in communities:
			cms.append([int(n) for n in c])
			cmos.append([nodelist[int(n)] for n in c])

		fuzz_assoc = defaultdict(dict)
		for i in range(num_vertices):
			for j in range(len(cms)):
				fuzz_assoc[i][j] = np.sum(fuzz_d[i, cms[j]])
		
		nodes = self.graph.nodes()
		found = []
		a = []
		for x in cmos:
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
		
	def __reachable(self, i, theta_cores, fuzz_d, visited):
		reach = []
		flag = True
		index = -1
		num_cores = len(theta_cores)
		while flag:
			if index == len(reach):
				flag = False
			if index == -1:
				flag = False
				for j in range(num_cores):
					if visited[j] == 0 and i != j:
						if fuzz_d[theta_cores[i]][theta_cores[j]] > 0:
							visited[j] = 1
							reach.append(j)
							flag = True

			else:
				for j in range(num_cores):
					if visited[j] == 0 and index != j:
						if fuzz_d[theta_cores[index]][theta_cores[j]] > 0:
							visited[j] = 1
							reach.append(j)
							flag = True
			index += 1
		return np.array(reach)

	def __gran_embed(self,core, c, fuzz_d):
		num = 0
		den = 0
		c = np.array(c)
		c = np.append(c, core)
		n = len(fuzz_d[0])
		for i in range(n):
			num += np.min(fuzz_d[c, i])
			den += np.max(fuzz_d[c, i])
		return float(num) / den

