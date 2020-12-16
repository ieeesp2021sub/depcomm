import networkx as nx
import decimal as de

class Mergeedge:
	
	def __init__(self, backtrack):
		self.backtrack = backtrack

	def mergeEdgeDiffWindow(self, window):
		print "Merging..."
		mergegraph = nx.MultiDiGraph()
		
		nodes = self.backtrack.nodes()
		for node_id in nodes:
			mergegraph.add_node(node_id, data_node=nodes[node_id]['data_node'])
		
		edgelist = self.backtrack.edges.items()
		#print edgelist

		def cmp(x, y):
			x_edge = x[1]['data_edge']
			y_edge = y[1]['data_edge']
			if de.Decimal(x_edge.starttime) == de.Decimal(y_edge.starttime):
				return int(de.Decimal(x_edge.endtime).compare(de.Decimal(y_edge.endtime)).to_eng_string())
			return int(de.Decimal(x_edge.starttime).compare(de.Decimal(y_edge.starttime)).to_eng_string())

		edgelist_sorted = sorted(edgelist, cmp)

		edgestacks = self.initializeEdgestack(edgelist)
		#print edgestacks

		for item in edgelist_sorted:
			source = item[0][0]
			sink = item[0][1]
			edge = item[1]['data_edge']
			stack = edgestacks[edge.event][source][sink]
			#if nodes[source]['data_node'].__class__.__name__ == 'FileNode' and nodes[sink]['data_node'].__class__.__name__ == 'ProcessNode':
			#	if nodes[source]['data_node'].filename == '/tmp/ccJoB2zx.s' and nodes[sink]['data_node'].pid == '9675':
			#		print str(edge.size)
			if len(stack) == 0:
				stack.append(edge)
			else:
				edge_pre = stack.pop()
				diff_time = de.Decimal(edge.starttime) - de.Decimal(edge_pre.endtime)
				if diff_time <= de.Decimal(window):
					edge_merged = self.merge(edge_pre, edge)
					stack.append(edge_merged)
				else:
					stack.append(edge_pre)
					stack.append(edge)

		for e in edgestacks:
			for s in edgestacks[e]:
				for t in edgestacks[e][s]:
					st = edgestacks[e][s][t]
					for i in st:
						mergegraph.add_edge(s, t, data_edge=i)

		print 'merge is over'
		return mergegraph

	def initializeEdgestack(self, edgelist):
		
		edgestacks = {}
		for items in edgelist:
			event = items[1]['data_edge'].event
			source = items[0][0]
			sink = items[0][1]
			if edgestacks.has_key(event):
				if edgestacks[event].has_key(source):
					if edgestacks[event][source].has_key(sink):
						continue
					else:
						edgestacks[event][source][sink] = []
				else:
					edgestacks[event][source] = {}
					edgestacks[event][source][sink] = [] 
			else:
				edgestacks[event] = {}
				edgestacks[event][source] = {}
				edgestacks[event][source][sink] = []
				
		return edgestacks

	def merge(self, edge_pre, edge):
		if edge_pre.__class__.__name__ != 'PtoPEvent':
			if edge_pre.endtime == edge.endtime:
				tmp = 0.0
			else:
				tmp = edge.size
			edge_pre.size += tmp
		edge_pre.setEndtime(edge.endtime)
		return edge_pre
		





