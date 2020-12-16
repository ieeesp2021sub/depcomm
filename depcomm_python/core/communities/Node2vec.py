from Deepwalk import Deepwalk
from utils.AliasSimple import AliasSimple
from gensim.models import Word2Vec,LdaModel
from gensim import corpora
from utils.ExportResult import ExportResult
import networkx as nx
import random

class Node2vec:

	def __init__(self, graph, direct, p, q):
		self.graph = graph
		#self.dw = Deepwalk(graph)
		self.direct = direct
		self.p = p
		self.q = q
		self.nodes = self.graph.nodes()

	def preprocess_transition_probs(self):
		print 'preprocess transition probables...'
		alias_nodes = {}
		for node in self.graph.nodes():
			if self.direct:
				neighbor = self.dw.in_neighbor(node)
			else:
				neighbor = list(nx.all_neighbors(self.graph, node))
			if len(neighbor) == 0:
				normalized_probs = []
			else:
				normalized_probs = [1.0/len(neighbor)]*len(neighbor)
			alias_nodes[node] = AliasSimple.alias_setup(normalized_probs)

		alias_edges = {}
		if self.direct:
			for edge in list(self.graph.edges()):
				alias_edges[edge[1],edge[0]] = self.get_alias_edge(edge[1], edge[0])
		else:
			for edge in list(self.graph.edges()):
				alias_edges[edge] = self.get_alias_edge(edge[0], edge[1])
				alias_edges[edge[1],edge[0]] = self.get_alias_edge(edge[1], edge[0])
		
		self.alias_nodes = alias_nodes
		self.alias_edges = alias_edges

		return

	def get_alias_edge(self, src, dst):
		unnormalized_probs = []

		if self.direct:
			for dst_nbr in sorted(self.dw.in_neighbor(dst)):
				if dst_nbr == src:
					unnormalized_probs.append(1/self.p)
				elif self.graph.has_edge(dst_nbr, src):
					unnormalized_probs.append(1)
				else:
					unnormalized_probs.append(1/self.q)
		else:
			for dst_nbr in sorted(nx.all_neighbors(self.graph, dst)):
				if dst_nbr == src:
					unnormalized_probs.append(1/self.p)
				elif self.graph.has_edge(dst_nbr, src) or self.graph.has_edge(src, dst_nbr):
					unnormalized_probs.append(1)
				else:
					unnormalized_probs.append(1/self.q)

		norm_const = sum(unnormalized_probs)
		normalized_probs = [float(u_prob)/norm_const for u_prob in unnormalized_probs]
		return AliasSimple.alias_setup(normalized_probs)

	def randomwalk(self, number_walks, walk_length, filename):
		print 'walking...'
		write_file = open('../detection_file/'+filename+'_node2vec_walk.csv','w')
		walks = []
		nodes = list(self.graph.nodes)
		for walk_iter in range(number_walks):
			random.shuffle(nodes)
			for node in nodes:
				one_walk = self.walk(walk_length=walk_length, start_node=node)
				self.export_walks(one_walk, write_file)
				one_walk = self.removingfile(one_walk)
				walks.append(one_walk)
		return walks
		
	def walk(self, walk_length, start_node):
		walk = [start_node]
		while len(walk) < walk_length:
			cur = walk[-1]
			if self.direct:
				cur_nbrs = sorted(self.dw.in_neighbor(cur))
			else:
				cur_nbrs = sorted(nx.all_neighbors(self.graph, cur))

			if len(cur_nbrs) > 0:
				if len(walk) == 1:
					walk.append(cur_nbrs[AliasSimple.alias_draw(self.alias_nodes[cur][0], self.alias_nodes[cur][1])])
				else:
					prev = walk[-2]
					next_node = cur_nbrs[AliasSimple.alias_draw(self.alias_edges[(prev, cur)][0],self.alias_edges[(prev, cur)][1])]
					walk.append(next_node)
			else:
				break
		walk = self.removingsysfile(walk)	
		return walk
		
	def to_vector(self, walks, window_size, embedding_size, sg, hs, epoch, batch):
		print 'generating vector...'
		model = Word2Vec(
				sentences = walks, 
				size=embedding_size, 
				window=window_size, 
				min_count=0, 
				sg=sg, 
				hs=hs, 
				iter=epoch, 
				batch_words=batch)
		return model
	
	def lda(self, walks, cluster_num, epoch, batch, filename, meth, issplit, ismergepath):
		print 'running lda...'
		dictionary = corpora.Dictionary(walks)
		corpus = [dictionary.doc2bow(words) for words in walks]
		node2id = dictionary.token2id
		lda_model = LdaModel(corpus=corpus, num_topics=cluster_num, iterations=epoch, update_every=batch)
		nodes = self.graph.nodes()
		z = []	
		for node in nodes:
			if nodes[node]['data_node'].unidname in Systemfile.sysfile:continue
			cluster_probability = lda_model.get_term_topics(node2id[node],minimum_probability=0.0)
			probs = []
			for i in cluster_probability:
				probs.append(i[1])
			z.append((node,probs))
		ExportResult.exportaffiliation(self.graph, z, filename, meth, issplit, ismergepath)

	def removingfile(self, path):
		new_path = []
		for item in path:
			node = self.nodes[item]['data_node']
			if node.__class__.__name__ == 'ProcessNode':
				new_path.append(item)
		return new_path
	
	def export_walks(self, one_walks, write_file):
		#nodes = self.graph.nodes()
		#for i in one_walks:
		#   node = nodes[i]['data_node']
		#   if node.__class__.__name__ == 'ProcessNode':
		#       write_file.write(node.pidname+'('+node.pid+')'+'('+i+'),')
		#   elif node.__class__.__name__ == 'FileNode':
		#       write_file.write(node.filename+'('+i+'),')
		#   elif node.__class__.__name__ == 'NetworkNode':
		#       write_file.write(node.sourceIP+':'+node.sourcePort + '->' +node.desIP+':'+node.desPort+'('+i+'),')
		#   elif node.__class__.__name__ == 'NetworkNode2':
		#       write_file.write(sourcenode_out.desIP+':'+sourcenode_out.desPort+'('+i+'),')
		#write_file.write('\n')
		write_file.write(','.join(one_walks))
		write_file.write('\n')

	def walks_from_file(self,filename):
		walkspath = '../detection_file/'+filename+'_node2vec_walk.csv'
		walks = []
		walks_file = open(walkspath)
		line = walks_file.readline()
		while line != '':
			line = line.rstrip()
			part = line.split(',')
			part = self.removingfile(part)
			part = self.removingsysprocess(part)
			walks.append(part)
			line = walks_file.readline()
		return walks


