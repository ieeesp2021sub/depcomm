import networkx as nx

class PageRank:

	def __init__(self,graph):
		self.graph = graph
		self.pr = self.run()

	def run(self):
		PR = {}
		leaf = self.getleafnode()
		for startnode in leaf:
			PR[startnode] = 1
			path = [startnode]
			while path:
				pre = path.pop()
				curs = list(self.graph.neighbors(pre))
				for cur in curs:
					if PR.has_key(cur):
						PR[cur] = PR[cur] + PR[startnode]
					else:
						PR[cur] = PR[startnode]
					if self.graph.out_degree(cur) != 0:
						path.append(cur)
		
		for node in PR:
			if PR[node] == 1:
				PR[node] = 0
		return PR

	def getleafnode(self):
		leaf = []
		nodes = self.graph.nodes()
		for node in nodes:
			if self.graph.in_degree(node) == 0:
				leaf.append(node)
		return leaf


