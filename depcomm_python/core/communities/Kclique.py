import networkx as nx
from utils.ExportResult import ExportResult

class Kclique:

	def __init__(self, graph, k):
		self.graph = graph.to_undirected()
		self.k = k

	def getc(self, filename, meth, issplit, ismergepath):
		nodes = self.graph.nodes()
		coms = list(nx.algorithms.community.k_clique_communities(self.graph, self.k))
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



		


