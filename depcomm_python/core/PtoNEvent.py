class PtoNEvent:
	
	def __init__(self, sourceP, sinkN, starttime, size, event):
		self.sourceP = sourceP
		self.sinkN = sinkN
		self.starttime = starttime
		self.endtime = ''
		self.event = event
		self.size = size
		self.eventtype = 'PtoN'
		self.merged = False

	def setEndtime(self, endtime):
		self.endtime = endtime

