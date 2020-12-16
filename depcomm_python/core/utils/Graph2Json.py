import networkx as nx
import sys
sys.path.append("..")
from ProcessNode import ProcessNode
from FileNode import FileNode
from NetworkNode import NetworkNode
from NetworkNode2 import NetworkNode2
from PtoPEvent import PtoPEvent
from PtoFEvent import PtoFEvent
from FtoPEvent import FtoPEvent
from PtoNEvent import PtoNEvent
from NtoPEvent import NtoPEvent
import ast

path = './outgraph/'

def graph2json(graph, filename):
	text_node = open(path+filename+'_nodes.json','w')
	text_edge = open(path+filename+'_edges.json','w')
	js_node = {}
	js_edge = {}
	nodes = graph.nodes()
	for node in nodes:
		if js_node.has_key(node):continue
		js_node[node] = {}
		nodein = nodes[node]['data_node']
		if nodein.__class__.__name__ == 'ProcessNode':
			js_node[node]['unid'] = nodein.unid
			js_node[node]['pid'] = nodein.pid
			js_node[node]['pidname'] = nodein.pidname
			js_node[node]['nodetype'] = nodein.nodetype
			js_node[node]['merged'] = nodein.merged
			js_node[node]['argus'] = nodein.argus
			js_node[node]['unidname'] = nodein.unidname
		elif nodein.__class__.__name__ == 'FileNode':
			js_node[node]['unid'] = nodein.unid
			js_node[node]['filename'] = nodein.filename
			js_node[node]['nodetype'] = nodein.nodetype
			js_node[node]['merged'] = nodein.merged
			js_node[node]['unidname'] = nodein.unidname
			js_node[node]['name'] = nodein.name
			js_node[node]['path'] = nodein.path
			js_node[node]['extension'] = nodein.extension
		elif nodein.__class__.__name__ == 'NetworkNode':
			js_node[node]['unid'] = nodein.unid
			js_node[node]['sourceIP'] = nodein.sourceIP
			js_node[node]['sourcePort'] = nodein.sourcePort
			js_node[node]['desIP'] = nodein.desIP
			js_node[node]['desPort'] = nodein.desPort
			js_node[node]['nodetype'] = nodein.nodetype
			js_node[node]['merged'] = nodein.merged
			js_node[node]['unidname'] = nodein.unidname
		elif nodein.__class__.__name__ == 'NetworkNode2':
			js_node[node]['unid'] = nodein.unid
			js_node[node]['desIP'] = nodein.desIP
			js_node[node]['desPort'] = nodein.desPort
			js_node[node]['nodetype'] = nodein.nodetype
			js_node[node]['merged'] = nodein.merged
			js_node[node]['unidname'] = nodein.unidname

	text_node.write(str(js_node))

	edges = graph.edges()
	for (src,sink) in edges:
		for i in graph[src][sink]:
			edge = (src,sink,i)
			if js_edge.has_key(edge):continue
			js_edge[edge]={}
			edgein = graph[src][sink][i]['data_edge']
			if edgein.__class__.__name__ == 'PtoPEvent':
				js_edge[edge]['starttime'] = edgein.starttime
				js_edge[edge]['endtime'] = edgein.endtime
				js_edge[edge]['event'] = edgein.event
				js_edge[edge]['size'] = edgein.size
				js_edge[edge]['eventtype'] = edgein.eventtype
				js_edge[edge]['merged'] = edgein.merged
				js_edge[edge]['direct'] = edgein.direct
			else:
				js_edge[edge]['starttime'] = edgein.starttime
				js_edge[edge]['endtime'] = edgein.endtime
				js_edge[edge]['event'] = edgein.event
				js_edge[edge]['size'] = edgein.size
				js_edge[edge]['eventtype'] = edgein.eventtype
				js_edge[edge]['merged'] = edgein.merged

	text_edge.write(str(js_edge))


