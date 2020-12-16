import sys
sys.path.append("..")

def indexfile(graph):
	fw = open('./core/intermediatefiles/nid2name.txt','w')
	nodes = graph.nodes()
	for nid in nodes:
		node_instance = nodes[nid]['data_node']
		fw.write(nid+','+node_instance.unidname)
		if node_instance.__class__.__name__ == 'ProcessNode':
			fw.write(','+node_instance.pidname+','+node_instance.pid+',p')
		elif node_instance.__class__.__name__ == 'FileNode':
			fw.write(','+node_instance.path+','+node_instance.name+',f')
		elif node_instance.__class__.__name__ == 'NetworkNode':
			fw.write(','+node_instance.sourceIP+','+node_instance.desIP+',n')
		fw.write('\n')

	fw.close()

