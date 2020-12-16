import networkx as nx
import decimal as de
import copy

class FileNodeSplit:

	def __init__(self, originalgraph):
		self.originalgraph = originalgraph

	def run(self):
		print 'spliting file node...'
		filenode_splited = self.eventcluster()
		path = '../core/intermediatefiles/split.csv'
		fw = open(path,'w')
		for nodeid in filenode_splited:
			if len(filenode_splited[nodeid]) > 1:
				self.split(fw, nodeid, filenode_splited[nodeid])
		return self.originalgraph

	def eventcluster(self):
		nodes = self.originalgraph.nodes()
		filenode_splited = {}
		for nodeid in nodes:
			node = nodes[nodeid]['data_node']
			if node.__class__.__name__ == 'FileNode':
				in_edges = set(self.originalgraph.in_edges(nodeid))
				out_edges = set(self.originalgraph.out_edges(nodeid))
				if len(in_edges) + len(out_edges) > 2:
					filenode_splited[nodeid] = []
					out_inevents = {}
					edges_clustered = set()
					for out_edgeid in out_edges:
						relatedinevents = self.getrelatedinevents(out_edgeid, in_edges)
						out_inevents[out_edgeid[1]] = relatedinevents
						for i in relatedinevents:
							edges_clustered.add(i)
					in_outevents = {}
					for out_neighborid in out_inevents:
						in_neighbors = []
						for inevent in out_inevents[out_neighborid]:
							in_neighbors.append(inevent[0])
						in_neighbors.sort()
						key = ':'.join(in_neighbors)
						if in_outevents.has_key(key):
							in_outevents[key].append((nodeid,out_neighborid))
						else:
							in_outevents[key] = [(nodeid,out_neighborid)]
					
					for k in in_outevents:
						in_outeventsdict = {}
						for outevent in in_outevents[k]:
							if in_outeventsdict.has_key('out'):
								in_outeventsdict['out'].add(outevent)
							else:
								in_outeventsdict['out'] = set([outevent])
							for ineventid in out_inevents[outevent[1]]:
								if in_outeventsdict.has_key('in'):
									in_outeventsdict['in'].add(ineventid)
								else:
									in_outeventsdict['in'] = set([ineventid])
						filenode_splited[nodeid].append(in_outeventsdict)
					edges_remained = in_edges - edges_clustered
					if edges_remained:
						assignededges = self.assigninedgesremained(edges_remained, edges_clustered)
						for assignedge, existedge in assignededges:
							for ci in filenode_splited[nodeid]:
								if existedge in ci['in']:
									ci['in'].add(assignedge)

		return filenode_splited

	def getrelatedinevents(self, out_edgeid, in_edges):
		relatedinevents = set()
		out_edge = self.originalgraph[out_edgeid[0]][out_edgeid[1]][0]['data_edge']
		starttime_out = out_edge.starttime
		endtime_out = out_edge.endtime
		starttimetemp = []
		inedgestemp = []
		for in_edgeid in in_edges:
			in_edge = self.originalgraph[in_edgeid[0]][in_edgeid[1]][0]['data_edge']
			starttime_in = in_edge.starttime
			endtime_in = in_edge.endtime
			if de.Decimal(starttime_in) < de.Decimal(starttime_out):
				starttimetemp.append(de.Decimal(starttime_in))
				inedgestemp.append(in_edgeid)
			if de.Decimal(endtime_in) < de.Decimal(starttime_out):
				starttimetemp.append(de.Decimal(endtime_in))
				inedgestemp.append(in_edgeid)
			if (de.Decimal(starttime_in) < de.Decimal(endtime_out)) and \
					(de.Decimal(endtime_in) > de.Decimal(endtime_out)):
				relatedinevents.add(in_edgeid)
			if (de.Decimal(starttime_in) > de.Decimal(starttime_out)) and \
					(de.Decimal(endtime_in) < de.Decimal(endtime_out)):
				relatedinevents.add(in_edgeid)
		if starttimetemp:
			relatedinevents.add(inedgestemp[starttimetemp.index(max(starttimetemp))])
		return list(relatedinevents)

	def assigninedgesremained(self, edges_remained, edges_clustered):
		assignedtuple = []
		for edges_remainedid in edges_remained:
			edge_remained = self.originalgraph[edges_remainedid[0]][edges_remainedid[1]][0]['data_edge']
			endtime_edge_remained = edge_remained.endtime
			endtimetemp = []
			edgestemp = []
			for edges_clusteredid in edges_clustered:
				edge_clustered = self.originalgraph[edges_clusteredid[0]][edges_clusteredid[1]][0]['data_edge']
				endtime_edge_clustered = edge_clustered.endtime
				if de.Decimal(endtime_edge_clustered) > de.Decimal(endtime_edge_remained):
					endtimetemp.append(de.Decimal(endtime_edge_clustered))
					edgestemp.append(edges_clusteredid)
			if endtimetemp:
				edge_relaved = edgestemp[endtimetemp.index(max(endtimetemp))]
			assignedtuple.append((edges_remainedid,edge_relaved))
		return assignedtuple

	def split(self, fw, nodeid, clusters):
		nodes = self.originalgraph.nodes()
		node = nodes[nodeid]['data_node']
		fw.write(nodeid+','+node.filename)
		n = 0
		for ci in clusters:
			n += 1
			cnodeid = nodeid + '_' + str(n)
			cnode = copy.deepcopy(node)
			cnode.unid = cnodeid
			suffix = []
			for s in ci['in']:
				ss = nodes[s[0]]['data_node'].pidname+nodes[s[0]]['data_node'].pid
				suffix.append(ss)
			suffix.sort()
			st = ''
			for su in suffix:
				st += su
			cnode.filename = node.filename+'_'+st
			fw.write(','+str(n)+':'+st)
			self.originalgraph.add_node(cnodeid, data_node = cnode)
			for in_edge in ci['in']:
				cin_edge = copy.deepcopy(self.originalgraph[in_edge[0]][in_edge[1]][0]['data_edge'])
				cin_edge.sinkF = cnode
				self.originalgraph.add_edge(in_edge[0], cnodeid, data_edge=cin_edge)
			for out_edge in ci['out']:
				cout_edge = copy.deepcopy(self.originalgraph[out_edge[0]][out_edge[1]][0]['data_edge'])
				cout_edge.sourceF = cnode
				self.originalgraph.add_edge(cnodeid, out_edge[1], data_edge=cout_edge)
		self.originalgraph.remove_node(nodeid)
		fw.write('\n')


