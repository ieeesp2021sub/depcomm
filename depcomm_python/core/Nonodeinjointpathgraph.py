import networkx as nx
import numpy as np
from itertools import combinations
import copy
import decimal as de
import pdb

class Nonodeinjointpathgraph:

	def __init__(self, originalgraph):
		self.originalgraph = originalgraph
		self.resultgraph = copy.deepcopy(self.originalgraph)
		self.node_neighbor_dict = {}
		self.node_neighbor_name_dict = {}

	def getNonodeinjointpathgraph(self, thre):
		
		print 'merging node-injoin path...'
		self.node_neighbor_dict,self.node_neighbor_name_dict,node_neighbor_name_merge = self.getnodetoneighbor()
		
		nodewithsimilarneighbor_dict = self.getnodewithsimilarneighbor(node_neighbor_name_merge, thre)
		#pdb.set_trace()

		mergetuples = self.getpathclusters(nodewithsimilarneighbor_dict,thre)

		resultgraph = self.mergence(mergetuples)

		return resultgraph

	def getpathclusters(self, pathsource, thre):
		nodes = self.originalgraph.nodes()
		mergetuples = []
		while pathsource:
			current_node_neighbors = pathsource.popitem()
			part = current_node_neighbors[0].split(':')
			pre_node = part[0]
			current_node_list = current_node_neighbors[1]
			path = {}
			#path_edge = {}
			cluster0 = []
			for path_id, current_node in enumerate(current_node_list):
				path[str(path_id)] = [current_node]
				#path_edge[str(path_id)] = [(current_node,pre_node)]
				cluster0.append((path_id,current_node,pre_node))
			clusters = []
			clusters.append([cluster0])
			cluster_log = set()
			while clusters:
				next_clusters = []
				current_cluster = clusters.pop()
				for ci in current_cluster:
					if len(ci) == 1: continue
					next_nodes_dict = {}
					key_neighbor_args = {}
					for node_tuple in ci:
						next_nodes_events = self.node_neighbor_dict[node_tuple[1]]
						for node_event in next_nodes_events:
							if node_tuple[2] in node_event: continue
							else:
								node_event_part = node_event.split(':')
								node_item = nodes[node_event_part[0]]['data_node']
								node_neighbors = self.node_neighbor_name_dict[node_event_part[0]]
								node_neighbors.sort()
								neighbors_key = '_'.join(node_neighbors)
								if node_item.__class__.__name__ == 'ProcessNode':
									name = node_item.pidname
									node_args = self.getargs([node_event_part[0]])
									name_neighbor_key = name+':'+node_event_part[1]+':'+neighbors_key
									if not key_neighbor_args:
										key = name_neighbor_key+':'+node_args[0][1]
										key_neighbor_args[name_neighbor_key] = {node_args[0][1]:key}
									elif key_neighbor_args.has_key(name_neighbor_key):
										f = 0
										for k in key_neighbor_args[name_neighbor_key]:
											score = self.getsimilaritytwo(k,node_args[0][1])
											if score > thre:
												f = 1
												key = key_neighbor_args[name_neighbor_key][k]
												break
										if f == 0:
											key = name_neighbor_key+':'+node_args[0][1]
											key_neighbor_args[name_neighbor_key][node_args[0][1]] = key
									else:
										key = name_neighbor_key+':'+node_args[0][1]
										key_neighbor_args[name_neighbor_key] = {node_args[0][1]:key}
								elif node_item.__class__.__name__ == 'FileNode':
									name = node_item.path+':'+node_item.extension
									key = name+':'+node_event_part[1]+':'+neighbors_key
								elif node_item.__class__.__name__ == 'NetworkNode':
									name = node_item.sourceIP+':'+node_item.sourcePort + '->' +node_item.desIP+':'+node_item.desPort
									key = name+':'+node_event_part[1]+':'+neighbors_key
								elif node_item.__class__.__name__ == 'NetworkNode2':
									name = node_item.sourceIP+':'+node_item.sourcePort
									key = name+':'+node_event_part[1]+':'+neighbors_key
								item = (node_tuple[0],node_event_part[0],node_tuple[1])
								if next_nodes_dict.has_key(key):
									next_nodes_dict[key].append(item)
								else:
									next_nodes_dict[key] = [item]
					#print next_nodes_dict
					
					flag = []
					cluster_ci_ = []
					for nextkey in next_nodes_dict:
						next_tuples = next_nodes_dict[nextkey]
						t = set()
						n = 0

						for pathi,nexti,_ in next_tuples:
							t.add(nexti)
							if nexti in path[str(pathi)]:
								n += 1
						if n == len(next_tuples):
							#for pathi,nexti,prei in next_tuples:
							#	if ((nexti,prei) not in path_edge[str(pathi)]) and ((prei,nexti) not in path_edge[str(pathi)]):
							#		path_edge[str(pathi)].append((nexti,prei))
							continue

						#if len(next_tuples) > 1 and len(t) == 1:
						if len(t) == 1:
							flag.append(1)
							reducepath = []
							if len(next_tuples) > 1:
								for pathi, _, _ in next_tuples:
									reducepath.append(pathi)
							#for pathi,nexti,prei in next_tuples:
							#	if ((nexti,prei) not in path_edge[str(pathi)]) and ((prei,nexti) not in path_edge[str(pathi)]):
							#		path_edge[str(pathi)].append((nexti,prei))
								for k in pathsource:
									if list(t)[0] in k:
										if next_tuples[0][2] in pathsource[k]:
											pathsource.pop(k)
											break
							else:
								cluster_ci_.append(next_tuples)
						else:
							flag.append(0)
							for pathi,nexti,prei in next_tuples:
								path[str(pathi)].append(nexti)
								#path_edge[str(pathi)].append((nexti,prei))
							cluster_ci_.append(next_tuples)
					cluster_ci = self.reducecluster(cluster_ci_)
					#if len(cluster_ci) == len(ci):
					#	continue
					if (flag) and (0 not in flag):
						if reducepath:
							cluster_log_i = []
							for pathi,nodei,_ in ci:
								if pathi in reducepath:
									cluster_log_i.append(pathi)
							if cluster_log_i:
								cluster_log_i.sort()
								cluster_log.add(tuple(cluster_log_i))
						else:
							for i in cluster_ci:
								next_clusters.append(i)
					else:
						reducepath = []
						for i in cluster_ci:
							next_clusters.append(i)
					#pdb.set_trace()
				if next_clusters:
					#print 'next node...'
					next_clusters_reduced = self.reducecluster2(next_clusters)
					#pdb.set_trace()
					clusters.append(next_clusters_reduced)

			#mergetuples.append((cluster_log, path, path_edge))
			mergetuples.append((cluster_log, path))
		return mergetuples

	def reducecluster(self, clusters):
		if len(clusters) == 1:
			return clusters
		else:
			a = set()
			for i in clusters:
				b = []
				for j in i:
					b.append(j[0])
				b.sort()
				a.add(tuple(b))

			reduce_clusters_path = []
			r = []
			r.append(list(a))
			while True:
				p = r.pop()
				ct = list(combinations(p, 2))
				i_s = set()
				for s1,s2 in ct:
					tmp = list(set(s1) & set(s2))
					tmp.sort()
					if tmp:
						i_s.add(tuple(tmp))
				if len(i_s) == 1:
					reduce_clusters_path = list(i_s)
					break
				elif len(i_s) == 0:
					reduce_clusters_path = p 
					break
				else:
					r.append(list(i_s))
			
			new_cluster = []
			for clusteri in clusters:
				for new_clusteri in reduce_clusters_path:
					tmp_list = []
					for i in clusteri:
						if i[0] in new_clusteri:
							tmp_list.append(i)
					if tmp_list:
						new_cluster.append(tmp_list)

			return new_cluster

	def reducecluster2(self, clusters):
		a = set()
		for i in clusters:
			b = []
			for j in i:
				b.append(j[0])
			b.sort()
			a.add(tuple(b))
		
		def getintersection(set_tuple):
			ct = list(combinations(set_tuple, 2))
			i_s = set()
			for s1,s2 in ct:
				tmp = list(set(s1) & set(s2))
				tmp.sort()
				if tmp:
					i_s.add(tuple(tmp))
			return i_s

		if len(a) == 1:
			return clusters
		else:
			intersection = getintersection(a)
			if not intersection:
				return clusters
			else:
				r = [a]
				while intersection:
					p = r.pop()
					reduce_clusters_path = set()
					reduce_clusters_path = reduce_clusters_path.union(intersection)
					for i in p:
						flag = 0
						for j in intersection:
							if set(i)&set(j):
								flag = 1
								d = set(i) - set(j)
								if d:
									d = list(d)
									d.sort()
									reduce_clusters_path.add(tuple(d))
						if flag == 0:
							reduce_clusters_path.add(i)
					r.append(reduce_clusters_path)
					intersection = getintersection(reduce_clusters_path)
 
				new_cluster = []
				reduce_clusters_path = list(reduce_clusters_path)
				for k in reduce_clusters_path:
					if len(list(k)) == 1:
						reduce_clusters_path.remove(k)

				for clusteri in clusters:
					for new_clusteri in reduce_clusters_path:
						tmp_list = []
						for i in clusteri:
							if i[0] in new_clusteri:
								tmp_list.append(i)
						if tmp_list:
							new_cluster.append(tmp_list)

			return new_cluster

	def getnodetoneighbor(self):
		nodes = self.originalgraph.nodes()
		node_neighbors = {}
		node_neighbors_name = {}
		node_neighbors_name_merge = {}
		for node_id in nodes:
			out_neighbor_event = {}
			out_neighbors = list(self.originalgraph.neighbors(node_id))
			for out_nodeid in out_neighbors:
				out_edges = self.originalgraph[node_id][out_nodeid]
				out_events = set()
				for i in out_edges:
					out_events.add(out_edges[i]['data_edge'].event)
				out_event_str = ','.join(sorted(list(out_events)))
				out_neighbor_event[out_nodeid] = out_event_str

			in_neighbor_event = {}
			in_neighbors = self.inneighbors(node_id)
			for in_nodeid in in_neighbors:
				in_edges = self.originalgraph[in_nodeid][node_id]
				in_events = set()
				for i in in_edges:
					in_events.add(in_edges[i]['data_edge'].event)
				in_event_str = ','.join(sorted(list(in_events)))
				in_neighbor_event[in_nodeid] = in_event_str
			
			neighbors_list = set()
			for out_n in out_neighbor_event:
				out_event = out_n+':'+out_neighbor_event[out_n]
				if out_n in in_neighbor_event:
					if out_neighbor_event[out_n] != in_neighbor_event[out_n]:
						out_event = out_n+':'+out_neighbor_event[out_n]+'_'+in_neighbor_event[out_n]
				neighbors_list.add(out_event)

			for in_n in in_neighbor_event:
				if in_n in out_neighbor_event:
					continue
				else:
					in_event = in_n+':'+in_neighbor_event[in_n]
					neighbors_list.add(in_event)
			neighbors_list = list(neighbors_list)

			neighbors_name_list = []
			neighbors_name_merge_dict = {}
			for i in neighbors_list:
				part = i.split(':')
				node = nodes[part[0]]['data_node']
				if node.__class__.__name__ == 'ProcessNode':
					name = node.pidname
				elif node.__class__.__name__ == 'FileNode':
					name = node.path+':'+node.extension
				elif node.__class__.__name__ == 'NetworkNode':
					name = node.sourceIP+':'+node.sourcePort + '->' +node.desIP+':'+node.desPort
				elif node.__class__.__name__ == 'NetworkNode2':
					name = node.sourceIP+':'+node.sourcePort
				key = name+':'+part[1]
				neighbors_name_list.append(key)
				if neighbors_name_merge_dict.has_key(key):
					neighbors_name_merge_dict[key].append(part[0])
				else:
					neighbors_name_merge_dict[key] = [part[0]]
			node_neighbors_name[node_id] = neighbors_name_list
			node_neighbors_name_merge[node_id] = neighbors_name_merge_dict
			node_neighbors[node_id] = neighbors_list
			
		return node_neighbors,node_neighbors_name,node_neighbors_name_merge

	def getnodewithsimilarneighbor(self, node_neighbor_merge, thre):
		nodewithsimilarneighbor = {}
		for node_id in node_neighbor_merge:
			n = 0
			if self.originalgraph.nodes()[node_id]['data_node'].__class__.__name__ != 'ProcessNode':continue
			for namekey in node_neighbor_merge[node_id]:
				neighbors_list = node_neighbor_merge[node_id][namekey]
				if len(neighbors_list) >= 2:
					neighbor_neighbor_similar = {}
					for neighbor in neighbors_list:
						neighbor_neighbors = self.node_neighbor_name_dict[neighbor]
						neighbor_neighbors.sort()
						key = '_'.join(neighbor_neighbors)
						if neighbor_neighbor_similar.has_key(key):
							neighbor_neighbor_similar[key].append(neighbor)
						else:
							neighbor_neighbor_similar[key] = [neighbor]
					for neighbor_neighbor_key in neighbor_neighbor_similar:
						neighbor_neighbor_list = neighbor_neighbor_similar[neighbor_neighbor_key]
						if len(neighbor_neighbor_list) >= 2:
							if self.originalgraph.nodes()[neighbor_neighbor_list[0]]['data_node'].__class__.__name__ == 'ProcessNode':
								neighbor_args = self.getargs(neighbor_neighbor_list)
								clusterbyargs = self.getclusterbyargs(neighbor_args, thre)
								for c in clusterbyargs:
									if len(c) >= 2:
										n += 1
										nodewithsimilarneighbor[node_id+':'+str(n)] = c
										#print node_id+':'+str(n)
										#print c
							else:
								n += 1
								nodewithsimilarneighbor[node_id+':'+str(n)] = neighbor_neighbor_list
								#print node_id+':'+str(n)
								#print neighbor_neighbor_list
		return nodewithsimilarneighbor	

	def getargs(self, node_list):
		nodes = self.originalgraph.nodes()
		node_args = []
		for node_id in node_list:
			neighbors = list(nx.all_neighbors(self.originalgraph, node_id))
			args = nodes[node_id]['data_node'].argus
			for neighbor_id in neighbors:
				if nodes[neighbor_id]['data_node'].__class__.__name__ == 'FileNode':
					args = args.replace(nodes[neighbor_id]['data_node'].name,'~')
			for neighbor_id in neighbors:
				if nodes[neighbor_id]['data_node'].__class__.__name__ == 'FileNode':
					if nodes[neighbor_id]['data_node'].extension != '':
						args = args.replace(nodes[neighbor_id]['data_node'].extension,'~')
			node_args.append((node_id,args))
		return node_args

	def getsimilaritytwo(self, str1, str2):
		part1 = str1.split('.')
		for i in part1:
			if '' in part1:
				part1.remove('')
		if not part1:
			part1.append('xxx')
		part2 = str2.split('.')
		for i in part2:
			if '' in part2:
				part2.remove('')
		if not part2:
			part2.append('xxx')
		similarity = self.getsimilarscore(part1, part2)
		return similarity

	def getclusterbyargs(self, node_args_list, thre):
		part0 = node_args_list[0][1].split('.')
		for i in part0:
			if '' in part0:
				part0.remove('')
		if not part0:
			part0.append('xxx')
		clusterbyargs = [[(node_args_list[0][0],part0)]]
		for node_args_ta in node_args_list:
			part_ta = node_args_ta[1].split('.')
			for i in part_ta:
				if '' in part_ta:
					part_ta.remove('')
			if not part_ta:
				part_ta.append('xxx')
			flag = 0
			for node_args_sc in clusterbyargs:
				part_sc = node_args_sc[0][1]
				similar_score = self.getsimilarscore(part_sc, part_ta)
				if similar_score >= thre:
					flag = 1
					node_args_sc.append((node_args_ta[0],part_ta))
			if flag == 0:
				clusterbyargs.append([(node_args_ta[0],part_ta)])
		
		del clusterbyargs[0][0]
		cluster1 = []
		for i in clusterbyargs:
			cluster2 = []
			for j in i:
				cluster2.append(j[0])
			cluster1.append(cluster2)

		return cluster1

	def getsimilarscore(self, list1, list2):
		cosine_score = self.getcosinesimilar(list1, list2)
		jaccard_score = self.getjaccardsimilar(list1, list2)
		return max(cosine_score, jaccard_score)

	def getcosinesimilar(self, list1, list2):
		key_list = list(set(list1+list2))
		list_vector1 = np.zeros(len(key_list))
		list_vector2 = np.zeros(len(key_list))
		for i in range(len(key_list)):
			for j in range(len(list1)):
				if key_list[i] == list1[j]:
					list_vector1[i] += 1
			for k in range(len(list2)):
				if key_list[i] == list2[k]:
					list_vector2[i] += 1

		return float(np.dot(list_vector1, list_vector2)/
				(np.linalg.norm(list_vector1)*np.linalg.norm(list_vector2)))
	
	def getjaccardsimilar(self, list1, list2):
		temp1 = 0
		for i in list1:
			if i in list2:
				temp1 += 1
		temp2 = 0
		for i in list2:
			if i in list1:
				temp2 += 1
		temp = min(temp1,temp2)
		fenmu = len(list1)+len(list2)-temp
		return float(temp/fenmu)

	def inneighbors(self, node_id):
		in_neighbors = []
		for i in list(self.originalgraph.in_edges(node_id)):
			in_neighbors.append(i[0])	
		return list(set(in_neighbors))
	
	def mergence(self, mergetuples):
		#print mergetuples
		nodes = self.originalgraph.nodes()
		outputfile_node = './core/intermediatefiles/nodegroup.csv'
		#outputfile_edge = './intermediatefiles/edgegroup.csv'
		f_node = open(outputfile_node,'w')
		#f_edge = open(outputfile_edge,'w')
		groupid = 0
		#for groups,pathnodes,pathedges in mergetuples:
		for groups,pathnodes in mergetuples:
			for group in groups:
				groupid += 1
				S_node = {}
				#S_edge = {}
				n = 0
				for pathid in group:
					n += 1
					if n == 1:
						name_node_list = []
						path_nodes = pathnodes[str(pathid)]
						hold_nodes = path_nodes
						for nodeid in path_nodes:
							node = nodes[nodeid]['data_node']
							resultnodes = self.resultgraph.nodes()
							if self.resultgraph.has_node(nodeid):
								resultnodes[nodeid]['data_node'].merged = True
							if node.__class__.__name__ == 'FileNode':
								name = node.path
								data = node.filename
							elif node.__class__.__name__ == 'ProcessNode':
								name = node.pidname
								data = name+'('+node.pid+')'
							elif node.__class__.__name__ == 'NetworkNode':
								name = node.sourceIP+':'+node.sourcePort + '->' +node.desIP+':'+node.desPort
								data = name
							elif node.__class__.__name__ == 'NetworkNode2':
								name = node.sourceIP+':'+node.sourcePort
								data = name
							name_node_list.append(name)
							S_node[nodeid+','+name] = [(nodeid,data)]
						
						'''
						name_edge_list = []
						path_edges = pathedges[str(pathid)]
						hold_edges = []
						for edgeid in path_edges:
							edgetwo = []
							try:
								edge_tuple = (self.originalgraph[edgeid[0]][edgeid[1]], (edgeid[0],edgeid[1]))
							except KeyError:
								edge_tuple = 'None'
							edgetwo.append(edge_tuple)
							try:
								edge_tuple = (self.originalgraph[edgeid[1]][edgeid[0]], (edgeid[1],edgeid[0]))
							except KeyError:
								edge_tuple = 'None'
							edgetwo.append(edge_tuple)
							for edge_tuple in edgetwo:
								if edge_tuple == 'None':
									continue
								else:
									hold_edges.append(edge_tuple[1])
									edge = edge_tuple[0]
									sourceid = edge_tuple[1][0]
									sinkid = edge_tuple[1][1]
									event = edge[0]['data_edge'].event
									starttime = edge[0]['data_edge'].starttime
									endtime = edge[0]['data_edge'].endtime
									size = edge[0]['data_edge'].size
									name = sourceid+':'+sinkid+':'+event
									data = sourceid+','+sinkid+','+event+','+starttime+','+endtime+','+str(size)
									name_edge_list.append(name)
									S_edge[name] = [data]
									self.resultgraph[sourceid][sinkid][0]['data_edge'].merged = True
							'''
					else:
						path_nodes = pathnodes[str(pathid)]
						for local,nodeid in enumerate(path_nodes):
							node = nodes[nodeid]['data_node']
							if node.__class__.__name__ == 'FileNode':
								data = node.filename
							elif node.__class__.__name__ == 'ProcessNode':
								data = node.pidname+'('+node.pid+')'
							elif node.__class__.__name__ == 'NetworkNode':
								data = node.sourceIP+':'+node.sourcePort + '->' +node.desIP+':'+node.desPort
							elif node.__class__.__name__ == 'NetworkNode2':
								data = node.sourceIP+':'+node.sourcePort
							S_node[hold_nodes[local]+','+name_node_list[local]].append((nodeid,data))
							if self.resultgraph.has_node(nodeid):
								self.resultgraph.remove_node(nodeid)
						
						'''
						path_edges = pathedges[str(pathid)]
						edges_converted = []
						for edgeid in path_edges:
							edgetwo = []
							try:
								edge_tuple = (self.originalgraph[edgeid[0]][edgeid[1]], (edgeid[0],edgeid[1]))
							except KeyError:
								edge_tuple = 'None'
							edgetwo.append(edge_tuple)
							try:
								edge_tuple = (self.originalgraph[edgeid[1]][edgeid[0]], (edgeid[1],edgeid[0]))
							except KeyError:
								edge_tuple = 'None'
							edgetwo.append(edge_tuple)
							for edge_tuple in edgetwo:
								if edge_tuple == 'None':
									continue
								else:
									edges_converted.append(edge_tuple[1])
						
						for local,edgeid in enumerate(edges_converted):
							sourceid = edgeid[0]
							sinkid = edgeid[1]
							edge = self.originalgraph[sourceid][sinkid][0]
							event = edge['data_edge'].event
							starttime = edge['data_edge'].starttime
							endtime = edge['data_edge'].endtime
							size = edge['data_edge'].size
							data = sourceid+','+sinkid+','+event+','+starttime+','+endtime+','+str(size)
							#print local
							#print name_edge_list
							S_edge[name_edge_list[local]].append(data)
							holdedgeid = hold_edges[local]
							holdedge = self.resultgraph[holdedgeid[0]][holdedgeid[1]][0]
							holdstarttime = holdedge['data_edge'].starttime
							holdendtime = holdedge['data_edge'].endtime
							if de.Decimal(starttime) < de.Decimal(holdstarttime):
								holdedge['data_edge'].starttime = starttime
							if de.Decimal(endtime) > de.Decimal(holdendtime):
								holdedge['data_edge'].endtime = endtime
							holdedge['data_edge'].size += float(size)
						'''
				for key in S_node:
					n = 0
					for i in S_node[key]:
						n += 1
						f_node.write('group'+str(groupid)+',')
						f_node.write(str(n)+','+key+',')
						f_node.write(i[0]+','+i[1])
						f_node.write('\n')
				'''
				for key in S_edge:
					n = 0
					for i in S_edge[key]:
						n += 1
						f_edge.write('group'+str(groupid)+',')
						f_edge.write(str(n)+','+key+',')
						f_edge.write(i)
						f_edge.write('\n')
				'''
		return self.resultgraph


