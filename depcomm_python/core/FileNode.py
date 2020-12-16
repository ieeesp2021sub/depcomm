class FileNode:
	def __init__(self, unid, filename):
		self.unid='f'+unid
		self.filename = filename
		self.nodetype = 'file'
		self.merged = False
		self.unidname = filename

		part0 = filename.split('\\\\')
		part1 = part0[-1].split('.')
		self.path = filename.replace(part0[-1],'')
		if len(part1) == 1:
			self.extension = ''
			self.name = part1[0]
		else:
			self.extension = '.'+part1[-1]
			self.name = part0[-1].replace(self.extension,'')
	



