import networkx as nx
from utils.Multigraph2graph import Multigraph2graph
from utils.ExportResult import ExportResult

class Lais2:
	
	def __init__(self, graph):
		self.graph = Multigraph2graph(graph)

	def __weight(self,community):
		if nx.number_of_nodes(community) == 0:
			return 0
		else:
			return float(2*nx.number_of_edges(community)/nx.number_of_nodes(community))

	def __order_nodes(self):

		def __get_key(node):
			return node[1]

		dict_of_nodes = nx.pagerank(self.graph)
		ordered_nodes = dict_of_nodes.items()
		ordered_nodes = sorted(ordered_nodes, reverse=True, key=__get_key)
		return ordered_nodes

	def __list_aggregate(self):
		ordered_nodes = self.__order_nodes()

		coms = []
		for i in ordered_nodes:
			added = False
			for c in coms:
				temp1 = self.graph.subgraph(c)
				cc = list(c)
				cc.append(i[0])
				temp2 = self.graph.subgraph(cc)
				if self.__weight(temp2) > self.__weight(temp1):
					added = True
					c.append(i[0])
			if not added:
				coms.append([i[0]])
		return coms
	
	def __is2(self, cluster):
		c = self.graph.subgraph(cluster)
		initial_weight = self.__weight(c)
		increased = True
		while increased:
			list_of_nodes = cluster
			for vertex in c.nodes():
				adjacent_nodes = self.graph.neighbors(vertex)
				list_of_nodes = list(set(list_of_nodes).union(set(adjacent_nodes)))

			for vertex in list_of_nodes:
				list_of_nodes = list(c.nodes())
				if vertex in c.nodes():
					list_of_nodes.remove(vertex)
				else:
					list_of_nodes.append(vertex)
				c_dash = self.graph.subgraph(list_of_nodes)

				if self.__weight(c_dash) > self.__weight(c):
					c = c_dash.copy()
			new_weight = self.__weight(c)
			if new_weight == initial_weight:
				increased = False
			else:
				initial_weight = new_weight
		return c

	def Lais2(self, filename, meth, issplit, ismergepath):
		initial_clusters = self.__list_aggregate()

		final_clusters = []
		initial_clusters_without_duplicates = []
		for cluster in initial_clusters:
			cluster = sorted(cluster)
			if cluster not in initial_clusters_without_duplicates:
				initial_clusters_without_duplicates.append(cluster)
				updated_cluster = self.__is2(cluster)
				final_clusters.append(updated_cluster.nodes())

		final_clusters_without_duplicates = []
		for cluster in final_clusters:
			cluster = sorted(cluster)
			if cluster not in final_clusters_without_duplicates:
				final_clusters_without_duplicates.append(cluster)
		
		nodes = self.graph.nodes()
		found = []
		a = []
		for x in final_clusters_without_duplicates:
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


