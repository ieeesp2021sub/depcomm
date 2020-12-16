
class ExportResult:

	@classmethod
	def exportaffiliation(cls, graph, z, filename, meth, issplit, ismergepath):
		# z: list of (nodeid,[probability for community])
		node2comm = {}
		comm2node = {}

		if graph == None:
			#fw = open('./detection_file/'+filename+'_'+meth+'_community.txt','w')
			for i in z:
				fw.write(i[0]+': ')
				for j in i[1]:
					fw.write(str(j)+',')
				fw.write(str(i[1].index(max(i[1]))+1)+'\n')


		else:
			if issplit:
				fr = open('./core/intermediatefiles/split.csv')
				line = fr.readline()
				splitnode = {}
				while line != '':
					part = line.split(',')
					for i in range(len(part)-2):
						if splitnode.has_key(part[0]):
							p = part[i+2].rstrip().split(':')
							splitnode[part[0]].append((p[0],p[1]))
						else:
							p = part[i+2].rstrip().split(':')
							splitnode[part[0]] = [(p[0],p[1])]
					line = fr.readline()
			else:
				splitnode = {}
			
			if ismergepath:
				fr = open('./core/intermediatefiles/nodegroup.csv')
				line = fr.readline()
				mergenode = {}
				while line != '':
					part = line.split(',')
					if part[2] in splitnode:
						for i in splitnode[part[2]]:
							if mergenode.has_key(part[2]+'_'+i[0]):
								mergenode[part[2]+'_'+i[0]].append(part[4].rstrip()+'_'+i[1])
							else:
								mergenode[part[2]+'_'+i[0]] = [part[4].rstrip()+'_'+i[1]]
					else:
						if mergenode.has_key(part[2]):
							mergenode[part[2]].append(part[4].rstrip())
						else:
							mergenode[part[2]] = [part[4].rstrip()]
					line = fr.readline()
			
			else:
				mergenode = {}
			#fw = open('./output/'+filename+'_'+meth+'_community.txt','w')
			#fw_o = open('../detection_file/'+filename+'_'+meth+'_affiliation_original.txt','w')
			
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

			process2file = {}
			fpf = open('./core/intermediatefiles/process2file.txt')
			line = fpf.readline()
			while line != '':
				line = line.rstrip()
				part = line.split(',')
				process = part[0]
				files = part[1:]
				process2file[process] = files
				line = fpf.readline()

			leaf = {}
			fleaf = open('./core/intermediatefiles/leaf.txt')
			line = fleaf.readline()
			while line != '':
				line = line.rstrip()
				part = line.split(',')
				nid = part[0]
				leaf[nid] = part[2:-2]
				line = fleaf.readline()
			
			node2comm_f = {}
			for i in z:
				node = graph.nodes[i[0]]['data_node']
				if i[0] in mergenode:
					for label_name in mergenode[i[0]]:
						fw.write(label_name+','+node2name[label_name]+',')
						for j in i[1]:
							fw.write(str(j)+',')
						fw.write(str(i[1].index(max(i[1]))+1)+'\n')
				else:
					prob = [float(k) for k in i[1]]
					thre = 0.1*max(prob)
					comm = set()
					for index, p in enumerate(prob):
						if p >=thre:
							comm.add(str(index+1))
					node2comm[i[0]] = comm
					if process2file.has_key(i[0]):
						files = process2file[i[0]]
						for f in files:
							#node2comm[f] = comm
							if node2comm_f.has_key(f):
								node2comm_f[f].append(comm)
							else:
								node2comm_f[f] = [comm]
					if leaf.has_key(i[0]):
						leafs = leaf[i[0]]
						for l in leafs:
							node2comm[l] = comm
			
			for f in node2comm_f:
				flag = False
				node2comm[f] = set()
				for c in node2comm_f[f]:
					if len(c) == 1:
						flag = True
						node2comm[f] = node2comm[f] | c
				if not flag:
					for c in node2comm_f[f]:
						node2comm[f] = node2comm[f] | c

			for node in node2comm:
				for c in node2comm[node]:
					if comm2node.has_key(c):
						comm2node[c].add(node)
					else:
						comm2node[c] = set([node])
		
			#for c in comm2node:
			#	fw.write(str(c)+',')
			#	for nodeid in comm2node[c]:
			#		label_name = node2name[nodeid]
			#		fw.write(label_name+',')
			#	fw.write('\n')
		return comm2node
