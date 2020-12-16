from Parser import Parser
import networkx as nx

class ImportGraph:
	
	def __init__(self, pathlog):
		self.pathlog = pathlog
		self.graph = nx.MultiDiGraph()

	def generateGraph(self, onlydesIP, process_bidirection):
		parser = Parser(self.pathlog)
		parser.parseLog(onlydesIP,process_bidirection)
		
		print "Generating original graph"
		PtoPDict = parser.PtoPDict
		PtoFDict = parser.PtoFDict
		FtoPDict = parser.FtoPDict
		PtoNDict = parser.PtoNDict
		NtoPDict = parser.NtoPDict

		self.addPtoP(PtoPDict)
		self.addPtoF(PtoFDict)
		self.addFtoP(FtoPDict)
		self.addPtoN(PtoNDict)
		self.addNtoP(NtoPDict)
		print "ending original graph Generation"

	def addPtoP(self, PtoPDict):
		for key in PtoPDict:
			source = PtoPDict[key].sourceP
			sink = PtoPDict[key].sinkP
			edge = PtoPDict[key]
			
			source_unid = source.unid
			sink_unid = sink.unid

			self.graph.add_node(source_unid,
							data_node = source)

			self.graph.add_node(sink_unid,
							data_node = sink)

			self.graph.add_edge(source_unid,
							sink_unid,
							data_edge = edge)


	def addPtoF(self, PtoFDict):
		for key in PtoFDict:
			source = PtoFDict[key].sourceP
			sink = PtoFDict[key].sinkF
			edge = PtoFDict[key]

			source_unid = source.unid
			sink_unid = sink.unid

			self.graph.add_node(source_unid,
							data_node = source)

			self.graph.add_node(sink_unid,
							data_node = sink)

			self.graph.add_edge(source_unid,
							sink_unid,
							data_edge = edge)

	def addFtoP(self, FtoPDict):
		for key in FtoPDict:
			source = FtoPDict[key].sourceF
			sink = FtoPDict[key].sinkP
			edge = FtoPDict[key]

			source_unid = source.unid
			sink_unid = sink.unid

			self.graph.add_node(source_unid,
							data_node = source)

			self.graph.add_node(sink_unid,
							data_node = sink)

			self.graph.add_edge(source_unid,
							sink_unid,
							data_edge = edge)
	
	def addPtoN(self, PtoNDict):
		for key in PtoNDict:
			source = PtoNDict[key].sourceP
			sink = PtoNDict[key].sinkN
			edge = PtoNDict[key]

			source_unid = source.unid
			sink_unid = sink.unid

			self.graph.add_node(source_unid,
							data_node = source)
					
			self.graph.add_node(sink_unid,
							data_node = sink)

			self.graph.add_edge(source_unid,
							sink_unid,
							data_edge = edge)

	def addNtoP(self, NtoPDict):
		for key in NtoPDict:
			source = NtoPDict[key].sourceN
			sink = NtoPDict[key].sinkP
			edge = NtoPDict[key]

			source_unid = source.unid
			sink_unid = sink.unid

			self.graph.add_node(source_unid,
							data_node = source)

			self.graph.add_node(sink_unid,
							data_node = sink)

			self.graph.add_edge(source_unid,
							sink_unid,
							data_edge = edge)

