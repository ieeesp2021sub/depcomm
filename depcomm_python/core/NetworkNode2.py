class NetworkNode2:
	def __init__(self, unid, desIP, desPort):
		self.unid = 'n'+unid
		self.desIP = desIP
		self.desPort = desPort
		self.nodetype = 'network2'
		self.merged = False
		self.unidname = node.desIP+':'+node.desPort