def json2graph(filename):
	graph = nx.MultiDiGraph()
	text_node = open(path+filename+'_nodes.json')
	text_edge = open(path+filename+'_edges.json')
	line_node = text_node.readline()
	line_node = line_node.rstrip()
	nodein_dict = {}
	js_nodes = ast.literal_eval(line_node)
	for node in js_nodes:
		if js_nodes[node]['nodetype'] == 'process':
			unid = js_nodes[node]['unid']
			pid = js_nodes[node]['pid']
			pidname = js_nodes[node]['pidname']
			merged = js_nodes[node]['merged']
			argus = js_nodes[node]['argus']
			unidname = js_nodes[node]['unidname']
			processin = ProcessNode(unid, pid, pidname)
			processin.merged = merged
			processin.argus = argus
			processin.unidname = unidname
			nodein_dict[node] = processin
		elif js_nodes[node]['nodetype'] == 'file':
			unid = js_nodes[node]['unid']
			filename = repr(js_nodes[node]['filename'])[1:-1]
			merged = js_nodes[node]['merged']
			unidname = repr(js_nodes[node]['unidname'])[1:-1]
			name = js_nodes[node]['name']
			fpath = repr(js_nodes[node]['path'])[1:-1]
			extension = js_nodes[node]['extension']
			filein = FileNode(unid,filename)
			filein.merged = merged
			filein.unidname = unidname
			filein.name = name
			filein.path = fpath
			filein.extension = extension
			nodein_dict[node] = filein
		elif js_nodes[node]['nodetype'] == 'network':
			unid = js_nodes[node]['unid']
			sourceIP = js_nodes[node]['sourceIP']
			sourcePort = js_nodes[node]['sourcePort']
			desIP = js_nodes[node]['desIP']
			desPort = js_nodes[node]['desPort']
			merged = js_nodes[node]['merged']
			unidname = js_nodes[node]['unidname']
			networkin = NetworkNode(unid, sourceIP, sourcePort, desIP, desPort)
			networkin.merged = merged
			networkin.unidname = unidname
			nodein_dict[node] = networkin
		elif js_nodes[node]['nodetype'] == 'network2':
			unid = js_nodes[node]['unid']
			desIP = js_nodes[node]['desIP']
			desPort = js_nodes[node]['desPort']
			merged = js_nodes[node]['merged']
			unidname = js_nodes[node]['unidname']
			network2in = NetworkNode2(unid, desIP, desPort)
			network2in.merged = merged
			network2in.unidname = unidname
			nodein_dict[node] = network2in
		
	line_edge = text_edge.readline()
	line_edge = line_edge.rstrip()
	edgein_dict = {}
	js_edges = ast.literal_eval(line_edge)
	for edge in js_edges:
		srcnode = edge[0]
		sinknode = edge[1]
		starttime = js_edges[edge]['starttime']
		endtime = js_edges[edge]['endtime']
		event = js_edges[edge]['event']
		size = js_edges[edge]['size']
		merged = js_edges[edge]['merged']
		eventtype = js_edges[edge]['eventtype']
		if eventtype == 'PtoP':
			direct = js_edges[edge]['direct']
			sourceP = nodein_dict[srcnode]
			sinkP = nodein_dict[sinknode]
			PtoPin = PtoPEvent(sourceP, sinkP, starttime, event)
			PtoPin.endtime = endtime
			PtoPin.merged = merged
			PtoPin.direct = direct
			edgein_dict[edge] = PtoPin
		elif eventtype == 'PtoF':
			sourceP = nodein_dict[srcnode]
			sinkF = nodein_dict[sinknode]
			PtoFin = PtoFEvent(sourceP,sinkF,starttime,size,event)
			PtoFin.endtime = endtime
			PtoFin.merged = merged
			edgein_dict[edge] = PtoFin
		elif eventtype == 'FtoP':
			sourceF = nodein_dict[srcnode]
			sinkP = nodein_dict[sinknode]
			FtoPin = FtoPEvent(sourceF,sinkP,starttime,size,event)
			FtoPin.endtime = endtime
			FtoPin.merged = merged
			edgein_dict[edge] = FtoPin
		elif eventtype == 'PtoN':
			sourceP = nodein_dict[srcnode]
			sinkN = nodein_dict[sinknode]
			PtoNin = PtoNEvent(sourceP,sinkN,starttime,size,event)
			PtoNin.endtime = endtime
			PtoNin.merged = merged
			edgein_dict[edge] = PtoNin
		elif eventtype == 'NtoP':
			sourceN = nodein_dict[srcnode]
			sinkP = nodein_dict[sinknode]
			NtoPin = NtoPEvent(sourceN,sinkP,starttime,size,event)
			NtoPin.endtime = endtime
			NtoPin.merged = merged
			edgein_dict[edge] = NtoPin
		
	for node in nodein_dict:
		graph.add_node(node, data_node=nodein_dict[node])

	for edge in edgein_dict:
		graph.add_edge(edge[0],edge[1],data_edge=edgein_dict[edge])

	return graph
