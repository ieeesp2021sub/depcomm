class PtoFEvent:
	
	def __init__(self, sourceP, sinkF, starttime, size, event):
		self.sourceP = sourceP
		self.sinkF = sinkF
		self.starttime = starttime
		self.endtime = ''
		self.event = event
		self.size = size
		self.eventtype = 'PtoF'
		self.merged = False

	def setEndtime(self, endtime):
		self.endtime = endtime

