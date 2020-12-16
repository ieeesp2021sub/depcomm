import random
from time import time
from communities.Deepwalk import Deepwalk
from communities.Node2vec import Node2vec
from communities.Specific import Specific
from communities.Specific2 import Specific2
from communities.Kclique import Kclique
from communities.Lais2 import Lais2
from communities.Congo import Congo
from communities.Fcm import FCM
from communities.HLC import HLC
from communities.SLPA import SLPA
from communities.Linepartition import Linepartition
from communities.Fuzzycom import Fuzzycom
from communities.MNMF import MNMF
from communities.DANMF import DANMF
from communities.EgoNetSplitter import EgoNetSplitter
from communities.PercoMCV import PercoMCV
from communities.Louvain import Louvain
from communities.LineBlackHole import LineBlackHole
from communities.NISE import NISE
from utils.Cmeans import Cmeans


class Community:

	def __init__(
			self, 
			graph,
			is_walks,
			is_generatevector,
			meth, 
			vector_or_lda, 
			number_walks, 
			walk_length,
			window_size,
			embedding_size,
			sg,
			hs,
			epoch,
			batch,
			filename,
			outpath):
		self.graph = graph
		self.is_generatevector = is_generatevector
		self.is_walks = is_walks
		self.meth = meth
		self.vector_or_lda = vector_or_lda
		self.number_walks = number_walks
		self.walk_length = walk_length
		self.window_size = window_size
		self.embedding_size = embedding_size
		self.sg = sg
		self.hs = hs
		self.epoch = epoch
		self.batch = batch
		self.filename = filename
		self.outpath = outpath

	def detection(self):
		print 'community detecting...'
		#deepwalk
		if self.meth == 'deepwalk':
			dw = Deepwalk(self.graph)
			if self.is_walks:
				walks = dw.randomwalk(
						number_walks=self.number_walks, 
						walk_length=self.walk_length, 
						alpha=0, 
						rand=random.Random(0), 
						filename=self.filename)
			else:
				walks = dw.walks_from_file(self.filename)
			if self.vector_or_lda == 'vector':
				if self.is_generatevector:
					model = dw.to_vector(
							walks = walks, 
							window_size = self.window_size, 
							embedding_size = self.embedding_size, 
							sg = self.sg, 
							hs = self.hs, 
							epoch = self.epoch, 
							batch = self.batch)
					model.wv.save_word2vec_format('./detection_file/'+self.filename+'_deepwalk_vector.csv')
				c = 3
				fpcs = []
				while True:
					_,fpc = Cmeans.cluster(
							filename=self.filename, 
							meth=self.meth, 
							c=c, 
							graph=self.graph)
					c += 1
					fpcs.append(fpc)
					if fpc < max(fpcs):
						break
				comm2node,_ = Cmeans.cluster(
						filename=self.filename, 
						meth=self.meth, 
						c=c-2, 
						graph=self.graph)
				return comm2node

			elif self.vector_or_lda == 'lda':
				dw.lda(
						walks = walks,
						cluster_num = self.cluster_num,
						epoch = self.epoch,
						batch = self.batch,
						filename = self.filename,
						meth = self.meth)

		elif self.meth == 'node2vec':
			n2v = Node2vec(self.graph, self.direct, 1.0, 0.2)
			if self.is_walks:
				n2v.preprocess_transition_probs()
				walks = n2v.randomwalk(
						number_walks=self.number_walks,
						walk_length=self.walk_length,
						filename=self.filename)
			else:
				walks = n2v.walks_from_file(self.filename)
			if self.vector_or_lda == 'vector':
				if self.is_generatevector:
					model = n2v.to_vector(
							walks = walks, 
							window_size = self.window_size, 
							embedding_size = self.embedding_size, 
							sg = self.sg, 
							hs = self.hs, 
							epoch = self.epoch, 
							batch = self.batch)
					model.wv.save_word2vec_format('./detection_file/'+self.filename+'_node2vec_vector.csv')
				c = 3
				fpcs = []
				while True:
					_,fpc = Cmeans.cluster(
							filename=self.filename, 
							meth=self.meth, 
							c=c, 
							graph=self.graph)
					c += 1
					fpcs.append(fpc)
					if fpc < max(fpcs):
						break
				comm2node,_ = Cmeans.cluster(
						filename=self.filename, 
						meth=self.meth, 
						c=c-2, 
						graph=self.graph)
				return comm2node

			elif self.vector_or_lda == 'lda':
				n2v.lda(
						walks = walks,
						cluster_num = self.cluster_num,
						epoch = self.epoch,
						batch = self.batch,
						filename = self.filename,
						meth = self.meth)

		elif self.meth == 'HRW':
			#statefile = open(self.outpath+self.filename+'_states.txt','a')
			spe2 = Specific2(self.graph)
			start_time = time()
			if self.is_walks:
				spe2.getProcesslink2()
				spe2.getParent()
				spe2.getR()
				walks = spe2.randomwalk(
					number_walks=self.number_walks,
					walk_length = self.walk_length,
					filename=self.filename)
			else:
				walks = spe2.walks_from_file(self.filename)
			if self.vector_or_lda == 'vector':
				start_time = time()
				if self.is_generatevector:
					model = spe2.to_vector(
						walks = walks, 
						window_size = self.window_size, 
						embedding_size = self.embedding_size, 
						sg = self.sg, 
						hs = self.hs, 
						epoch = self.epoch, 
						batch = self.batch)
					model.wv.save_word2vec_format('./detection_file/'+self.filename+'_HRW_vector.csv')
				c = 3
				fpcs = []
				while True:
					_,fpc = Cmeans.cluster(
							filename=self.filename, 
							meth=self.meth, 
							c=c, 
							graph=self.graph)
					fpcs.append(fpc)
					if fpc < max(fpcs):
						break
					c+=1
				comm2node,_ = Cmeans.cluster(
						filename=self.filename, 
						meth=self.meth, 
						c=c-2, 
						graph=self.graph)

				return comm2node	
			elif self.vector_or_lda == 'lda':
				spe2.lda(
						walks = walks,
						cluster_num = self.cluster_num,
						epoch = self.epoch,
						batch = self.batch,
						filename = self.filename,
						meth = self.meth)

		elif self.meth == 'kclique':
			kcq = Kclique(self.graph, k=3)
			kcq.getc(self.filename, self.meth, self.issplit, self.ismergepath)

		elif self.meth == 'lais2':
			lais2 = Lais2(self.graph)
			lais2.Lais2(self.filename, self.meth, self.issplit, self.ismergepath)

		#elif self.meth == 'congo':
		#	cgo = Congo(self.graph, self.cluster_num, 3)
		#	cgo.congo(self.graph,self.filename,self.meth,self.issplit, self.ismergepath)

		#elif self.meth == 'fcm':
		#	fcm = FCM(self.graph, self.cluster_num, 5)
		#	fcm.fcm(self.filename, self.meth, self.issplit, self.ismergepath)

		elif self.meth == 'hlc':
			hlc = HLC(self.graph)
			hlc.hlc(threshold=None, 
					w=None, 
					dendro_flag=False, 
					filename=self.filename, 
					meth=self.meth, 
					issplit=self.issplit,
					ismergepath=self.ismergepath)
		
		elif self.meth == 'slpa':
			slpa = SLPA(self.graph, 100, 0.2)
			slpa.slpa(self.filename, self.meth, self.issplit, self.ismergepath)

		elif self.meth == 'linepartition':
			lp = Linepartition(self.graph, is_weight=False)
			lp.linepar(self.filename, self.meth, self.issplit, self.ismergepath)
		
		elif self.meth == 'fuzzycom':
			fuzc = Fuzzycom(self.graph, 0.2, 0.1, 3)
			fuzc.fuzzy_comm(self.filename, self.meth, self.issplit, self.ismergepath)

		#elif self.meth == 'mnmf':
		#	model = MNMF(dimensions=self.embedding_size, clusters=self.cluster_num)
		#	model.fit(self.graph)
		#	model.get_memberships(self.filename, self.meth, self.issplit, self.ismergepath)

		elif self.meth == 'danmf':
			model = DANMF()
			model.fit(self.graph)
			model.get_memberships(self.filename, self.meth, self.issplit, self.ismergepath)
		
		elif self.meth == 'egonetsplitter':
			model = EgoNetSplitter(resolution=1.0)
			model.fit(self.graph)
			model.get_memberships(self.filename, self.meth, self.issplit, self.ismergepath)

		elif self.meth == 'percomcv':
			pmcv = PercoMCV(self.graph)
			pmcv.percoMVC(self.filename, self.meth, self.issplit, self.ismergepath)

		elif self.meth == 'louvain':
			louvain = Louvain(self.graph)
			louvain.apply_method(self.filename, self.meth, self.issplit, self.ismergepath)
		
		#elif self.meth == 'lineblackhole':
		#	lbh = LineBlackHole(
		#			graph=self.graph,
		#			number_walks=self.number_walks,
		#			walk_length=self.walk_length,
		#			window_size=self.window_size,
		#			embedding_size=self.embedding_size,
		#			cluster_num=self.cluster_num,
		#			direct=self.direct,
		#			sg=self.sg,
		#			hs=self.hs,
		#			epoch=self.epoch,
		#			batch=self.batch)
		#	lbh.lineblackhole(self.filename, self.meth, self.issplit, self.ismergepath)
		
		elif self.meth == 'nise':
			nise = NISE(
					graph=self.graph,
					seed_num=6,
					ninf=False,
					expansion='ppr',
					stopping='cond',
					nworkers=1,
					nruns=13,
					alpha=0.99,
					maxexpand=float('INF'),
					delta=0.2)
			nise.nise(self.filename, self.meth, self.issplit, self.ismergepath)

		else:
			raise Exception('This method is non-existent')

