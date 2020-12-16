import networkx as nx
from gensim.models import Word2Vec,LdaModel
from gensim import corpora
from utils.ExportResult import ExportResult


class Deepwalk:

	def __init__(self, graph):
		self.graph = graph
		self.nodes = self.graph.nodes()

	def randomwalk(
			self, 
			number_walks, 
			walk_length, 
			alpha, 
			rand, 
			direct,
			filename):

		print("Walking...")
		write_file = open('../detection_file/'+filename+'_deepwalk_walk.csv','w')
		walks = []
		nodes = list(self.graph.nodes())
		for i in range(number_walks):
			rand.shuffle(nodes)
			for node in nodes:
				one_walk = self.walk(node, walk_length, rand, alpha, direct)
				self.export_walks(one_walk, write_file)
				one_walk = self.removingfile(one_walk)
				walks.append(one_walk)
		return walks

	def walk(self, start, walk_length, rand, alpha, direct):
		path = [start]
		while len(path) < walk_length:
			cur = path[-1]
			if direct:
				next_nodes = self.in_neighbor(cur)
			else:
				next_nodes = self.all_neighbor(cur)
			if len(next_nodes) > 0:
				if rand.random() >= alpha:
					path.append(rand.choice(next_nodes))
				else:
					path.append(path[0])
			else:
				break
		path = self.removingsysfile(path)
		
		return path

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


	def all_neighbor(self, node):
		return list(nx.all_neighbors(self.graph, node))

	def in_neighbor(self, node):
		in_node = []
		for i in list(self.graph.in_edges(node)):
			in_node.append(i[0])
		return in_node

	def out_neighbor(self, node):
		return list(graph.neighbors(node))

	def removingsysfile(self, path):
		nodes = self.graph.nodes()
		new_path = []
		for item in path:
			node = nodes[item]['data_node']
			if node.__class__.__name__ == 'FileNode':
				if node.filename in Systemfile.sysfile:
					continue
			new_path.append(item)
		return new_path

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
		#	node = nodes[i]['data_node']
		#	if node.__class__.__name__ == 'ProcessNode':
		#		write_file.write(node.pidname+'('+node.pid+')'+'('+i+'),')
		#	elif node.__class__.__name__ == 'FileNode':
		#		write_file.write(node.filename+'('+i+'),')
		#	elif node.__class__.__name__ == 'NetworkNode':
		#		write_file.write(node.sourceIP+':'+node.sourcePort + '->' +node.desIP+':'+node.desPort+'('+i+'),')
		#	elif node.__class__.__name__ == 'NetworkNode2':
		#		write_file.write(sourcenode_out.desIP+':'+sourcenode_out.desPort+'('+i+'),')
		#write_file.write('\n')
		write_file.write(','.join(one_walks))
		write_file.write('\n')
	
	def walks_from_file(self,filename):
		walkspath = '../detection_file/'+filename+'_deepwalk_walk.csv'
		walks = []
		walks_file = open(walkspath)
		line = walks_file.readline()
		while line != '':
			line = line.rstrip()
			part = line.split(',')
			part = self.removingfile(part)
			walks.append(part)
			line = walks_file.readline()
		return walks


