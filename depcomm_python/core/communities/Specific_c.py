from Deepwalk import Deepwalk
from utils.AliasSimple import AliasSimple
from gensim.models import Word2Vec,LdaModel
from gensim import corpora
from utils.Rbo import Rbo
from utils.PageRank import PageRank
from Systemfile import Systemfile
from utils.ExportResult import ExportResult
import networkx as nx
import random
import datetime
from math import exp,tanh

class Specific2:

	def __init__(self, graph):
		self.graph = graph
		#self.dw = Deepwalk(graph)
		self.beta = 0.8
		self.thre_w8 = 0.2
		self.thre_w9 = 0.2
		self.counthistory = {}
		self.processlink = {}
		self.PR = {}
		self.parent = {}
		self.parents = {}
		self.pgraph = nx.DiGraph()
		self.edges = set(self.graph.edges())
		self.nodes = self.graph.nodes()
	
	def getProcesslink(self):
		for node in self.nodes:
			if self.nodes[node]['data_node'].__class__.__name__ == 'ProcessNode':
				self.processlink[node] = []
				self.parents[node] = []
				queue = [node]
				while queue:
					cur = queue.pop()
					if not self.pgraph.has_node(cur):
						self.pgraph.add_node(cur,data_node=self.nodes[node]['data_node'])
					neighbors = set(nx.all_neighbors(self.graph, cur))
					for ngb in neighbors:
						if self.nodes[ngb]['data_node'].__class__.__name__ == 'ProcessNode':
							if self.graph[ngb][cur][0]['data_edge'].direct == 'forward':
								if not self.pgraph.has_node(ngb):
									self.pgraph.add_node(ngb,data_node=self.nodes[ngb]['data_node'])
								if not self.pgraph.has_edge(ngb,cur):
									self.pgraph.add_edge(ngb,cur,data_edge=self.graph[ngb][cur][0]['data_edge'])
								queue.append(ngb)
								self.parents[node].append(ngb)
								nneighbors = set(nx.all_neighbors(self.graph, ngb))
								n = 0
								for nngb in nneighbors:
									if self.nodes[nngb]['data_node'].__class__.__name__ == 'ProcessNode':
										if self.graph[nngb][ngb][0]['data_edge'].direct == 'back':
											n+=1
								if n > 1:
									self.processlink[node].append(ngb)
					if not queue:
						if not self.processlink[node]:
							self.processlink[node].append(cur)
							self.parents[node].append(cur+'_top')
						elif self.processlink[node][-1] != cur:
							self.processlink[node].append(cur)
							#self.parents[node].append(cur)
	
	def getProcesslink2(self):
		for node in self.nodes:
			if self.nodes[node]['data_node'].__class__.__name__ == 'ProcessNode':
				self.processlink[node] = []
				self.parents[node] = []
				queue = [node]
				while queue:
					cur = queue.pop()
					if not self.pgraph.has_node(cur):
						self.pgraph.add_node(cur,data_node=self.nodes[node]['data_node'])
					in_neighbors = self.in_neighbor(self.graph,cur) 
					for in_ngb in in_neighbors:
						if self.nodes[in_ngb]['data_node'].__class__.__name__ == 'ProcessNode':
							if self.graph[in_ngb][cur][0]['data_edge'].direct == 'forward':
								if not self.pgraph.has_node(in_ngb):
									self.pgraph.add_node(in_ngb,data_node=self.nodes[in_ngb]['data_node'])
								if not self.pgraph.has_edge(in_ngb,cur):
									self.pgraph.add_edge(in_ngb,cur,data_edge=self.graph[in_ngb][cur][0]['data_edge'])
								queue.append(in_ngb)
								self.parents[node].append(in_ngb)
								nneighbors = set(self.graph.neighbors(in_ngb))
								n = 0
								for nngb in nneighbors:
									if self.nodes[nngb]['data_node'].__class__.__name__ == 'ProcessNode':
										if self.graph[in_ngb][nngb][0]['data_edge'].direct == 'forward':
											n+=1
								if n > 1:
									self.processlink[node].append(in_ngb)
					if not queue:
						if not self.processlink[node]:
							self.processlink[node].append(cur)
							self.parents[node].append(cur+'_top')
						elif self.processlink[node][-1] != cur:
							self.processlink[node].append(cur)
							#self.parents[node].append(cur)

	def getParent(self):
		for node in self.nodes:
			par = self.in_neighbor(self.pgraph,node)
			if par:
				self.parent[node] = par[0]
			else:
				self.parent[node] = node+'_top'
	
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

	def getweight2(self, prev, cur, nbr, fnum, nnum):
		if prev == nbr:
			#return 1.0 - exp(-(self.pgraph.out_degree(prev)))
			return 0.0
		else:
			#return exp(-(self.pgraph.out_degree(prev)))/(self.graph.degree(cur)-1.0)
			
			if self.nodes[nbr]['data_node'].__class__.__name__ == 'ProcessNode':
				return 1.0
			elif self.nodes[nbr]['data_node'].__class__.__name__ == 'FileNode':
				return 1.0/fnum
			elif self.nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode':
				return 1.0/nnum
			elif self.nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode2':
				return 1.0/nnum
			''
	def getweight3(self, prev, cur, nbr, pnum, fnum, nnum, thre):
		if prev == nbr:
			return 0.0
		else:
			if self.graph.degree(cur) <= 2:
				return 1.0
			else:
				if self.nodes[nbr]['data_node'].__class__.__name__ == 'ProcessNode':
					#return max(exp(-self.PR[nbr])-thre,0)/pnum
					#return max(exp(-self.pgraph.out_degree(nbr))-thre,0)/pnum
					return 1.0/pnum
				elif self.nodes[nbr]['data_node'].__class__.__name__ == 'FileNode':
					return 1.0/fnum
				elif self.nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode':
					return 1.0/nnum
				elif self.nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode2':
					return 1.0/nnum
	
	def getweight4(self, pprev, prev, cur, nbr):
		if prev == nbr:
			return 1.0
		#elif nbr in self.parents[pprev]:
		#	return 1.0
		elif pprev == nbr:
			return 1.0
		else:
			return 0.0

	def getweight5(self, pprev, prev, cur, nbr, fnum, nnum):
		if prev == nbr:
			#return 1.0 - exp(-(self.pgraph.out_degree(pprev)))
			return 0.0
		#elif pprev == nbr:
		#	return 1.0 - exp(-(self.pgraph.out_degree(pprev)))
		elif pprev == nbr:
			return 1.0
		else:
			''
			if self.nodes[nbr]['data_node'].__class__.__name__ == 'ProcessNode':
				return 1.0
			elif self.nodes[nbr]['data_node'].__class__.__name__ == 'FileNode':
				return 1.0/fnum
			elif self.nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode':
				return 1.0/nnum
			elif self.nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode2':
				return 1.0/nnum
			''	
			#return exp(-(self.pgraph.out_degree(pprev)))/(self.graph.degree(cur)-2.0)

	def getweight6(self, pprev, prev, cur, nbr, pnum, fnum, nnum, thre):
		if prev == nbr:
			return 0.0
		elif self.parent[cur] == nbr:
			#return exp(-self.PR[nbr])/(pnum+1)
			return 1.0
		else:
			if self.nodes[nbr]['data_node'].__class__.__name__ == 'ProcessNode':
				#return max(exp(-self.PR[nbr])-thre,0)/(pnum+1)
				#return max(exp(-self.pgraph.out_degree(nbr))-thre,0)/pnum
				return 1.0/pnum
			elif self.nodes[nbr]['data_node'].__class__.__name__ == 'FileNode':
				return 1.0/fnum
			elif self.nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode':
				return 1.0/nnum
			elif self.nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode2':
				return 1.0/nnum

	def getweight7(self, prev, cur, nbr, pnum, fnum, nnum):
		if prev == nbr:
			return 0.0
		elif self.nodes[nbr]['data_node'].__class__.__name__ == 'ProcessNode':
			return 1.0/(pnum+1)
		elif self.nodes[nbr]['data_node'].__class__.__name__ == 'FileNode':
			return 1.0/fnum
		elif self.nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode':
			return 1.0/nnum
		elif self.nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode2':
			return 1.0/nnum

	def getweight8(self, prev, cur, nbr, thre):
		if prev == nbr:
			return 1.0
		else:
			return 0.0

	def getweight9(self, prev, cur, nbr, pnum, fnum, nnum, thre):
		if prev == nbr:
			return 0.0
		elif self.parent[cur] == nbr:
			return 1.0
		else:
			if self.nodes[nbr]['data_node'].__class__.__name__ == 'ProcessNode':
				return 1.0
			elif self.nodes[nbr]['data_node'].__class__.__name__ == 'FileNode':
				return 1.0
			elif self.nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode':
				return 1.0
			elif self.nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode2':
				return 1.0
		#elif self.parent[cur] == nbr:
		#	return exp(-self.PR[nbr])/(self.graph.degree(cur)-1.0)
		#else:
		#	return max(exp(-self.PR[cur])-thre,0.0)/(self.graph.degree(cur)-1.0)

	def getweight10(self, prev, cur, nbr):
		if prev == nbr:
			return 1.0
		else:
			return self.getrbo(prev,nbr)
			
			''
			'''
			if (prev,cur) in self.edges:
				timestamp_pre = self.graph[prev][cur][0]['data_edge'].starttime.split('.')[0]
				timeArray_pre = datetime.datetime.fromtimestamp(int(timestamp_pre))
				date_pre = timeArray_pre.strftime("%Y-%m-%d")
			else:
				timestamp_pre = self.graph[cur][prev][0]['data_edge'].starttime.split('.')[0]
				timeArray_pre = datetime.datetime.fromtimestamp(int(timestamp_pre))
				date_pre = timeArray_pre.strftime("%Y-%m-%d")
			if (cur,nbr) in self.edges:
				timestamp_next = self.graph[cur][nbr][0]['data_edge'].starttime.split('.')[0]
				timeArray_next = datetime.datetime.fromtimestamp(int(timestamp_next))
				date_next = timeArray_next.strftime("%Y-%m-%d")
			else:
				timestamp_next = self.graph[nbr][cur][0]['data_edge'].starttime.split('.')[0]
				timeArray_next = datetime.datetime.fromtimestamp(int(timestamp_next))
				date_next = timeArray_next.strftime("%Y-%m-%d")
			if date_pre == date_next:
				return self.getrbo(prev,nbr)
			else:
				return 0.0
			'''
			'''
			if (prev,cur) in self.edges and (cur,prev) in self.edges:
				return self.getrbo(prev,nbr)
			elif (prev,cur) in self.edges and (cur,nbr) in self.edges:
				return self.getrbo(prev,nbr)
			elif (cur,prev) in self.edges and (nbr,cur) in self.edges:
				return self.getrbo(prev,nbr)
			else:
				
				if (prev,cur) in self.edges and (nbr,cur) in self.edges:
					prev_name = self.nodes[prev]['data_node'].pidname
					nbr_name = self.nodes[nbr]['data_node'].pidname
					prev_process = len(self.processlink[prev])
					nbr_process = len(self.processlink[nbr])
					if prev_name == nbr_name and prev_process == nbr_process and self.getrbo(prev,nbr) == 1.0:
						return 1.0
					else:
						return 0.0
				else:
					return 0.0
				
				#return 0.0
			'''
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
		for nbr in neighbors:
			if self.nodes[nbr]['data_node'].__class__.__name__ == 'ProcessNode':
				unnormalized_probs.append(1.0/pnum)
			elif self.nodes[nbr]['data_node'].__class__.__name__ == 'FileNode':
				unnormalized_probs.append(1.0/fnum)
			elif self.nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode':
				unnormalized_probs.append(1.0/nnum)
			elif self.nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode2':
				unnormalized_probs.append(1.0/nnum)
		norm_const = sum(unnormalized_probs)
		normalized_probs = [float(u_prob)/norm_const for u_prob in unnormalized_probs]
		return AliasSimple.alias_setup(normalized_probs)

	def getnextprobs(self, pprev, prev, cur, cur_nbrs):
		#if pprev == None:
		#	print prev+':'+cur
		#else:
		#	print pprev+':'+prev+':'+cur
		unnormalized_probs = []
		backlocal = None
		if len(cur_nbrs) == 1:
			unnormalized_probs.append(1)
		elif pprev == None:
			if self.nodes[cur]['data_node'].__class__.__name__ == 'ProcessNode':
				if self.parent[prev] == cur:
					if self.pgraph.out_degree(cur) > 1:
						for nbr in cur_nbrs:
							w = self.getweight1(prev,cur,nbr)
							unnormalized_probs.append(w)
					elif self.pgraph.out_degree(cur) == 1:
						pnum = self.p_nbr_num(cur)
						fnum,nnum = self.fileornet_nbr_num(cur)
						for nbr in cur_nbrs:
							w = self.getweight2(prev,cur,nbr,fnum,nnum)
							unnormalized_probs.append(w)
				elif self.parent[cur] == prev:
					pnum = self.p_nbr_num(cur)
					fnum,nnum = self.fileornet_nbr_num(cur)
					for nbr in cur_nbrs:
						w = self.getweight3(prev,cur,nbr,pnum,fnum,nnum,self.thre_w8)
						unnormalized_probs.append(w)
			else:
				for nbr in cur_nbrs:
					w = self.getweight10(prev,cur,nbr)
					unnormalized_probs.append(w)
					if prev == nbr:
						backlocal = len(unnormalized_probs) - 1
		else:
			if self.nodes[cur]['data_node'].__class__.__name__ == 'ProcessNode':
				if cur in self.parents[pprev]:
					if self.pgraph.out_degree(cur) > 1:
						for nbr in cur_nbrs:
							w = self.getweight4(pprev,prev,cur,nbr)
							unnormalized_probs.append(w)
					elif self.pgraph.out_degree(cur) == 1:
						pnum = self.p_nbr_num(cur)
						fnum,nnum = self.fileornet_nbr_num(cur)
						for nbr in cur_nbrs:
							w = self.getweight5(pprev,prev,cur,nbr,fnum,nnum)
							unnormalized_probs.append(w)
				elif pprev in self.parents[cur]:
					pnum = self.p_nbr_num(cur)
					fnum,nnum = self.fileornet_nbr_num(cur)
					for nbr in cur_nbrs:
						w = self.getweight6(pprev,prev,cur,nbr,pnum,fnum,nnum,self.thre_w8)
						unnormalized_probs.append(w)
				elif cur == pprev:
					pnum = self.p_nbr_num(cur)
					fnum,nnum = self.fileornet_nbr_num(cur)
					for nbr in cur_nbrs:
						w = self.getweight7(prev,cur,nbr,pnum,fnum,nnum)
						unnormalized_probs.append(w)
				else:
					if self.pgraph.out_degree(cur) > 1:
						for nbr in cur_nbrs:
							w = self.getweight8(prev,cur,nbr,self.thre_w8)
							unnormalized_probs.append(w)
					else:
						pnum = self.p_nbr_num(cur)
						fnum,nnum = self.fileornet_nbr_num(cur)
						for nbr in cur_nbrs:
							w = self.getweight9(prev,cur,nbr,pnum,fnum,nnum,self.thre_w8)
							unnormalized_probs.append(w)
			else:
				for nbr in cur_nbrs:
					w = self.getweight10(prev,cur,nbr)
					unnormalized_probs.append(w)
					if prev == nbr:
						backlocal = len(unnormalized_probs) - 1
		
		if self.nodes[cur]['data_node'].__class__.__name__ != 'ProcessNode':
			unnormalized_probs = self.processweight(unnormalized_probs,backlocal,self.thre_w9)
		norm_const = sum(unnormalized_probs)
		normalized_probs = [float(u_prob)/norm_const for u_prob in unnormalized_probs]
		#print prev, cur
		#print cur_nbrs
		#print normalized_probs
		return AliasSimple.alias_setup(normalized_probs)

	def randomwalk(self, number_walks, walk_length, filename):
		print 'walking...'
		write_file = open('../detection_file/'+filename+'_specific2_walk.csv','w')
		walks = []
		nodes = self.graph.nodes()
		node_list = list(self.graph.nodes)
		for walk_iter in range(number_walks):
			random.shuffle(node_list)
			for node in node_list:
				if nodes[node]['data_node'].__class__.__name__ == 'ProcessNode':
					#print '+++++++++++++++++++++++++++++++++++'
					one_walk = self.walk(walk_length=walk_length, start_node=node)
					self.export_walks(one_walk, write_file)
					one_walk = self.removingfile(one_walk)
					one_walk = self.removingsysprocess(one_walk)
					walks.append(one_walk)
		return walks

	def walk(self, walk_length, start_node):
		self.counthistory = {}
		walk = [start_node]
		num = 0
		while len(walk) < walk_length:
			cur = walk[-1]
			#cur_nbrs = sorted(set(nx.all_neighbors(self.graph, cur)))
			num += 1
			#print str(num)+':'+cur+'start'
			cur_nbrs = list(set(nx.all_neighbors(self.graph, cur)))
			#print str(len(cur_nbrs))
			#print cur+'end'
			if len(cur_nbrs) > 0:
				if len(walk) == 1:
					probs = self.getstartprobs(cur, cur_nbrs)
					walk.append(cur_nbrs[AliasSimple.alias_draw(probs[0], probs[1])])
				else:
					prev = walk[-2]
					#if self.counthistory.has_key((prev,cur)):
					#	self.counthistory[(prev,cur)] += 1
					#else:
					#	self.counthistory[(prev,cur)] = 1
					#print '-----------------------'
					if self.nodes[prev]['data_node'].__class__.__name__ == 'ProcessNode':
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
		#walk = self.removingsysfile(walk)
		#walk = self.removingfile(walk[1:])
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
				negative = 5,
				iter=epoch, 
				batch_words=batch)
		return model
	
	def lda(self, walks, cluster_num, epoch, batch, filename, meth, issplit, ismergepath):
		print 'running lda...'
		dictionary = corpora.Dictionary(walks)
		corpus = [dictionary.doc2bow(words) for words in walks]
		node2id = dictionary.token2id
		lda_model = LdaModel(corpus=corpus, num_topics=cluster_num, iterations=epoch, update_every=batch)
		z = []
		for node in self.nodes:
			if self.nodes[node]['data_node'].unidname in Systemfile.sysfile:continue
			cluster_probability = lda_model.get_term_topics(node2id[node],minimum_probability=0.0)
			probs = []
			for i in cluster_probability:
				probs.append(i[1])
			z.append((node,probs))
		ExportResult.exportaffiliation(self.graph, z, filename, meth, issplit, ismergepath)

	'''
	def processneighbornum(self, node):
		num = 0
		nodes = self.graph.nodes()
		neighbors = sorted(set(nx.all_neighbors(self.graph, node)))
		for nbr in neighbors:
			if nodes[nbr]['data_node'].__class__.__name__ == 'ProcessNode':
				num += 1
		return num
	'''
	def in_neighbor(self, graph, node):
		in_node = []
		for i in list(graph.in_edges(node)):
			in_node.append(i[0])
		return in_node
	
	def p_nbr_num(self,pnode):
		pnum = len(set(self.pgraph.neighbors(pnode)))
		return pnum

	def fileornet_nbr_num(self,pnode):
		fnum = 0
		nnum = 0
		nbrs = set(nx.all_neighbors(self.graph, pnode))
		for nbr in nbrs:
			if self.nodes[nbr]['data_node'].__class__.__name__ == 'FileNode':
				fnum+=1
			elif self.nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode':
				nnum+=1
			elif self.nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode2':
				nnum+=1
		return fnum, nnum
	
	def removingsysfile(self, path):
		new_path = []
		for item in path:
			node = self.nodes[item]['data_node']
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
	
	def removingsysprocess(self, path):
		new_path = []
		for item in path:
			node = self.nodes[item]['data_node']
			if node.__class__.__name__ == 'ProcessNode':
				if node.unidname in Systemfile.sysprocess:
					continue
			new_path.append(item)
		return new_path

	def getrbo(self, prev, nbr):
		prev_list = self.processlink[prev]
		nbr_list = self.processlink[nbr]
		ld = len(prev_list) - len(nbr_list)
		if ld > 0:
			nbr_list = [nbr]*ld + nbr_list
			#if nbr in self.parents[prev]:
			#   return 1.0
			#else:
			#   nbr_list = [nbr]*ld + nbr_list
		elif ld < 0:
			prev_list = [prev]*abs(ld) + prev_list
			#if prev in self.parents[nbr]:
			#   return 1.0
			#else:
			#   prev_list = [prev]*abs(ld) + prev_list
		rbo = Rbo(prev_list, nbr_list, self.beta).rbo_ext
		return rbo

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
		walkspath = '../detection_file/'+filename+'_specific2_walk.csv'
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

