from collections import defaultdict
import networkx as nx
from utils.Multigraph2graph import Multigraph2graph
from utils.ExportResult import ExportResult

class PercoMCV:

	def __init__(self, graph):
		self.graph = Multigraph2graph(graph)

	def percoMVC(self, filename, meth, issplit, ismergepath):
		c = list(self.__k_clique_communities(self.graph))

		m2 = set()
		coms = []
		for com in c:
			coms_list = list(com)
			coms += [coms_list]
			m1 = set(coms_list)
			m2 = m2 | m1

		t = []
		p = 1
		while p <= len(self.graph.nodes):
			t.append(p)
			p += 1
		t = set(t)
		nodn_classes = t - m2

		nodn_classes = sorted(nodn_classes)

		for Com in range(len(coms)):
			if len(coms[Com]) > 3:
				sub = self.graph.subgraph(coms[Com])
				centrality = nx.eigenvector_centrality(sub)
				vercteur_pr = sorted((round((centrality[node]), 2), node) for node in centrality)
				for vect in range(len(vercteur_pr)):
					centralitiness = vercteur_pr[vect][0] / vercteur_pr[len(vercteur_pr) - 1][0]
					if centralitiness >= 0.99:
						neud_central = vercteur_pr[vect][1]
						for nod in range(len(nodn_classes)):
							if self.graph.has_edge(nodn_classes[nod], neud_central):
								coms[Com] += [nodn_classes[nod]]

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

	def __k_clique_communities(self, g, cliques=None):
		if cliques is None:
			cliques = nx.find_cliques(g)
		cliques = [frozenset(c) for c in cliques if len(c) >= 3]

		membership_dict = defaultdict(list)
		for clique in cliques:
			for node in clique:
				membership_dict[node].append(clique)

		perc_graph = nx.Graph()
		perc_graph.add_nodes_from(cliques)
		for clique in cliques:
			for adj_clique in self._get_adjacent_cliques(clique, membership_dict):
				if len(clique.intersection(adj_clique)) >= 3:
					perc_graph.add_edge(clique, adj_clique)

		for component in nx.connected_components(perc_graph):
			yield frozenset.union(*component)

	def _get_adjacent_cliques(self, clique, membership_dict):
		adjacent_cliques = set()
		for n in clique:
			for adj_clique in membership_dict[n]:
				if clique != adj_clique:
					adjacent_cliques.add(adj_clique)
		return adjacent_cliques
