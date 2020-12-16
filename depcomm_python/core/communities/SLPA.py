import networkx as nx
import numpy as np
import copy
from collections import defaultdict
from utils.Multigraph2graph import Multigraph2graph
from utils.ExportResult import ExportResult

class SLPA:

	def __init__(self,graph,iter_num,threshold):
		self.graph = Multigraph2graph(graph)
		self.t = iter_num
		self.r = threshold

	def slpa(self, filename, meth, issplit, ismergepath):
		memory = {i: {i: 1} for i in self.graph.nodes()}
		for t in range(self.t):
			listeners_order = list(self.graph.nodes())
			np.random.shuffle(listeners_order)

			for listener in listeners_order:
				speakers = self.graph[listener].keys()
				if len(speakers) == 0:
					continue

				labels = defaultdict(int)
				for j, speaker in enumerate(speakers):
					total = float(sum(memory[speaker].values()))
					labels[list(memory[speaker].keys())[
						np.random.multinomial(1, [freq / total for freq in memory[speaker].values()]).argmax()]] += 1

				accepted_label = max(labels, key=labels.get)

				if accepted_label in memory[listener]:
					memory[listener][accepted_label] += 1
				else:
					memory[listener][accepted_label] = 1

		for node, mem in memory.items():
			its = copy.copy(list(mem.items()))
			for label, freq in its:
				if freq / float(self.t + 1) < self.r:
					del mem[label]

		communities = {}
		for node, mem in memory.items():
			for label in mem.keys():
				if label in communities:
					communities[label].add(node)
				else:
					communities[label] = {node}

		nested_communities = set()
		keys = list(communities.keys())
		for i, label0 in enumerate(keys[:-1]):
			comm0 = communities[label0]
			for label1 in keys[i + 1:]:
				comm1 = communities[label1]
				if comm0.issubset(comm1):
					nested_communities.add(label0)
				elif comm0.issuperset(comm1):
					nested_communities.add(label1)

		for comm in nested_communities:
			del communities[comm]

		coms = [list(c) for c in communities.values()]
		
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


