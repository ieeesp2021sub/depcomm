import networkx as nx
import numpy as np
from skfuzzy.cluster import cmeans
from utils.Multigraph2graph import Multigraph2graph
from utils.ExportResult import ExportResult

class FCM:
	def __init__(self,graph,cluster_num,k):
		self.graph = Multigraph2graph(graph)
		self.cluster_num = cluster_num
		self.k = k

	def fcm(self, filename, meth, issplit, ismergepath):

		Adjacent, nodelist = self.adjacent(self.graph)

		Laplacian = self.laplacianMatrix(Adjacent)

		x, v = np.linalg.eig(Laplacian)
		dictEigval = dict(zip(x, range(len(x))))
		x_k=np.sort(x)[0:self.k]
		ix=[dictEigval[k] for k in x_k]

		v_k = v[:,ix].T
		
		center, u, u0, d, jm, p, fpc = cmeans(v_k, m=2, c=self.cluster_num, error=0.001, maxiter=1000)
		u = u.T.tolist()
		z = zip(nodelist,u)

		ExportResult.exportaffiliation(self.graph, z, filename, meth, issplit, ismergepath)

	def adjacent(self,graph):
		nodes = graph.nodes()
		nodelist = list(nodes)
		A = np.array(nx.adjacency_matrix(graph, nodelist=nodelist).todense())
		return A,nodelist

	def laplacianMatrix(self,adjacentMatrix):
		degreeMatrix = np.sum(adjacentMatrix, axis=1)
		laplacianMatrix = np.diag(degreeMatrix) - adjacentMatrix
		sqrtDegreeMatrix = np.diag(1.0 / (degreeMatrix ** (0.5)))
		return np.dot(np.dot(sqrtDegreeMatrix, laplacianMatrix), sqrtDegreeMatrix)


