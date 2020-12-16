import networkx as nx
import re
import decimal as de
from Queue import Queue

class Backtrack:

	def __init__(self, originalgraph):
		self.originalgraph = originalgraph


	def getBackgraph(self, detection):
		print "Backtracking..."
		backgraph = nx.MultiDiGraph()
		start = self.getGraphnode(detection)
		if start == None: return
		timethre = self.getLargestendtime(start)
		if timethre == None: return
		timethredict = {}
		if not timethredict.has_key(start):
			timethredict[start] = timethre
		backnodelist = set()
		backnodelist.add(start)
		backedgelist = set()
		q = Queue()
		q.put(start)
		while not q.empty():
			node = q.get()
			backgraph.add_node(node, data_node=self.originalgraph.nodes()[node]['data_node'])
			if timethredict.has_key(node):
				curthre = timethredict[node]
				#print 'curthre'+node+':'+curthre
				#print '+++++++++++++++++++++++++'
			in_edges = set()
			for (source, sink) in self.originalgraph.in_edges(node):
				in_edges.add((source, sink))
			for (source, sink) in in_edges:
				for i in self.originalgraph[source][sink]:
					edge = self.originalgraph[source][sink][i]['data_edge']
					#print source+'->'+sink+':'+edge.starttime+str(de.Decimal(edge.starttime) < de.Decimal(curthre))
					if de.Decimal(edge.starttime) < de.Decimal(curthre):
						backgraph.add_node(source, data_node=self.originalgraph.nodes()[source]['data_node'])
						backgraph.add_edge(source, sink, data_edge=edge)
						if not timethredict.has_key(source):				
							timethredict[source] = '0'
						curthreforsource = edge.endtime if de.Decimal(edge.endtime) < de.Decimal(curthre) else curthre
						#print '+++++  '+source+':'+timethredict[source]+'  '+edge.endtime+':'+curthre
						#print '+++++  '+str(de.Decimal(timethredict[source]) < de.Decimal(curthreforsource))
						if de.Decimal(timethredict[source]) < de.Decimal(curthreforsource):
							timethredict[source] = curthreforsource
							#print '++++++source'+source+':'+curthreforsource
						edgekey = source+':'+sink+':'+edge.event
						
						''
						if (source not in backnodelist) or (edgekey not in backedgelist):
							if source not in backnodelist:
								backnodelist.add(source)
							if edgekey not in backedgelist:
								backedgelist.add(edgekey)
							q.put(source)
						''
						#if source not in backnodelist:
						#	backnodelist.add(source)
						#	q.put(source)
						''
						#else:
						#	print source+' skip'
		print 'backtrack is over'	
		return backgraph

	def getGraphnode(self, detection):
		pPattern = re.compile(r'(?P<pidname>.+?)'+'\((?P<pid>\d+)\)')
		#fPattern = re.compile(r'(?P<filename>.+)')
		fPattern = re.compile(r'(?P<filename>/.+)')
		nPattern = re.compile(r'(?P<sourceIP>\d+\.\d+\.\d+\.\d+):(?P<sourcePort>\d+)->(?P<desIP>\d+\.\d+\.\d+\.\d+):(?P<desPort>\d+)')
		nPattern1 = re.compile(r'(?P<desIP>\d+\.\d+\.\d+\.\d+):(?P<desPort>\d+)')

		p_match = pPattern.match(detection)
		f_match = fPattern.match(detection)
		n_match = nPattern.match(detection)
		n_match1 = nPattern1.match(detection)
		
		nodes = self.originalgraph.nodes()
		if p_match:
			for node_id in nodes:
				node = nodes[node_id]['data_node']
				if node.__class__.__name__ == 'ProcessNode':
					pidname = node.pidname
					#print pidname
					pid = node.pid
					if (pidname == p_match.group('pidname') and pid == p_match.group('pid')):
						return node_id
			print detection+' is not in the dependent graph'
			print 'Backtrack is broken'
			return None

		elif f_match:
			for node_id in nodes:
				node = nodes[node_id]['data_node']
				if node.__class__.__name__ == 'FileNode':
					filename = node.filename
					#print filename
					if filename == f_match.group('filename'):
						return node_id
			print detection+' is not in the dependent graph'
			print 'Backtrack is broken'
			return None

		elif n_match:
			for node_id in nodes:
				node = nodes[node_id]['data_node']
				if node.__class__.__name__ == 'NetworkNode':
					sourceIP = node.sourceIP
					sourcePort = node.sourcePort
					desIP = node.desIP
					desPort = node.desPort
					if (sourceIP == n_match.group('sourceIP') and sourcePort == n_match.group('sourcePort')
									and desIP == n_match.group('desIP') and desPort == n_match.group('desPort')):
						return node_id
			print detection+' is not in the dependent graph'
			print 'Backtrack is broken'
			return None

		elif n_match1:
			for node_id in nodes:
				node = nodes[node_id]['data_node']
				if node.__class__.__name__ == 'NetworkNode2':
					desIP = node.desIP
					desPort = node.desPort
					if (desIP == n_match1.group('desIP') and desPort == n_match1.group('desPort')):
						return node_id

			print detection+' is not in the dependent graph'
			print 'Backtrack is broken'
			return None

		
		else:
			print detection+' is not a standard input detection point'
			print 'Backtrack is broken'
			return None


	def getLargestendtime(self, node):
		curtime = de.Decimal(0)
		if self.originalgraph.in_degree(node) == 0:
			print node + ' is a root node'
			print 'Backtrack is broken'
			return None

		edges = set()
		for (source, sink) in self.originalgraph.in_edges(node):
			edges.add((source, sink))

		for (source, sink) in edges:
			for i in self.originalgraph[source][sink]:
				endtime = self.originalgraph[source][sink][i]['data_edge'].endtime
				if curtime < de.Decimal(endtime):
					curtime = de.Decimal(endtime)

		return curtime.to_eng_string()

				





