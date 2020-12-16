class NetworkNode:
	def __init__(self, unid, sourceIP, sourcePort, desIP, desPort):
		self.unid = 'n'+unid
		self.sourceIP = sourceIP
		self.sourcePort = sourcePort
		self.desIP = desIP
		self.desPort = desPort
		self.nodetype = 'network'
		self.merged = False
		self.unidname = sourceIP+':'+sourcePort+'->'+desIP+':'+desPort


