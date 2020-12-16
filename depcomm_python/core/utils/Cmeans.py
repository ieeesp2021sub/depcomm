from skfuzzy.cluster import cmeans
from ExportResult import ExportResult
import numpy as np

class Cmeans:

	@classmethod
	def cluster(cls, filename, meth, c, graph=None, issplit=False, ismergepath=False):
		#print 'clusting...'
		fr = open('./detection_file/'+filename+'_'+meth+'_vector.csv')
		line = fr.readline()
		part_1 = line.split(' ')
		num_data = int(part_1[0])
		dimension = int(part_1[1].rstrip())
		line = fr.readline()
		data = []
		label = []
		while line != '':
			part = line.split(' ')
			node = part[0]
			if 'p' in node:
				data_line = part[1:]
				data_line = [float(i.rstrip()) for i in data_line]
				label.append(node)
				data.append(data_line)
				line = fr.readline()
			else:
				line = fr.readline()

		data = np.array(data)		
		data = data.T
		center, u, u0, d, jm, p, fpc = cmeans(data, m=1.3, c=c, error=0.0001, maxiter=1000)
		u = u.T.tolist()
		z = zip(label,u)
		#print u
		comm2node = ExportResult.exportaffiliation(graph, z, filename, meth, issplit, ismergepath)
		return comm2node,fpc
		#print 'fpc: '+str(fpc)

