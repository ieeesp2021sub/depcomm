class FtoPEvent:
	
	def __init__(self, sourceF, sinkP, starttime, size, event):
		self.sourceF = sourceF
		self.sinkP = sinkP
		self.starttime = starttime
		self.endtime = ''
		self.event = event
		self.size = size
		self.eventtype = 'FtoP'
		self.merged = False

	def setEndtime(self, endtime):
		self.endtime = endtime

