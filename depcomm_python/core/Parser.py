import re
import decimal as de
from time import time
from ProcessNode import ProcessNode
from FileNode import FileNode
from NetworkNode import NetworkNode
from NetworkNode2 import NetworkNode2
from EventList import EventList
from BidrProcess import BidrProcess
from PtoPEvent import PtoPEvent
from PtoFEvent import PtoFEvent
from FtoPEvent import FtoPEvent
from PtoNEvent import PtoNEvent
from NtoPEvent import NtoPEvent

class Parser:

	pattern = re.compile(
					r'(?P<timestamp>\d+\.\d+) '+
					'(?P<cpu>\d+) '+
					'(?P<process>.+?) '+
					'\((?P<pid>\d+)\) '+
					'(?P<direction>>|<) '+
					'(?P<event>.+?) '+
					'cwd=(?P<cwd>.+?) '+
					'(?P<args>.*?) '+
					'latency=(?P<latency>\d+)'
					)
	pattern_file = re.compile(r'fd=(?P<fd>\d+)\(<f>(?P<path>.+?)\)')
	pattern_processfile = re.compile('filename=(?P<path>[^ ]+)')
	pattern_socket = re.compile(r'(?:(?:fd)|(?:res))=(?P<fd>\d+)\((?:(?:<4t>)|(?:<4u>))(?P<sourceIP>\d+\.\d+\.\d+\.\d+):(?P<sourcePort>\d+)' +
					'->(?P<desIP>\d+\.\d+\.\d+\.\d+):(?P<desPort>\d+)\)')
	pattern_size = re.compile(r'res=(?P<size>\d+)')
	pattern_parent = re.compile(r'ptid=(?P<parentPID>\d+)\((?P<parent>.+?)\)')
	pattern_child = re.compile(r'res=(?P<childPID>\d+)\((?P<child>.+?)\)')
	pattern_args = re.compile(r'args=(?P<arguments>.*?) tid=')

	process_entity = {}
	file_entity = {}
	network_entity = {}

	process_uid = 0
	file_uid = 0
	network_uid = 0

	forwardupdate = {}
	backupdate = {}

	PtoPKeydict = {}
	eventtmp = {}
	removedPtoP = set()
	newtoremoved = {}

	process_argus = {}
	
	def __init__(self, pathlog):
		self.pathlog = pathlog
		self.PtoPDict = {}
		self.PtoFDict = {}
		self.FtoPDict = {}
		self.PtoNDict = {}
		self.NtoPDict = {}

	def parseLog(self, onlydesIP, process_bidirection):
		print "Parsing..."
		begin_time = time()

		start_search_dict = {}
		text = open(self.pathlog)
		line = text.readline()
		line = line.rstrip()
		while line != '':
			search_line = Parser.pattern.search(line)
			if search_line:
				args = search_line.group('args')
				search_file = Parser.pattern_file.search(args)
				#search_parent = Parser.pattern_parent.search(args)
				search_child = Parser.pattern_child.search(args)

				if search_line.group('process') == 'mv' and search_line.group('direction') == '<' and search_line.group('event') == '<unknown>':
					search_line = self.correctedmv(search_line)

				if search_line.group('direction') == '>':
					key = search_line.group('timestamp')+':'+search_line.group('event')+':'+search_line.group('cwd')
					start_search_dict[key] = search_line
				else:
					self.findStartandend(start_search_dict,search_line,onlydesIP,process_bidirection)
			line = text.readline().rstrip()
		end_time = time()

		self.writeargustoprocess()
		print "Parser is over"
		print "Parsing time is: "+str(end_time-begin_time)

	def findStartandend(self, start_search_dict, search_end, onlydesIP,process_bidirection):
		starttime = (de.Decimal(search_end.group('timestamp'))-de.Decimal(search_end.group('latency')).scaleb(-9)).to_eng_string()
		key = starttime+':'+search_end.group('event')+':'+search_end.group('cwd')
		if start_search_dict.has_key(key):
			search_start = start_search_dict.pop(key)
		else:
			dummy_str = '%s %s %s %s (%s) %s %s cwd=%s !dummy! latency=%s' % (
							'0', starttime, search_end.group('cpu'), search_end.group('process'), search_end.group('pid'), 
							'>', search_end.group('event'), search_end.group('cwd'), search_end.group('latency'))
			search_start = Parser.pattern.search(dummy_str)
		
		start_entity = self.extractEntity(search_start, onlydesIP)
		end_entity = self.extractEntity(search_end, onlydesIP)
		
		self.addEvent(search_start, search_end, start_entity, end_entity, process_bidirection) 

	def extractEntity(self, search_line, onlydesIP):
		entity_list = ['']*2
		pidname = search_line.group('process')
		pid = search_line.group('pid')
		#cwd = search_line.group('cwd')
		processKey = pidname+':'+pid

		if Parser.process_entity.has_key(processKey):
			puid = str(Parser.process_entity[processKey])
		else:
			Parser.process_uid += 1
			Parser.process_entity[processKey] = Parser.process_uid
			puid = str(Parser.process_uid)
		
		args = search_line.group('args')
		search_file = Parser.pattern_file.search(args)
		search_processfile = Parser.pattern_processfile.search(args)
		search_socket = Parser.pattern_socket.search(args)
		search_parent = Parser.pattern_parent.search(args)
		search_child = Parser.pattern_child.search(args)
		search_args = Parser.pattern_args.search(args)
		if search_args:
			arguments = search_args.group('arguments')
			Parser.process_argus[processKey] = arguments

		entity_list[0] = ProcessNode(puid, pid, pidname)

		if search_file:
			path = search_file.group('path')

			if '(' in path:
				path = path[path.find('(')+1:len(path)-1]
			
			fileKey = path
			if Parser.file_entity.has_key(fileKey):
				fuid = str(Parser.file_entity[fileKey])
			else:
				Parser.file_uid += 1
				Parser.file_entity[fileKey] = Parser.file_uid
				fuid = str(Parser.file_uid)

			entity_list[1] = FileNode(fuid, path)

		elif search_processfile:
			path = search_processfile.group('path')
			if '(' in path:
				path = path[path.find('(')+1:len(path)-1]
			
			if path != '<NA>':
				fileKey = path
				if Parser.file_entity.has_key(fileKey):
					fuid = str(Parser.file_entity[fileKey])
				else:
					Parser.file_uid += 1
					Parser.file_entity[fileKey] = Parser.file_uid
					fuid = str(Parser.file_uid)

				entity_list[1] = FileNode(fuid, path)
			
		elif search_socket:
			sourceIP = search_socket.group('sourceIP')
			sourcePort = search_socket.group('sourcePort')
			desIP = search_socket.group('desIP')
			desPort = search_socket.group('desPort')

			if onlydesIP:
				networkKey = desIP+":"+desPort
			else:
				networkKey = sourceIP+":"+sourcePort+"->"+ desIP+":"+desPort
			
			if Parser.network_entity.has_key(networkKey):
				nuid = str(Parser.network_entity[networkKey])
			else:
				Parser.network_uid += 1 
				Parser.network_entity[networkKey] = Parser.network_uid
				nuid = str(Parser.network_uid)
			
			if onlydesIP:
				entity_list[1] = NetworkNode2(nuid, desIP, desPort)
			else:
				entity_list[1] = NetworkNode(nuid, sourceIP, sourcePort, desIP, desPort)
		
		elif search_parent:
			ptidname = search_parent.group('parent')
			ptid = search_parent.group('parentPID')
			parentKey = ptidname+':'+ptid

			if Parser.process_entity.has_key(parentKey):
				ptuid = str(Parser.process_entity[parentKey])
			else:
				Parser.process_uid += 1 
				Parser.process_entity[parentKey] = Parser.process_uid
				ptuid = str(Parser.process_uid)

			if search_child:
				ctidname = search_child.group('child')
				ctid = search_child.group('childPID')
				childKey = ctidname+':'+ctid
				if Parser.process_entity.has_key(childKey):
					ctuid = str(Parser.process_entity[childKey])
				else:
					Parser.process_uid += 1
					Parser.process_entity[childKey] = Parser.process_uid
					ctuid = str(Parser.process_uid)					
				entity_list[1] = ProcessNode(ctuid, ctid, ctidname)
		
			else:
				entity_list[1] = ProcessNode(ptuid, ptid, ptidname)

		return entity_list

	def addEvent(self, search_start, search_end, start_entity, end_entity, process_bidirection):
		start_source = start_entity[0]
		start_sink = start_entity[1]
		end_source = end_entity[0]
		end_sink = end_entity[1]

		event = search_end.group('event')
		starttime = search_start.group('timestamp')
		endtime = search_end.group('timestamp')
		cwd = search_end.group('cwd')
		key = starttime+':'+event+':'+cwd
		
		if event in EventList.PtoPList:
			args = search_end.group('args')
			child_search = Parser.pattern_child.search(args)
			if child_search:
				if end_sink.__class__.__name__ == 'ProcessNode':
					forwardptop = PtoPEvent(end_source, end_sink, starttime, event)
					forwardptop.setEndtime(endtime)
					self.PtoPDict[key] = forwardptop
					Parser.forwardupdate[end_sink.pidname+':'+end_sink.pid] = forwardptop

					backptop = PtoPEvent(end_sink, end_source, starttime, event)
					backptop.setEndtime(endtime)
					backptop.setDirect('back')
					if process_bidirection:
						self.PtoPDict[key+'back'] = backptop
					elif (end_source.pidname,end_sink.pidname) in BidrProcess.processpair:
						self.PtoPDict[key+'back'] = backptop
					Parser.backupdate[end_sink.pidname+':'+end_sink.pid] = backptop
					Kkey = end_source.pid+':'+end_sink.pid
					if Parser.PtoPKeydict.has_key(Kkey):
						Parser.PtoPKeydict[Kkey].append(key)
					else:
						Parser.PtoPKeydict[Kkey] = [key]

		if event == 'execve':
			args = search_end.group('args')
			search_parent = Parser.pattern_parent.search(args)
			if 'res=0' in args:
				if search_parent:
					if end_sink.__class__.__name__ == 'ProcessNode':
						forwardptop = PtoPEvent(end_sink, end_source, starttime, event)
						forwardptop.setEndtime(endtime)
						backptop = PtoPEvent(end_source, end_sink, starttime, event)
						backptop.setEndtime(endtime)
						backptop.setDirect('back')
						Kkey = end_sink.pid+':'+end_source.pid
						#print Kkey
						if Parser.PtoPKeydict.has_key(Kkey):
							for i in Parser.PtoPKeydict[Kkey]:
								if self.PtoPDict.has_key(i):
									removed = self.PtoPDict.pop(i)
									removedsink = removed.sinkP.pidname+':'+removed.sinkP.pid
									if process_bidirection:
										self.PtoPDict.pop(i+'back')
									#elif (end_sink.pidname,end_source.pidname) in BidrProcess.processpair:
									#	self.PtoPDict.pop(i+'back')
									if removedsink != end_source.pidname+':'+end_source.pid:
										Parser.removedPtoP.add(removedsink)
									Parser.newtoremoved[end_source.pid] = removedsink

							
								if Parser.newtoremoved.has_key(end_source.pid):
									r = Parser.newtoremoved[end_source.pid]
									if Parser.eventtmp.has_key(r):
										self.alter(r, end_source)
							
						self.PtoPDict[key] = forwardptop
						if process_bidirection:
							self.PtoPDict[key+'back'] = backptop
						elif (end_sink.pidname,end_source.pidname) in BidrProcess.processpair:
							self.PtoPDict[key+'back'] = backptop

						Parser.forwardupdate[end_source.pidname+':'+end_source.pid] = forwardptop
						Parser.backupdate[end_source.pidname+':'+end_source.pid] = backptop

				if start_sink.__class__.__name__ == 'FileNode':
					ftop = FtoPEvent(start_sink, end_source, starttime, 0, event)
					ftop.setEndtime(starttime)
					self.FtoPDict[key] = ftop

		if event in EventList.PtoFList:
			if start_sink.__class__.__name__ == 'FileNode':
				self.updataPtoPendtime(end_source, endtime)

				args = search_end.group('args')
				size_search = Parser.pattern_size.search(args)
				if size_search:
					size = size_search.group('size')
					if start_source.__class__.__name__ == 'ProcessNode':
						Pkey = start_source.pidname+':'+start_source.pid
						if Parser.eventtmp.has_key(Pkey):
							Parser.eventtmp[Pkey].append(key)
						else:
							Parser.eventtmp[Pkey] = [key]
						
						if Pkey not in Parser.removedPtoP:
							ptof = PtoFEvent(start_source, start_sink, starttime, float(size), event)
							ptof.setEndtime(endtime)
							self.PtoFDict[key] = ptof
				

		if event in EventList.FtoPList:
			if start_sink.__class__.__name__ == 'FileNode':
				self.updataPtoPendtime(end_source, endtime)

				args = search_end.group('args')
				size_search = Parser.pattern_size.search(args)
				if size_search:
					size = size_search.group('size')
					if start_source.__class__.__name__ == 'ProcessNode':
						Pkey = start_source.pidname+':'+start_source.pid
						if Parser.eventtmp.has_key(Pkey):
							Parser.eventtmp[Pkey].append(key)
						else:
							Parser.eventtmp[Pkey] = [key]
						
						if Pkey not in Parser.removedPtoP:
							ftop = FtoPEvent(start_sink, start_source, starttime, float(size), event)
							ftop.setEndtime(endtime)
							self.FtoPDict[key] = ftop

		if event in EventList.PtoNList:
			if start_sink.__class__.__name__ == 'NetworkNode' or start_sink.__class__.__name__ == 'NetworkNode2':
				self.updataPtoPendtime(end_source, endtime)
			
				args = search_end.group('args')
				size_search = Parser.pattern_size.search(args)
				if size_search:
					size = size_search.group('size')
					if start_source.__class__.__name__ == 'ProcessNode':
						Pkey = start_source.pidname+':'+start_source.pid
						if Parser.eventtmp.has_key(Pkey):
							Parser.eventtmp[Pkey].append(key)
						else:
							Parser.eventtmp[Pkey] = [key]
					
						if Pkey not in Parser.removedPtoP:
							pton = PtoNEvent(start_source, start_sink, starttime, float(size), event)
							pton.setEndtime(endtime)
							self.PtoNDict[key] = pton


		if event in EventList.NtoPList:
			if start_sink.__class__.__name__ == 'NetworkNode' or start_sink.__class__.__name__ == 'NetworkNode2':
				self.updataPtoPendtime(end_source, endtime)

				args = search_end.group('args')
				size_search = Parser.pattern_size.search(args)
				if size_search:
					size = size_search.group('size')
					if start_source.__class__.__name__ == 'ProcessNode':
						Pkey = start_source.pidname+':'+start_source.pid
						if Parser.eventtmp.has_key(Pkey):
							Parser.eventtmp[Pkey].append(key)
						else:
							Parser.eventtmp[Pkey] = [key]
						
						if Pkey not in Parser.removedPtoP:
							ntop = NtoPEvent(start_sink, start_source, starttime, float(size), event)
							ntop.setEndtime(endtime)
							self.NtoPDict[key] = ntop

		if event == 'accept':
			if end_sink.__class__.__name__ == 'NetworkNode' or end_sink.__class__.__name__ == 'NetworkNode2':
				self.updataPtoPendtime(end_source, endtime)

				if end_source.__class__.__name__ == 'ProcessNode':
					Pkey = end_source.pidname+':'+end_source.pid
					if Parser.eventtmp.has_key(Pkey):
						Parser.eventtmp[Pkey].append(key)
					else:
						Parser.eventtmp[Pkey] = [key]
					
					if Pkey not in Parser.removedPtoP:
						pton = PtoNEvent(end_source, end_sink, starttime, 0, event)
						pton.setEndtime(endtime)
						self.PtoNDict[key] = pton
				
						ntop = NtoPEvent(end_sink, end_source, starttime, 0, event)
						ntop.setEndtime(endtime)
						self.NtoPDict[key] = ntop

		if event == 'fcntl':
			if start_sink.__class__.__name__ == 'NetworkNode' or start_sink.__class__.__name__ == 'NetworkNode2':
				self.updataPtoPendtime(end_source, endtime)
				
				if start_source.__class__.__name__ == 'ProcessNode':
					Pkey = start_source.pidname+':'+start_source.pid
					if Parser.eventtmp.has_key(Pkey):
						Parser.eventtmp[Pkey].append(key)
					else:
						Parser.eventtmp[Pkey] = [key]

					if Pkey not in Parser.removedPtoP:
						ntop = NtoPEvent(start_sink, start_source, starttime, 0, event)
						ntop.setEndtime(endtime)
						self.NtoPDict[key] = ntop

			if end_sink.__class__.__name__ == 'NetworkNode' or end_sink.__class__.__name__ == 'NetworkNode2':
				self.updataPtoPendtime(end_source, endtime)
				
				if end_source.__class__.__name__ == 'ProcessNode':
					Pkey = end_source.pidname+':'+end_source.pid
					if Parser.eventtmp.has_key(Pkey):
						Parser.eventtmp[Pkey].append(key)
					else:
						Parser.eventtmp[Pkey] = [key]

					if Pkey not in Parser.removedPtoP:
						ntop = NtoPEvent(end_sink, end_source, starttime, 0, event)
						ntop.setEndtime(endtime)
						self.NtoPDict[key] = ntop
	
		if event == 'rename':
			self.updataPtoPendtime(end_source, endtime)

			args = search_end.group('args')
			oldPath = args[args.find("oldpath=")+8:args.rfind(" newpath")]
			newPath = args[args.find("newpath=")+8:args.rfind(" ")]
			if oldPath.endswith(')'): 
				oldPath = oldPath[oldPath.find("(")+1:len(oldPath)-1]
			if newPath.endswith(")"): 
				newPath = newPath[newPath.find("(")+1:len(newPath)-1]
			
			if end_source.__class__.__name__ == 'ProcessNode':
				Pkey = end_source.pidname+':'+end_source.pid
				if Parser.eventtmp.has_key(Pkey):
					Parser.eventtmp[Pkey].append(key)
				else:
					Parser.eventtmp[Pkey] = [key]

				if Pkey not in Parser.removedPtoP:

					fileKey = oldPath	
					if Parser.file_entity.has_key(fileKey):
						fuid = str(Parser.file_entity[fileKey])
					else:
						Parser.file_uid += 1
						Parser.file_entity[fileKey] = Parser.file_uid
						fuid = str(Parser.file_uid)
					of = FileNode(fuid, oldPath)
			
					ftop = FtoPEvent(of, end_source, starttime, 0, event)                                                                                
					ftop.setEndtime(endtime)
					self.FtoPDict[key] = ftop

					fileKey = newPath
					if Parser.file_entity.has_key(fileKey):
						fuid = str(Parser.file_entity[fileKey])
					else:
						Parser.file_uid += 1
						Parser.file_entity[fileKey] = Parser.file_uid
						fuid = str(Parser.file_uid)
					nf = FileNode(fuid, newPath)

					ptof = PtoFEvent(end_source, nf, starttime, 0, event)
					ptof.setEndtime(endtime)
					self.PtoFDict[key] = ptof

	def updataPtoPendtime(self, end_source, endtime):
		key = end_source.pidname+':'+end_source.pid
		if Parser.forwardupdate.has_key(key):
			forward = Parser.forwardupdate[key]
			if de.Decimal(forward.endtime) < de.Decimal(endtime):
				forward.setEndtime(endtime)

		if Parser.backupdate.has_key(key):
			back = Parser.backupdate[key]
			if de.Decimal(back.endtime) < de.Decimal(endtime):
				back.setEndtime(endtime)
				#print back.sourceP.pidname+'('+back.sourceP.pid+')'+'->'+back.sinkP.pidname+'('+back.sinkP.pid+')'+' '+back.endtime
			
	def alter(self, sourcekey, targetentity):
		for i in Parser.eventtmp[sourcekey]:
			if self.PtoFDict.has_key(i):
				self.PtoFDict[i].sourceP = targetentity
			if self.FtoPDict.has_key(i):
				self.FtoPDict[i].sinkP = targetentity
			if self.PtoNDict.has_key(i):
				self.PtoNDict[i].sourceP = targetentity
			if self.NtoPDict.has_key(i):
				self.NtoPDict[i].sinkP = targetentity

	def correctedmv(self, search_line):
		mv_pid = {'19803':['/home/lishi/.cache/abrt/lastnotification.R57hJ9HC','/home/lishi/.cache/abrt/lastnotification'],
				  '19905':['(/home/lishi/tcpdump-4.9.2.tar.gz)','(/home/lishi/tcpdump.tar.gz)'],
				  '22457':['/home/wangwu/.cache/abrt/lastnotification.vi3ZA3NH','/home/wangwu/.cache/abrt/lastnotification']
				  }
		
		pid = search_line.group('pid')
		if mv_pid.has_key(pid):
			new_line = '%s %s %s %s (%s) %s %s cwd=%s res=0 oldpath=%s newpath=%s  latency=%s' % (
					'0', search_line.group('timestamp'), search_line.group('cpu'), search_line.group('process'), 
					pid, '<', 'rename', search_line.group('cwd'), mv_pid[pid][0], mv_pid[pid][1], search_line.group('latency'))
			return Parser.pattern.search(new_line)
		
		else:
			print 'error: the pid is not for mv'
			return search_line

	def writeargustoprocess(self):
		for key in self.PtoPDict:
			sourceP = self.PtoPDict[key].sourceP
			keyP = sourceP.pidname+':'+sourceP.pid
			if Parser.process_argus.has_key(keyP):
				sourceP.setArgus(Parser.process_argus[keyP])
			sinkP = self.PtoPDict[key].sinkP
			keyP = sinkP.pidname+':'+sinkP.pid
			if Parser.process_argus.has_key(keyP):
				sinkP.setArgus(Parser.process_argus[keyP])
		
		for key in self.PtoFDict:
			sourceP = self.PtoFDict[key].sourceP
			keyP = sourceP.pidname+':'+sourceP.pid
			if Parser.process_argus.has_key(keyP):
				sourceP.setArgus(Parser.process_argus[keyP])

		for key in self.FtoPDict:
			sinkP = self.FtoPDict[key].sinkP
			keyP = sinkP.pidname+':'+sinkP.pid
			if Parser.process_argus.has_key(keyP):
				sinkP.setArgus(Parser.process_argus[keyP])

		for key in self.PtoNDict:
			sourceP = self.PtoNDict[key].sourceP
			keyP = sourceP.pidname+':'+sourceP.pid
			if Parser.process_argus.has_key(keyP):
				sourceP.setArgus(Parser.process_argus[keyP])

		for key in self.NtoPDict:
			sinkP = self.NtoPDict[key].sinkP
			keyP = sinkP.pidname+':'+sinkP.pid
			if Parser.process_argus.has_key(keyP):
				sinkP.setArgus(Parser.process_argus[keyP])
	

