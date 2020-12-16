from Deepwalk import Deepwalk
from utils.AliasSimple import AliasSimple
from gensim.models import Word2Vec,LdaModel
from gensim import corpora
from utils.PageRank import PageRank
from utils.Rbo import Rbo
from utils.ExportResult import ExportResult
import networkx as nx
import random
import math

class Specific:

	def __init__(self, graph, beta, thre):
		self.graph = graph
		self.dw = Deepwalk(graph)
		self.beta = beta
		self.thre = thre
		self.counthistory = {}
		self.processlink = {}
		self.PR = {}
		self.pgraph = nx.DiGraph()
	
	def getProcesslink(self):
		nodes = self.graph.nodes()
		for node in nodes:
			if nodes[node]['data_node'].__class__.__name__ == 'ProcessNode':
				self.processlink[node] = []
				queue = [node]
				while queue:
					cur = queue.pop()
					if not self.pgraph.has_node(cur):
						self.pgraph.add_node(cur,data_node=nodes[node]['data_node'])
					neighbors = set(nx.all_neighbors(self.graph, cur))
					for ngb in neighbors:
						if nodes[ngb]['data_node'].__class__.__name__ == 'ProcessNode':
							if self.graph[ngb][cur][0]['data_edge'].direct == 'forward':
								if not self.pgraph.has_node(ngb):
									self.pgraph.add_node(ngb,data_node=nodes[ngb]['data_node'])
								if not self.pgraph.has_edge(ngb,cur):
									self.pgraph.add_edge(ngb,cur,data_edge=self.graph[ngb][cur][0]['data_edge'])
								queue.append(ngb)
								nneighbors = set(nx.all_neighbors(self.graph, ngb))
								n = 0
								for nngb in nneighbors:
									if nodes[nngb]['data_node'].__class__.__name__ == 'ProcessNode':
										if self.graph[nngb][ngb][0]['data_edge'].direct == 'back':
											n+=1
								if n > 1:
									self.processlink[node].append(ngb)
					if not queue:
						if not self.processlink[node]:
							self.processlink[node].append(cur)
						elif self.processlink[node][-1] != cur:
							self.processlink[node].append(cur)
	
	def getProcesslink2(self):
		nodes = self.graph.nodes()
		for node in nodes:
			if nodes[node]['data_node'].__class__.__name__ == 'ProcessNode':
				self.processlink[node] = []
				queue = [node]
				while queue:
					cur = queue.pop()
					if not self.pgraph.has_node(cur):
						self.pgraph.add_node(cur,data_node=nodes[node]['data_node'])
					in_neighbors = self.in_neighbor(cur) 
					for in_ngb in in_neighbors:
						if nodes[in_ngb]['data_node'].__class__.__name__ == 'ProcessNode':
							if self.graph[in_ngb][cur][0]['data_edge'].direct == 'forward':
								if not self.pgraph.has_node(in_ngb):
									self.pgraph.add_node(in_ngb,data_node=nodes[in_ngb]['data_node'])
								if not self.pgraph.has_edge(in_ngb,cur):
									self.pgraph.add_edge(in_ngb,cur,data_edge=self.graph[in_ngb][cur][0]['data_edge'])
								queue.append(in_ngb)
								nneighbors = set(self.graph.neighbors(in_ngb))
								n = 0
								for nngb in nneighbors:
									if nodes[nngb]['data_node'].__class__.__name__ == 'ProcessNode':
										if self.graph[in_ngb][nngb][0]['data_edge'].direct == 'forward':
											n+=1
								if n > 1:
									self.processlink[node].append(in_ngb)
					if not queue:
						if not self.processlink[node]:
							self.processlink[node].append(cur)
						elif self.processlink[node][-1] != cur:
							self.processlink[node].append(cur)

	def getPR(self):
		pgraph_rev = self.pgraph.reverse()
		self.PR = PageRank(pgraph_rev).pr

	def getweight1(self, prev, cur, nbr):
		#if self.counthistory.has_key((nbr,cur)):
		#	count = self.counthistory[(nbr,cur)]
		#else:
		#	count = 0
		#return math.tanh(count)
		if prev == nbr:
			return 1.0
		else:
			return 0.0

	def getweight2(self, prev, cur, nbr, pnum, fnum, nnum):
		nodes = self.graph.nodes()
		if prev == nbr:
			return 0.0
		else:
			#pnum = len(set(self.pgraph.neighbors(cur)))
			if nodes[nbr]['data_node'].__class__.__name__ == 'ProcessNode':
				pr_cur = self.PR[cur]
				pr_nbr = self.PR[nbr]
				if pr_nbr > pr_cur:
					return pr_cur/pr_nbr
				elif pr_nbr == pr_cur:
					return 1.0
				else:
					return (1.0 - pr_nbr/pr_cur)/pnum
					#return (1.0 - pr_nbr/pr_cur)
			elif nodes[nbr]['data_node'].__class__.__name__ == 'FileNode':
				return 1.0/fnum
			elif nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode':
				return 1.0/nnum
			elif nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode2':
				return 1.0/nnum
	
	def getweight3(self, prev, nbr):
		prev_list = self.processlink[prev]
		nbr_list = self.processlink[nbr]
		ld = len(prev_list) - len(nbr_list)
		if ld > 0:
			if nbr in prev_list:
				return 0.0
			else:
				nbr_list = [nbr]*ld + nbr_list
		elif ld < 0:
			if prev in nbr_list:
				return 1.0
			else:
				prev_list = [prev]*abs(ld) + prev_list
		rbo = Rbo(prev_list, nbr_list, self.beta).rbo_ext
		return rbo

	def processweight(self,unnormalized_probs,backlocal,thre):
		if backlocal == None:
			return unnormalized_probs
		else:
			n = 0
			for i,prob in enumerate(unnormalized_probs):
				if prob < thre:
					unnormalized_probs[i] = 0.0
				else:
					n += 1
			if n > 1:
				unnormalized_probs[backlocal] = 0.0
			return unnormalized_probs

	def getstartprobs(self, start, neighbors):
		pnum = len(set(nx.all_neighbors(self.pgraph, start)))
		fnum,nnum = self.fileornet_nbr_num(start)
		unnormalized_probs = []
		nodes = self.graph.nodes()
		for nbr in neighbors:
			if nodes[nbr]['data_node'].__class__.__name__ == 'ProcessNode':
				unnormalized_probs.append(1.0/pnum)
			elif nodes[nbr]['data_node'].__class__.__name__ == 'FileNode':
				unnormalized_probs.append(1.0/fnum)
			elif nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode':
				unnormalized_probs.append(1.0/nnum)
			elif nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode2':
				unnormalized_probs.append(1.0/nnum)
		norm_const = sum(unnormalized_probs)
		normalized_probs = [float(u_prob)/norm_const for u_prob in unnormalized_probs]
		return AliasSimple.alias_setup(normalized_probs)

	def getnextprobs(self, pprev, prev, cur, cur_nbrs):
		unnormalized_probs = []
		nodes = self.graph.nodes()
		backlocal = None
		if len(cur_nbrs) == 1:
			unnormalized_probs.append(1)
		elif pprev == None:
			if nodes[cur]['data_node'].__class__.__name__ == 'ProcessNode':
				prd = self.PR[cur] - self.PR[prev]
				if prd > 0:
					for nbr in cur_nbrs:
						w = self.getweight1(prev,cur,nbr)
						unnormalized_probs.append(w)
				else:
					pnum = self.p_nbr_num(cur)
					fnum,nnum = self.fileornet_nbr_num(cur)
					for nbr in cur_nbrs:
						w = self.getweight2(prev,cur,nbr,pnum,fnum,nnum)
						unnormalized_probs.append(w)
			else:
				for nbr in cur_nbrs:
					w = self.getweight3(prev,nbr)
					unnormalized_probs.append(w)
					if prev == nbr:
						backlocal = len(unnormalized_probs) - 1
		else:
			if nodes[cur]['data_node'].__class__.__name__ == 'ProcessNode':
				prd = self.PR[cur] - self.PR[pprev]
				if prd > 0:
					for nbr in cur_nbrs:
						w = self.getweight1(prev,cur,nbr)
						unnormalized_probs.append(w)
				else:
					pnum = self.p_nbr_num(cur)
					fnum,nnum = self.fileornet_nbr_num(cur)
					for nbr in cur_nbrs:
						w = self.getweight2(prev,cur,nbr,pnum,fnum,nnum)
						unnormalized_probs.append(w)
			else:
				for nbr in cur_nbrs:
					w = self.getweight3(prev,nbr)
					unnormalized_probs.append(w)
					if prev == nbr:
						backlocal = len(unnormalized_probs) - 1
		
		if nodes[cur]['data_node'].__class__.__name__ != 'ProcessNode':
			unnormalized_probs = self.processweight(unnormalized_probs,backlocal,self.thre)
		norm_const = sum(unnormalized_probs)
		normalized_probs = [float(u_prob)/norm_const for u_prob in unnormalized_probs]
		#print prev, cur
		#print cur_nbrs
		#print normalized_probs
		return AliasSimple.alias_setup(normalized_probs)

	def randomwalk(self, number_walks, walk_length, filename):
		print 'walking...'
		write_file = open('../detection_file/'+filename+'_specific_walk.csv','w')
		walks = []
		nodes = self.graph.nodes()
		node_list = list(self.graph.nodes)
		for walk_iter in range(number_walks):
			random.shuffle(node_list)
			for node in node_list:
				if nodes[node]['data_node'].__class__.__name__ == 'ProcessNode':
					#print '+++++++++++++++++++++++++++++++++++'
					one_walk = self.walk(walk_length=walk_length, start_node=node)
					self.dw.export_walks(one_walk, write_file)
					walks.append(one_walk)
		return walks

	def walk(self, walk_length, start_node):
		self.counthistory = {}
		walk = [start_node]
		while len(walk) < walk_length:
			cur = walk[-1]
			cur_nbrs = sorted(set(nx.all_neighbors(self.graph, cur)))
			if len(cur_nbrs) > 0:
				if len(walk) == 1:
					probs = self.getstartprobs(cur, cur_nbrs)
					walk.append(cur_nbrs[AliasSimple.alias_draw(probs[0], probs[1])])
				else:
					prev = walk[-2]
					nodes = self.graph.nodes()
					if self.counthistory.has_key((prev,cur)):
						self.counthistory[(prev,cur)] += 1
					else:
						self.counthistory[(prev,cur)] = 1
					#print '-----------------------'
					if nodes[prev]['data_node'].__class__.__name__ == 'ProcessNode':
						probs = self.getnextprobs(None, prev, cur, cur_nbrs)
						walki = cur_nbrs[AliasSimple.alias_draw(probs[0], probs[1])]
						walk.append(walki)
						#print walki
					else:
						pprev = walk[-3]
						probs = self.getnextprobs(pprev, prev, cur, cur_nbrs)
						walki = cur_nbrs[AliasSimple.alias_draw(probs[0], probs[1])]
						walk.append(walki)
						#print walki
			else:
				break
		return walk

	def to_vector(self, walks, window_size, embedding_size, sg, hs, epoch, batch):
		print 'generating vector...'
		model = Word2Vec(
				sentences=walks, 
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
			cluster_probability = lda_model.get_term_topics(node2id[node],minimum_probability=0.0)
			probs = []
			for i in cluster_probability:
				probs.append(i[1])
			z.append((node,probs))
		ExportResult.exportaffiliation(self.graph, z, filename, meth, issplit, ismergepath)

	def in_neighbor(self, node):
		in_node = []
		for i in list(self.graph.in_edges(node)):
			in_node.append(i[0])
		return in_node
	
	def p_nbr_num(self,pnode):
		pnum = len(set(self.pgraph.neighbors(pnode)))
		return pnum

	def fileornet_nbr_num(self,pnode):
		fnum = 0
		nnum = 0
		nodes = self.graph.nodes()
		nbrs = set(nx.all_neighbors(self.graph, pnode))
		for nbr in nbrs:
			if nodes[nbr]['data_node'].__class__.__name__ == 'FileNode':
				fnum+=1
			elif nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode':
				nnum+=1
			elif nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode2':
				nnum+=1
		return fnum, nnum


