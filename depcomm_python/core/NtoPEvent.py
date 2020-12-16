class NtoPEvent:
	
	def __init__(self, sourceN, sinkP, starttime, size, event):
		self.sourceN = sourceN
		self.sinkP = sinkP
		self.starttime = starttime
		self.endtime = ''
		self.event = event
		self.size = size
		self.eventtype = 'NtoP'
		self.merged = False

	def setEndtime(self, endtime):
		self.endtime = endtime

