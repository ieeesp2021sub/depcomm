from ImportGraph import ImportGraph
from Backtrack import Backtrack
from Mergeedge import Mergeedge
from Rwgraph import Rwgraph
from Noleafgraph import Noleafgraph
from Mergenode import Mergenode
from FileNodeSplit import FileNodeSplit
from ExportDOT import ExportDOT
from networkx.drawing.nx_pydot import write_dot,read_dot
from FindNode import FindNode
from Community import Community
import pympler.asizeof as sf
from time import time
from utils.Graph2Json import graph2json, json2graph
from utils.Indexfile import indexfile
from utils.Process2file import process2file
import os

class Process:
	
	def __init__(self, inpath, detection, outpath):
		self.inpath = inpath
		self.outpath = outpath
		self.detection = detection

	def run(self,
			isfromjson,
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
			batch):
		
		filename = self.inpath.split('/')[-1]
		filename = filename.split('.')[0]

		if not isfromjson:
			statefile = open(self.outpath+filename+'_states.txt','w')

			#----generating an original graph-----
			start_time = time()
			ig = ImportGraph(self.inpath)
			ig.generateGraph(False,False)
			graph = ig.graph
			end_time = time()
			#memory = sf.asizeof(graph)/1024./1024.
			statefile.write('Run time for original graph is: '+str(end_time-start_time)+'\n')
			#statefile.write('memory space for original graph is: '+str(memory)+'MB'+'\n')
			statefile.write('Original node number: '+str(graph.number_of_nodes())+'\n')
			statefile.write('Original edge number: '+str(graph.number_of_edges())+'\n')
			statefile.write('------------------------------------'+'\n')

			#----generating a graph based on the detection POI
			start_time = time()
			bg = Backtrack(graph)
			backgraph = bg.getBackgraph(self.detection)
			end_time = time()
			#memory = sf.asizeof(backgraph)/1024./1024.
			statefile.write('Run time for backtrack graph is: '+str(end_time-start_time)+'\n')
			#statefile.write('memory space for backtrack graph is: '+str(memory)+'MB'+'\n')
			statefile.write('Backtrack graph node number: '+str(backgraph.number_of_nodes())+'\n')
			statefile.write('Backtrack graph edge number: '+str(backgraph.number_of_edges())+'\n')
			statefile.write('------------------------------------'+'\n')


			#----generating a graph merging edges for backtrack graph
			start_time = time()
			mg = Mergeedge(backgraph)
			mergegraph = mg.mergeEdgeDiffWindow(86400)
			end_time = time()
			memory = sf.asizeof(mergegraph)/1024./1024.
			statefile.write('Run time for merged graph of backtrack graph is: '+str(end_time-start_time)+'\n')
			statefile.write('memory space for merged graph of backtrack graph is: '+str(memory)+'MB'+'\n')
			statefile.write('Merged graph node number of backtrack graph: '+str(mergegraph.number_of_nodes())+'\n')
			statefile.write('Merged graph edge number of backtrack graph: '+str(mergegraph.number_of_edges())+'\n')
			statefile.write('------------------------------------'+'\n')


			#----generating a graph with only read-write file node
			start_time = time()
			rwg = Rwgraph(mergegraph)
			rwgraph = rwg.getRwgraph()
			end_time = time()
			memory = sf.asizeof(rwgraph)/1024./1024.
			statefile.write('Run time for read-write graph of merged graph is: '+str(end_time-start_time)+'\n')
			statefile.write('memory space for read-write graph of merged graph is: '+str(memory)+'MB'+'\n')
			statefile.write('Read-write graph node number of merged graph: '+str(rwgraph.number_of_nodes())+'\n')
			statefile.write('Read-write graph edge number of merged graph: '+str(rwgraph.number_of_edges())+'\n')
			statefile.close()
			#ex = ExportDOT(rwgraph)
			#ex.export(self.outpath+filename+'_AfterMergeforback.dot')
		
			#Importing to json                                                                                                                           
			graph2json(rwgraph,filename)
		
		else:
			print 'geting graph from file'
			rwgraph = json2graph(filename)
		
		indexfile(rwgraph)
		nof = Noleafgraph(rwgraph)
		noleafgraph, _, _ = nof.getNoleafgraph()

		process2file(noleafgraph, './core/intermediatefiles/process2file.txt')
		
		#----community detection
		cd = Community(
				graph = noleafgraph,
				is_walks = is_walks,
				is_generatevector = is_generatevector,
				meth = meth,
				vector_or_lda = vector_or_lda,
				number_walks = number_walks,
				walk_length = walk_length,
				window_size = window_size,
				embedding_size = embedding_size,
				sg = sg,
				hs = hs,
				epoch = epoch,
				batch = batch,
				filename = filename,
				outpath = self.outpath)

		comm2node = cd.detection()

		#----community compression
		mergednode = Mergenode(noleafgraph,self.detection)
		mergenodegraph = mergednode.getMergedgraph(comm2node,filename,meth)

