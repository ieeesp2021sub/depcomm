import networkx as nx
import datetime

class FindNode:

	def __init__(self, graphinput):
		self.graphinput = graphinput

	def allnode(self, targetpath):
		fw = open(targetpath, 'w')
		nodes = self.graphinput.nodes()
		for node_id in nodes:
			dn = nodes[node_id]['data_node']
			if dn.__class__.__name__ == 'ProcessNode':
				node_name = dn.pidname+'('+dn.pid+')'
			elif dn.__class__.__name__ == 'FileNode':
				node_name = dn.filename
			elif dn.__class__.__name__ == 'NetworkNode':
				node_name = dn.sourceIP+':'+dn.sourcePort + '->' +dn.desIP+':'+dn.desPort
			elif dn.__class__.__name__ == 'NetworkNode2':
				node_name = dn.desIP+':'+dn.desPort
			fw.write(node_name+'\n')

	def processnode2onlyread(self, targetpath):
		fw = open(targetpath, 'w')
		pn2rf = {}
		nodes = self.graphinput.nodes()
		for node_id in nodes:
			dn = nodes[node_id]['data_node']
			if dn.__class__.__name__ == 'FileNode':
				if self.graphinput.in_degree(node_id) == 0:
					for (source, sink) in self.graphinput.out_edges(node_id):
						if nodes[sink]['data_node'].__class__.__name__ == 'ProcessNode':
							if pn2rf.has_key(sink):
								pn2rf[sink].add(node_id)
							else:
								pn2rf[sink] = set([node_id])

		for key in pn2rf:
			fw.write(nodes[key]['data_node'].pidname+'('+nodes[key]['data_node'].pid+')<-')
			for i in pn2rf[key]:
				fw.write(nodes[i]['data_node'].filename+',')
			fw.write('\n')
	
	def node2leafnode(self, targetpath):
		fw = open(targetpath, 'w')
		node2leaf = {}
		nodes = self.graphinput.nodes()
		for node_id in nodes:
			if self.graphinput.in_degree(node_id) == 1 and self.graphinput.out_degree(node_id) == 1:
				neighbors = list(nx.all_neighbors(self.graphinput, node_id))
				if neighbors[0] == neighbors[1]:
					if node2leaf.has_key(neighbors[0]):
						node2leaf[neighbors[0]].add(node_id)
					else:
						node2leaf[neighbors[0]] = set([node_id])

		for key in node2leaf:
			dn = nodes[key]['data_node']
			if dn.__class__.__name__ == 'FileNode':
				fw.write(dn.filename+'<-')
			elif dn.__class__.__name__ == 'ProcessNode':
				fw.write(dn.pidname+'('+dn.pid+')<-')
			elif dn.__class__.__name__ == 'NetworkNode':
				fw.write(dn.sourceIP+':'+dn.sourcePort + '->' +dn.desIP+':'+dn.desPort+'<-')
			elif dn.__class__.__name__ == 'NetworkNode2':
				fw.write(dn.desIP+':'+dn.desPort+'<-')
			for i in node2leaf[key]:
				di = nodes[i]['data_node']
				if di.__class__.__name__ == 'FileNode':
					fw.write(di.filename+',')
				elif di.__class__.__name__ == 'ProcessNode':
					fw.write(di.pidname+'('+di.pid+')'+',')
				elif di.__class__.__name__ == 'NetworkNode':
					fw.write(di.sourceIP+':'+di.sourcePort + '->' +di.desIP+':'+di.desPort+',')
				elif di.__class__.__name__ == 'NetworkNode2':
					fw.write(dn.desIP+':'+dn.desPort+',')
			fw.write('\n')

	def findfilenodezeroin_degree(self, targetpath):
		finddict = {}
		nodes = self.graphinput.nodes()
		for node_id in nodes:
			if nodes[node_id]['data_node'].__class__.__name__ == 'FileNode':
				if self.graphinput.in_degree(node_id) == 0 and self.graphinput.out_degree(node_id) > 1:
					for (source, sink) in self.graphinput.out_edges(node_id):
						if nodes[sink]['data_node'].__class__.__name__ == 'ProcessNode':
							for i in self.graphinput[source][sink]:
								if finddict.has_key(source):
									finddict[source].append((sink,i))
								else:
									finddict[source] = [(sink,i)]

		fw = open(targetpath, 'w')
		for key in finddict:
			sourcenode = nodes[key]['data_node']
			fw.write(sourcenode.filename+'('+key+') -> ')
			for i in finddict[key]:
				sinknode = nodes[i[0]]['data_node']
				edge = self.graphinput[key][i[0]][i[1]]['data_edge']
				fw.write(sinknode.pidname+'('+sinknode.pid+')('+i[0]+')('+edge.event+'), ')
			fw.write('\n')
		fw.close()
	
	def findrootprocessnode(self,targetpath):
		fw = open(targetpath, 'w')
		finddict = {}
		nodes = self.graphinput.nodes()
		for node_id in nodes:
			if nodes[node_id]['data_node'].__class__.__name__ == 'ProcessNode':
				father = self.getfather(self.graphinput, node_id)
				if father == 'none':
					fw.write(nodes[node_id]['data_node'].pidname+'('+nodes[node_id]['data_node'].pid+')('+node_id+'): ')
					out_edge = set()
					for (source,sink) in self.graphinput.out_edges(node_id):
						if nodes[sink]['data_node'].__class__.__name__ == 'ProcessNode':
							out_edge.add(sink)
					for i in out_edge:
						timestamp = self.graphinput[node_id][i][0]['data_edge'].starttime.split('.')[0]
						startArray = datetime.datetime.fromtimestamp(int(timestamp))
						starttime = startArray.strftime("%Y-%m-%d %H:%M:%S")
						fw.write(nodes[i]['data_node'].pidname+'('+nodes[i]['data_node'].pid+')('+i+')('+starttime+'), ')
					fw.write('\n')
					
	def getfather(self, graph, node):
		nodes = graph.nodes()
		in_neighbors = self.in_neighbor(graph, node)
		find = False
		for pre in in_neighbors:
			if nodes[pre]['data_node'].__class__.__name__ == 'ProcessNode':
				if graph[pre][node][0]['data_edge'].direct == 'forward':
					father = pre
					find = True
					break
		if find:
			return father
		else:
			return 'none'
	
	def in_neighbor(self, graph, node):
		in_node = []
		for i in list(graph.in_edges(node)):
			in_node.append(i[0])
		return in_node

	def findnodewithinorout_degree(self, targetpath):
		finddict_in = {}
		finddict_out = {}
		finddict_inevent = {}
		finddict_outevent = {}
		nodes = self.graphinput.nodes()
		for node_id in nodes:
			if self.graphinput.in_degree(node_id) > 0 and self.graphinput.out_degree(node_id) > 0:
				out_edge = set()
				for (source, sink) in self.graphinput.out_edges(node_id):
					out_edge.add((source,sink))

				for (source, sink) in out_edge:
					for i in self.graphinput[source][sink]:
						event = self.graphinput[source][sink][i]['data_edge'].event
						if finddict_out.has_key(source):
							if (sink,event) in finddict_outevent[source]:continue
							else:
								finddict_out[source].append((sink,i))
								finddict_outevent[source].add((sink,event))
						else:
							finddict_out[source] = [(sink,i)]
							finddict_outevent[source] = set([(sink,event)])
				
				in_edge = set()
				for (source, sink) in self.graphinput.in_edges(node_id):
					in_edge.add((source, sink))

				for (source, sink) in in_edge:
					for i in self.graphinput[source][sink]:
						event = self.graphinput[source][sink][i]['data_edge'].event
						if finddict_in.has_key(sink):
							if (source,event) in finddict_inevent[sink]:continue
							else:
								finddict_in[sink].append((source,i))
								finddict_inevent[sink].add((source,event))
						else:
							finddict_in[sink] = [(source,i)]
							finddict_inevent[sink] = set([(source,event)])

		fw = open(targetpath, 'w')
		for key in finddict_out:
			sourcenode_out = nodes[key]['data_node']
			if sourcenode_out.__class__.__name__ == 'ProcessNode':
				fw.write(sourcenode_out.pidname+'('+sourcenode_out.pid+')'+'('+key+') '+sourcenode_out.argus+' -> ')
				#fw.write(sourcenode_out.pidname+'('+sourcenode_out.pid+')'+'('+key+') -> ')
			elif sourcenode_out.__class__.__name__ == 'FileNode':
				fw.write(sourcenode_out.filename+'('+key+') '+sourcenode_out.extension+' -> ')
			elif sourcenode_out.__class__.__name__ == 'NetworkNode':
				fw.write(sourcenode_out.sourceIP+':'+sourcenode_out.sourcePort + '->' +sourcenode_out.desIP+':'+sourcenode_out.desPort+'('+key+') -> ')
			elif sourcenode_out.__class__.__name__ == 'NetworkNode2':
				fw.write(sourcenode_out.desIP+':'+sourcenode_out.desPort+'('+key+') -> ')

			for i in finddict_out[key]:
				sinknode_out = nodes[i[0]]['data_node']
				edge = self.graphinput[key][i[0]][i[1]]['data_edge']
				startlist = edge.starttime.split('.')
				startArray = datetime.datetime.fromtimestamp(int(startlist[0]))
				starttime = startArray.strftime("%Y-%m-%d %H:%M:%S")+'.'+startlist[1]
				endlist = edge.endtime.split('.')
				endArray = datetime.datetime.fromtimestamp(int(endlist[0]))
				endtime = endArray.strftime("%Y-%m-%d %H:%M:%S")+'.'+endlist[1]
				''
				if sinknode_out.__class__.__name__ == 'ProcessNode':
					#fw.write(sinknode_out.pidname+'('+sinknode_out.pid+')('+i[0]+'), '+edge.event+', ')
					fw.write(sinknode_out.pidname+'('+sinknode_out.pid+')('+i[0]+')('+edge.event+','+starttime+'~'+endtime+'), ')
					#fw.write(sinknode_out.pidname+'('+sinknode_out.pid+')('+i[0]+')('+edge.event+','+str(edge.size)+'), ')
				elif sinknode_out.__class__.__name__ == 'FileNode':
					#fw.write(sinknode_out.filename+'('+i[0]+'), '+edge.event+', ')
					fw.write(sinknode_out.filename+'('+i[0]+')('+edge.event+','+starttime+'~'+endtime+'), ')
					#fw.write(sinknode_out.filename+'('+i[0]+')('+edge.event+','+str(edge.size)+'), ')
				elif sinknode_out.__class__.__name__ == 'NetworkNode':
					#fw.write(sinknode_out.sourceIP+':'+sinknode_out.sourcePort + '->' +sinknode_out.desIP+':'+sinknode_out.desPort+'('+i[0]+'), '+edge.event+', ')
					fw.write(sinknode_out.sourceIP+':'+sinknode_out.sourcePort + '->' +sinknode_out.desIP+':'+sinknode_out.desPort+'('+i[0]+')('+edge.event+','+starttime+'~'+endtime+'), ')
					#fw.write(sinknode_out.sourceIP+':'+sinknode_out.sourcePort + '->' +sinknode_out.desIP+':'+sinknode_out.desPort+'('+i[0]+')('+edge.event+','+str(edge.size)+'), ')
				elif sinknode_out.__class__.__name__ == 'NetworkNode2':
					fw.write(sinknode_out.desIP+':'+sinknode_out.desPort+'('+i[0]+'), '+edge.event+', ')
					#fw.write(sinknode_out.desIP+':'+sinknode_out.desPort+'('+i[0]+')('+edge.event+','+starttime+'~'+endtime+'), ')
					#fw.write(sinknode_out.desIP+':'+sinknode_out.desPort+'('+i[0]+')('+edge.event+','+str(edge.size)+'), ')
			fw.write('\n')

			sinknode_in = nodes[key]['data_node']
			if sinknode_in.__class__.__name__ == 'ProcessNode':
				#fw.write(sinknode_in.pidname+'('+sinknode_in.pid+')'+'('+key+') <- ')
				fw.write(sinknode_in.pidname+'('+sinknode_in.pid+')'+'('+key+') '+sinknode_in.argus+' <- ')
			elif sinknode_in.__class__.__name__ == 'FileNode':
				fw.write(sinknode_in.filename+'('+key+') <- ')
			elif sinknode_in.__class__.__name__ == 'NetworkNode':
				fw.write(sinknode_in.sourceIP+':'+sinknode_in.sourcePort + '->' +sinknode_in.desIP+':'+sinknode_in.desPort+'('+key+') <- ')
			elif sinknode_in.__class__.__name__ == 'NetworkNode2':
				fw.write(sinknode_in.desIP+':'+sinknode_in.desPort+'('+key+') <- ')

			for i in finddict_in[key]:
				sourcenode_in = nodes[i[0]]['data_node']
				edge = self.graphinput[i[0]][key][i[1]]['data_edge']
		
				startlist = edge.starttime.split('.')
				startArray = datetime.datetime.fromtimestamp(int(startlist[0]))
				starttime = startArray.strftime("%Y-%m-%d %H:%M:%S")+'.'+startlist[1]
				endlist = edge.endtime.split('.')
				endArray = datetime.datetime.fromtimestamp(int(endlist[0]))
				endtime = endArray.strftime("%Y-%m-%d %H:%M:%S")+'.'+endlist[1]
				''
				if sourcenode_in.__class__.__name__ == 'ProcessNode':
					#fw.write(sourcenode_in.pidname+'('+sourcenode_in.pid+')('+i[0]+'), '+edge.event+', ')
					fw.write(sourcenode_in.pidname+'('+sourcenode_in.pid+')('+i[0]+')('+edge.event+','+starttime+'~'+endtime+'), ')
					#fw.write(sourcenode_in.pidname+'('+sourcenode_in.pid+')('+i[0]+')('+edge.event+','+str(edge.size)+'), ')
				elif sourcenode_in.__class__.__name__ == 'FileNode':
					#fw.write(sourcenode_in.filename+'('+i[0]+'), '+edge.event+', ')
					fw.write(sourcenode_in.filename+'('+i[0]+')('+edge.event+','+starttime+'~'+endtime+'), ')
					#fw.write(sourcenode_in.filename+'('+i[0]+')('+edge.event+','+str(edge.size)+'), ')
				elif sourcenode_in.__class__.__name__ == 'NetworkNode':
					#fw.write(sourcenode_in.sourceIP+':'+sourcenode_in.sourcePort + '->' +sourcenode_in.desIP+':'+sourcenode_in.desPort+'('+i[0]+'), '+edge.event+', ')
					fw.write(sourcenode_in.sourceIP+':'+sourcenode_in.sourcePort + '->' +sourcenode_in.desIP+':'+sourcenode_in.desPort+'('+i[0]+')('+edge.event+','+starttime+'~'+endtime+'), ')
					#fw.write(sourcenode_in.sourceIP+':'+sourcenode_in.sourcePort + '->' +sourcenode_in.desIP+':'+sourcenode_in.desPort+'('+i[0]+')('+edge.event+','+str(edge.size)+'), ')
				elif sourcenode_in.__class__.__name__ == 'NetworkNode2':
					#fw.write(sourcenode_in.desIP+':'+sourcenode_in.desPort+'('+i[0]+'), '+edge.event+', ')
					fw.write(sourcenode_in.desIP+':'+sourcenode_in.desPort+'('+i[0]+')('+edge.event+','+starttime+'~'+endtime+'), ')
					#fw.write(sourcenode_in.desIP+':'+sourcenode_in.desPort+'('+i[0]+')('+edge.event+','+str(edge.size)+'), ')
			fw.write('\n')
		fw.close()
