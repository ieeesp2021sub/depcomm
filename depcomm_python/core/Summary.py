import networkx as nx
import re
import os
import datetime
import sys
import decimal as de
from ExportDOT import ExportDOT
from networkx.drawing.nx_pydot import write_dot

from utils.Graph2Json import json2graph

class Summary:

	def __init__(self, inpath, detection):
		self.inpath = inpath
		self.detection = detection

	def run(self):
		print 'summarizing...'
		POI = self.detection

		pPattern = re.compile(r'(?P<pidname>.+?)'+'\((?P<pid>\d+)\)')

		path = self.inpath
		graph = json2graph(path)

		name2id = {}
		id2name = {}
		fr_nodeindex = open('./core/intermediatefiles/nid2name.txt')
		line = fr_nodeindex.readline()
		while line != '':
			line = line.rstrip()
			part = line.split(',')
			nid = part[0]
			name = part[1]
			name2id[name] = [nid,part[2],part[3],part[4]]
			id2name[nid] = [name,part[2],part[3],part[4]]
			line = fr_nodeindex.readline()


		def in_neighbor(graph, node):
			in_node = []
			for i in list(graph.in_edges(node)):
				in_node.append(i[0])
			return in_node

		def getfather(graph, node):
			nodes = graph.nodes()
			in_neighbors = in_neighbor(graph, node)
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

		fm = open('./output/'+path+'_HRW_community_merged.txt')
		comm2node = {}
		line = fm.readline()
		while line != '':
			line = line.rstrip()
			part = line.split(',')
			comm = part[0]
			#numm = part[-1]
			nodes = part[1:-1]
			nidlist = []
			for node in nodes:
				nidlist.append(name2id[node][0])
			comm2node[comm] = nidlist
			line = fm.readline()

		node2comm = {}
		for c in comm2node:
			for n in comm2node[c]:
				if node2comm.has_key(n):
					node2comm[n].append(c)
				else:
					node2comm[n] = [c]


		inter_community_input = {}
		inter_community_output = {}
		edges = list(graph.edges())
		for edge in edges:
			source = edge[0]
			sink = edge[1]
			if node2comm.has_key(source) and node2comm.has_key(sink):
				source_c = set(node2comm[source])
				sink_c = set(node2comm[sink])
				if source_c & sink_c:continue
				for c in list(source_c):
					if inter_community_output.has_key(c):
						inter_community_output[c].append(source)
					else:
						inter_community_output[c] = [source]
				for c in list(sink_c):
					if inter_community_input.has_key(c):
						inter_community_input[c].append(sink)
					else:
						inter_community_input[c] = [sink]

		paths_file = open('./output/summary.txt','w')
		
		def inspect_time(paths_id):
			paths_new = []
			for path in paths_id:
				f = True
				i = 0
				while i < len(path)-2:
					sourcenode_pre = path[i]
					sinknode_pre = path[i+1]
					sourcenode_cur = path[i+1]
					sinknode_cur = path[i+2]
					path_pre_starttime = de.Decimal(graph[sourcenode_pre][sinknode_pre][0]['data_edge'].starttime)
					path_cur_endtime = de.Decimal(graph[sourcenode_cur][sinknode_cur][0]['data_edge'].endtime)
					if path_pre_starttime > path_cur_endtime:
						f = False
						break

					i += 1
				if f:
					paths_new.append(path)
			return paths_new
		
		comm_input = {}
		comm_output = {}
		comm_graph = {}
		for c in comm2node:
			node_list = comm2node[c]
			inputs = []
			outputs = []
			if inter_community_output.has_key(c):
				outputs = outputs+inter_community_output[c]
			if inter_community_input.has_key(c):
				inputs = inputs+inter_community_input[c]
			sub = graph.subgraph(node_list)
			comm_graph[c] = sub
			for node in node_list:
				if 'n' in node:
					inputs.append(node)
				if id2name[node][0] == POI:
					outputs.append(node)
				if len(node2comm[node]) >= 2:
					if sub.in_degree(node):
						outputs.append(node)
					if sub.out_degree(node):
						inputs.append(node)
	
			if not inputs:
				for node in sub.nodes():
					if sub.nodes()[node]['data_node'].__class__.__name__ == 'ProcessNode':
						father = getfather(sub, node)
						if father == 'none':
							inputs.append(node)

			edges = list(sub.edges())
			starttimes = []
			endtimes = []
			for edge in edges:
				starttimes.append(de.Decimal(sub[edge[0]][edge[1]][0]['data_edge'].starttime))
				endtimes.append(de.Decimal(sub[edge[0]][edge[1]][0]['data_edge'].endtime))
			time_err = max(endtimes) - min(starttimes)
			max_endtime = max(endtimes).to_eng_string()
			max_endtime = max_endtime.split('.')[0]
			min_starttime = min(starttimes).to_eng_string()
			min_starttime = min_starttime.split('.')[0]
			startArray_end = datetime.datetime.fromtimestamp(int(max_endtime))
			endtime = startArray_end.strftime("%Y-%m-%d %H:%M:%S")
			startArray_start = datetime.datetime.fromtimestamp(int(min_starttime))
			starttime = startArray_start.strftime("%Y-%m-%d %H:%M:%S")

			sourceids = [source for source in list(set(inputs))]
			targetids = [target for target in list(set(outputs))]
			comm_input[c] = list(set(inputs))
			comm_output[c] = list(set(outputs))

			paths_file.write(c+': ')
			paths_file.write('\n')
			
			paths = []
			for sourceid in sourceids:
				for targetid in targetids:
					if sourceid == targetid:continue
					#path_generator = nx.all_shortest_paths(sub,sourceid,targetid)
					try:
						path_generator = nx.all_simple_paths(sub,sourceid,targetid)
						#paths_id = nx.shortest_path(sub,sourceid,targetid)
						paths_id = [p for p in path_generator]
						paths_id_ = inspect_time(paths_id)
						lengths = [len(p) for p in paths_id_]
						#print lengths
						max_index = lengths.index(max(lengths))
						#print max_index
						paths_id_i = paths_id_[max_index]
						#print paths_id
					except Exception:
						continue
					paths_name = []
					for i in paths_id_i:
						paths_name.append(id2name[i][0])
			
					i = 0
					total_score = 0
					is_input_process = False
					is_output_process = False
					is_POI = False
					while i < len(paths_name)-1:
						sourcenode = paths_name[i]
						sinknode = paths_name[i+1]
						if i == 0:
							path_starttime = de.Decimal(sub[name2id[sourcenode][0]][name2id[sinknode][0]][0]['data_edge'].starttime)
						if i == len(paths_name)-2:
							path_endtime = de.Decimal(sub[name2id[sourcenode][0]][name2id[sinknode][0]][0]['data_edge'].endtime)

						source_match = pPattern.match(sourcenode)
						sink_match = pPattern.match(sinknode)
						if source_match:
							if i == 0:
								is_input_process = True
							sourcenode = source_match.group('pidname')
						if sink_match:
							if i == len(paths_name)-2:
								is_output_process = True
							sinknode = sink_match.group('pidname')
						if i == len(paths_name)-2:
							if sinknode == POI:
								is_POI = True
						i += 1

					path_time_err = path_endtime - path_starttime
					if path_time_err < 0:continue
					if is_input_process and is_output_process:
						path_score = de.Decimal(de.Decimal(1.0)*path_time_err/time_err+de.Decimal(1.0))/de.Decimal(3)
					elif is_input_process and is_POI:
						path_score = de.Decimal(de.Decimal(1.0)*path_time_err/time_err+de.Decimal(1.5))/de.Decimal(3)
					elif is_input_process:
						path_score = de.Decimal(de.Decimal(1.0)*path_time_err/time_err+de.Decimal(0.5))/de.Decimal(3)
					elif is_output_process:
						path_score = de.Decimal(de.Decimal(1.0)*path_time_err/time_err+de.Decimal(0.5))/de.Decimal(3)
					elif is_POI:
						path_score = de.Decimal(de.Decimal(1.0)*path_time_err/time_err+de.Decimal(1.0))/de.Decimal(3)
					else:
						path_score = de.Decimal(de.Decimal(1.0)*path_time_err/time_err)/de.Decimal(3)

					paths.append((paths_name,path_score))
			
			for node in sub.nodes():
				if sub.nodes()[node]['data_node'].__class__.__name__ == 'ProcessNode':
					father = getfather(sub, node)
					if father == 'none':
						paths_file.write(sub.nodes()[node]['data_node'].pidname)
						paths_file.write('\n')
						break

			paths_file.write(starttime+'->'+endtime)
			paths_file.write('\n')
			paths.sort(key=lambda x:x[1],reverse=True)
			for p_s in paths:
				paths_file.write(','.join(p_s[0]))
				paths_file.write(','+str(p_s[1]))
				paths_file.write('\n')
		
		# generating summary graph
		def _time(node,c1,c2):
			f = False
			net1 = comm_graph[c1]
			inedges = list(net1.in_edges(node))
			net2 = comm_graph[c2]
			outedges = list(net2.out_edges(node))
			for inedge in inedges:
				st = de.Decimal(net1[inedge[0]][inedge[1]][0]['data_edge'].starttime)
				for outedge in outedges:
					et = de.Decimal(net2[outedge[0]][outedge[1]][0]['data_edge'].endtime)
					if st < et:
						f = True
						break
				if f:
					break
			return f
		
		for c in comm_graph:
			ex = ExportDOT(comm_graph[c])
			ex.export('./output/community_'+c+'.dot')
			#os.system('dot -Tsvg ./output/community_'+c+'.dot'+' -o ./output/community_'+c+'.svg')

		edges = list(graph.edges())
		
		graph_summary = nx.MultiDiGraph() 
		for c in comm_input:
			graph_summary.add_node(c,label='C'+c,shape='box')
			for k in comm_output:
				if c == k:continue
				for i in comm_output[k]:
					if i in comm_input[c]:
						time_ = _time(i,k,c)
						if time_:
							graph_summary.add_node(k,label='C'+k,shape='box')
							graph_summary.add_edge(k,c,label=id2name[i][0])
					for j in comm_input[c]:
						if (i,j) in edges:
							graph_summary.add_node(k,label='C'+k,shape='box')
							edge_name = id2name[i][0]+'->'+id2name[j][0]
							graph_summary.add_edge(k,c,label=edge_name)
		
		write_dot(graph_summary, './output/summary_graph.dot')
		#os.system('dot -Tsvg ./output/summary_graph.dot'+' -o ./output/summary_graph.svg')
		#print list(graph_summary.edges())

