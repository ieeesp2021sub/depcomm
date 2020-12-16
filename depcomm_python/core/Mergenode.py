import networkx as nx
import copy
#import datetime
from collections import Counter, OrderedDict

class Mergenode:
	
	def __init__(self, graph,detection):
		self.graph = graph
		self.detection = detection
		self.mergedgraph = copy.deepcopy(self.graph)
		self.nodeid_name = {}
		self.nodes = self.graph.nodes()
		self.edges = list(self.graph.edges())
		self.none_num = 0
		self.group_num = 0
		outputfile_node = './core/intermediatefiles/nodegroup.csv'
		self.fw = open(outputfile_node,'w')
	
	def getMergedgraph(self,comm2node,filename,meth):
		print 'Compressing...'
		self.nodeid_name = self.generatingnodename()
		
		mergedprocess = self.mergingprocess()  #graph
		mergedfile = self.mergingfile(mergedprocess)  #graph
		mergednetwork = self.mergingnetwork(mergedfile)  #graph
		self.fw.close()
		#nodes = list(mergednetwork.nodes())
		#for i in nodes:
		#	print i
		comm2node = self.merging(comm2node,filename,meth)
		return comm2node


	def generatingnodename(self):
		id_name = {}  #{id:(name,nameid)}
		nameid = 0
		names = []
		for nodeid in self.nodes:
			if self.nodes[nodeid]['data_node'].__class__.__name__ == 'ProcessNode':

				#get pidname
				pidname = self.nodes[nodeid]['data_node'].pidname

				#get filepath and ip
				neighbors = sorted(set(nx.all_neighbors(self.graph, nodeid)))
				filepaths = []
				ips = []
				for nbr in neighbors:
					if self.nodes[nbr]['data_node'].__class__.__name__ == 'FileNode':
						if (nodeid,nbr) in self.edges:
							filepath = self.nodes[nbr]['data_node'].filename
						else:
							filepath = self.nodes[nbr]['data_node'].filename+'-r'
						filepaths.append(filepath)
					if self.nodes[nbr]['data_node'].__class__.__name__ == 'NetworkNode':
						socureip = self.nodes[nbr]['data_node'].sourceIP
						desip = self.nodes[nbr]['data_node'].desIP
						ips.append(socureip+':'+desip)
				
				files_ips = sorted(filepaths)+sorted(ips)
				files_ips = '_'.join(files_ips)
				
				name = pidname+'_'+files_ips
				#name = pidname+'_'+files_ips
				if name in names:
					uid = names.index(name)+1
				else:
					names.append(name)
					nameid += 1
					uid = nameid
				
				id_name[nodeid] = (name,uid)
				#print nodeid+': '+name+', '+str(uid)

		return id_name

	def mergingprocess(self):
		res_group = []
		resid_group = []
		for nid in self.nodes:
			if self.nodes[nid]['data_node'].__class__.__name__ == 'ProcessNode':
				res_id,res = self.serizlize(nid)
				res_group.append(res)
				resid_group.append(res_id)
		b = dict(Counter(res_group))
		res_merge = [key for key,value in b.items()if value > 1]
		resid_merge = {}
		for i in res_merge:
			local = [k for (k,v) in enumerate(res_group) if v == i]
			for j in local:
				if resid_merge.has_key(i):
					resid_merge[i].append(resid_group[j])
				else:
					resid_merge[i] = [resid_group[j]]
			#print i+': '
			#print resid_merge[i]

		mergedprocess = self.runprocessmerging(self.mergedgraph, resid_merge)

		return mergedprocess

	def serizlize(self,root):
		res = []
		res_id = []
		father = self.getfather(self.graph, root)
		if father == 'none':
			self.none_num += 1
			father = father+str(self.none_num)
		res.append(father)
		res_id.append(father)

		def pre(root):
			if self.graph.has_node(root):
				res_id.append(root)
				res.append(self.nodeid_name[root][1])
				neighbors = self.graph.neighbors(root)
				neighbors_name = []
				for nid in neighbors:
					if self.nodes[nid]['data_node'].__class__.__name__ == 'ProcessNode':
						neighbors_name.append((nid,self.nodeid_name[nid][1]))
				neighbors_name.sort(key=lambda x:x[1])
				for nid,_ in neighbors_name:
					if self.graph[root][nid][0]['data_edge'].direct == 'forward':
						pre(nid)
		pre(root)
		return res_id ,str(res)

	def mergingfile(self, graph):
		filegroups = {}
		nodes = graph.nodes()
		for nid in nodes:
			node_instance = nodes[nid]['data_node']
			if node_instance.__class__.__name__ == 'FileNode':
				filepath = node_instance.path
				neighbors = sorted(set(nx.all_neighbors(graph, nid)))
				neighbors = '_'.join(neighbors)
				filekey = neighbors+'_'+filepath
				if filegroups.has_key(filekey):
					filegroups[filekey].append(nid)
				else:
					filegroups[filekey] = [nid]

		mergedfile = {}
		for key in filegroups:
			if len(filegroups[key]) == 1:
				continue
			mergedfile[key] = filegroups[key]
			#print key+': '+str(filegroups[key])
		
		mergedfilegraph = self.runfilemerging(graph, mergedfile)

		return mergedfilegraph

	def mergingnetwork(self, graph):
		networkgroups = {}
		nodes = graph.nodes()
		for nid in nodes:
			node_instance = nodes[nid]['data_node']
			if node_instance.__class__.__name__ == 'NetworkNode':
				sourceIP = node_instance.sourceIP
				desIP = node_instance.desIP
				IP = sourceIP+'->'+desIP
				neighbors = sorted(set(nx.all_neighbors(graph, nid)))
				neighbors = '_'.join(neighbors)
				networkkey = neighbors+'_'+IP
				if networkgroups.has_key(networkkey):
					networkgroups[networkkey].append(nid)
				else:
					networkgroups[networkkey] = [nid]

		mergednetwork = {}
		for key in networkgroups:
			if len(networkgroups[key]) == 1:
				continue
			mergednetwork[key] = networkgroups[key]
			#print key+': '+str(filegroups[key])

		mergednetworkgraph = self.runnetworkmerging(graph, mergednetwork)

		return mergednetworkgraph

	def runnetworkmerging(self, graph, mergenodes):
		nodes = graph.nodes()
		for group in mergenodes:
			self.group_num += 1
			holdnode = mergenodes[group][0]
			if graph.has_node(holdnode):
				nodes[holdnode]['data_node'].merged = True
			removenodes = mergenodes[group][1:]
			for i in removenodes:
				graph.remove_node(i)

			self.exportfile_network(mergenodes[group],self.group_num)

		return graph

	def runfilemerging(self, graph, mergenodes):
		nodes = graph.nodes()
		for group in mergenodes:
			self.group_num += 1
			holdnode = mergenodes[group][0]
			if graph.has_node(holdnode):
				nodes[holdnode]['data_node'].merged = True
			removenodes = mergenodes[group][1:]
			for i in removenodes:
				graph.remove_node(i)

			self.exportfile_file(mergenodes[group],self.group_num)

		return graph

	def runprocessmerging(self, graph, mergenodes):
		nodes = graph.nodes()
		b = sorted(mergenodes.items(), key = lambda kv:(len(kv[1][0]), kv[0]), reverse = True)
		mergenodes = OrderedDict(b)
		holdnodelist = []
		for group in mergenodes:
			popflag = False
			self.group_num += 1
			holdnodes = mergenodes[group][0][1:]
			for nid in holdnodes:
				if nid in nodes:
					nodes[nid]['data_node'].merged = True
					holdnodelist.append(nid)
			removenodes = mergenodes[group][1:]
			for i in removenodes:
				for j in i[1:]:
					if graph.has_node(j) and (j not in holdnodelist):
						graph.remove_node(j)
					elif j in holdnodelist:
						popflag = True
			if not popflag:
				self.exportfile_process(mergenodes[group],self.group_num)
		return graph

	def exportfile_process(self,groups,groupid):
		translist = [[i[j] for i in groups] for j in range(len(groups[0]))]
		root = translist[0][0]
		rootname = self.nodes[root]['data_node'].unidname
		for i in translist[1:]:
			n = 0
			for j in i:
				n += 1
				self.fw.write('group'+str(groupid)+',')
				self.fw.write(str(n)+','+i[0]+','+rootname+',')
				self.fw.write(j+','+self.nodes[j]['data_node'].unidname)
				self.fw.write('\n')

	def exportfile_file(self,group,groupid):
		n = 0
		for i in group:
			n += 1
			self.fw.write('group'+str(groupid)+',')
			self.fw.write(str(n)+','+group[0]+','+self.nodes[group[0]]['data_node'].path+',')
			self.fw.write(i+','+self.nodes[i]['data_node'].unidname)
			self.fw.write('\n')

	def exportfile_network(self,group,groupid):
		n = 0
		for i in group:
			n += 1
			self.fw.write('group'+str(groupid)+',')
			self.fw.write(str(n)+','+group[0]+','+self.nodes[group[0]]['data_node'].unidname+',')
			self.fw.write(i+','+self.nodes[i]['data_node'].unidname)
			self.fw.write('\n')

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

	def merging(self,comm2node,filename,meth):
		groups = {}
		fg = open('./core/intermediatefiles/nodegroup.csv')
		line = fg.readline()
		while line != '':
			line = line.rstrip()
			part = line.split(',')
			nid = part[2]
			group = part[4]
			if groups.has_key(nid):
				groups[nid].append(group)
			else:
				groups[nid] = [group]
			line = fg.readline()
		
		node2name = {}
		fr_nodeindex = open('./core/intermediatefiles/nid2name.txt')
		line = fr_nodeindex.readline()
		while line != '':
			line = line.rstrip()
			part = line.split(',')
			nid = part[0]
			name = part[1]
			node2name[nid] = name
			line = fr_nodeindex.readline()

		leaf = {}
		fleaf = open('./core/intermediatefiles/leaf.txt')
		line = fleaf.readline()
		while line != '':
			line = line.rstrip()
			part = line.split(',')
			nid = part[0]
			leaf[nid] = part[2:]
			line = fleaf.readline()

		comm2node_merged = copy.deepcopy(comm2node)
		for c in comm2node:
			for node in comm2node[c]:
				if groups.has_key(node):
					group = list(groups[node])
					for g in group:
						if g == node:
							continue
						else:
							comm2node_merged[c].remove(g)
				if leaf.has_key(node):
					leafs = leaf[node]
					f_num = 0
					n_num = 0
					for index,l in enumerate(leafs):
						if 'f' in l:
							f_num += 1
							if f_num == 1:
								continue
							else:
								comm2node_merged[c].remove(l)
						
						elif 'n' in l:
							if node2name[l] == self.detection:continue
							n_num += 1
							if n_num == 1:
								continue
							else:
								comm2node_merged[c].remove(l)
		
		fw = open('./output/'+filename+'_'+meth+'_community_merged.txt','w')
		for c in comm2node_merged:
			fw.write(str(c)+',')
			for nodeid in comm2node_merged[c]:
				if node2name.has_key(nodeid):
					label_name = node2name[nodeid]
					fw.write(label_name+',')
			fw.write('\n')
		#print comm2node_merged		




