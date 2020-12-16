class PtoPEvent:
	
	def __init__(self, sourceP, sinkP, starttime, event):
		self.sourceP = sourceP
		self.sinkP = sinkP
		self.starttime = starttime
		self.endtime = ''
		self.size = 0.0
		self.event = event
		self.eventtype = 'PtoP'
		self.merged = False
		self.direct = 'forward'

	def setEndtime(self, endtime):
		self.endtime = endtime
	
	def setDirect(self, direct):
		self.direct = direct

