import networkx as nx
from networkx.drawing.nx_pydot import write_dot

class ExportDOT:
	
	def __init__(self, ingraph):
		self.ingraph = ingraph

	def export(self, expath):
		#print 'export to dot...'
		exgraph = nx.MultiDiGraph()

		nodes = self.ingraph.nodes()
		for node_id in nodes:
			node = nodes[node_id]['data_node']
			if node.__class__.__name__ == 'ProcessNode':
				label = node_id+': '+node.pidname+'('+node.pid+')'
				exgraph.add_node(node_id, label = label, shape = 'box' )

			elif node.__class__.__name__ == 'FileNode':
				label = node_id+': '+node.filename
				exgraph.add_node(node_id, label = label, shape = 'ellipse')

			elif node.__class__.__name__ == 'NetworkNode':
				label = node_id+': '+node.sourceIP+':'+node.sourcePort+'->'+node.desIP+':'+node.desPort
				exgraph.add_node(node_id, label = label, shape = 'parallelogram')
			
			elif node.__class__.__name__ == 'NetworkNode2':
				label = node_id+': '+node.desIP+':'+node.desPort
				exgraph.add_node(node_id, label = label, shape = 'parallelogram')

		edgelist = self.ingraph.edges.items()
		for edgeitem in edgelist:
			source = edgeitem[0][0]
			sink = edgeitem[0][1]
			edge = edgeitem[1]['data_edge']
			if edge.__class__.__name__ == 'PtoPEvent':
				label = source+'->'+sink+': '+edge.event
			else:
				label = source+'->'+sink+': '+edge.event
			exgraph.add_edge(source, sink, label = label)

		write_dot(exgraph, expath)
		#print 'dot is generated'


