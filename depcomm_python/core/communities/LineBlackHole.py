from utils.Multigraph2graph import Multigraph2graph
import networkx as nx
from Deepwalk import Deepwalk
from utils.ExportResult import ExportResult
from sklearn.cluster import KMeans
import random
import numpy as np

class LineBlackHole:

	def __init__(self,graph,number_walks,walk_length,window_size,embedding_size,cluster_num,direct,sg,hs,epoch,batch):
		self.graph = Multigraph2graph(graph)
		self.number_walks = number_walks
		self.walk_length = walk_length
		self.window_size = window_size
		self.embedding_size = embedding_size
		self.cluster_num = cluster_num
		self.direct = direct
		self.sg = sg
		self.hs = hs
		self.epoch = epoch
		self.batch = batch

	def lineblackhole(self,filename,meth,issplit,ismergepath):
		edges, linegraph = self.linegraph(self.graph)
		
		dw = Deepwalk(linegraph)
		walks = dw.randomwalk(
				number_walks=self.number_walks, 
				walk_length=self.walk_length, 
				alpha=0, 
				rand=random.Random(0), 
				direct=self.direct, 
				filename=filename)

		model = dw.to_vector(
				walks = walks, 
				window_size = self.window_size, 
				embedding_size = self.embedding_size, 
				sg = self.sg, 
				hs = self.hs, 
				epoch = self.epoch, 
				batch = self.batch)
		
		model.wv.save_word2vec_format('../detection_file/'+filename+'_'+meth+'_vector.csv')

		self.cluster(filename=filename, 
				meth=meth, 
				c=self.cluster_num, 
				graph=self.graph, 
				issplit=issplit,
				ismergepath=ismergepath,
				edges=edges)


	def linegraph(self,graph):
		linegraph = nx.Graph()
		edges = list(graph.edges())
		edge_one = []
		edge_weight = []
		edge_tmp = []
		for i in range(len(edges)):
			linegraph.add_node(str(i))
		for x, edge_x in enumerate(edges):
			for y, edge_y in enumerate(edges):
				share_node = set(edge_x).intersection(set(edge_y))
				if len(share_node) == 1:
					if ((x,y) in edge_tmp) or ((y,x) in edge_tmp):
						continue
					else:
						linegraph.add_edge(str(x),str(y))
						edge_tmp.append((x,y))

		return edges,linegraph


	def cluster(self,filename,meth,c,graph,issplit,edges):
		
		fr = open('../detection_file/'+filename+'_'+meth+'_vector.csv')
		line = fr.readline()                                                                                                                             
		part_1 = line.split(' ')
		num_data = int(part_1[0])
		dimension = int(part_1[1].rstrip())
		line = fr.readline()
		data = []
		nodes = []

		while line != '':
			part = line.split(' ')
			node = part[0]
			data_line = part[1:]
			data_line = [float(i.rstrip()) for i in data_line]
			nodes.append(node)
			data.append(data_line)
			line = fr.readline()

		data = np.array(data)
		clf = KMeans(n_clusters=c)
		clf.fit(data)
		result = {}
		for i in range(c):
			result[i] = []
		labels = clf.predict(data).tolist()
		for index,label in enumerate(labels):
			result[label].append(nodes[index])

		coms = []
		for ckey in result:
			com = set()
			for edge_id in result[ckey]:
				com.add(edges[int(edge_id)][0])
				com.add(edges[int(edge_id)][1])
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

		ExportResult.exportaffiliation(self.graph, z, filename, meth, issplit)

