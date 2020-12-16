import re

class ProcessNode:
	pattern1 = re.compile(r'www.(?P<ignore>.*?).com')

	def __init__(self, unid, pid, pidname):
		self.unid = 'p'+unid
		self.pid = pid
		self.pidname = pidname
		self.nodetype = 'process'
		self.merged = False
		self.argus = '-'
		self.unidname = pidname+'('+pid+')'
	def	setArgus(self, arguments):
		search1 = ProcessNode.pattern1.search(arguments)
		if search1:
			ig = search1.group('ignore')
			arguments = arguments.replace(ig,'~')
		if arguments != '' and arguments != ' ':
			self.argus = arguments

	
