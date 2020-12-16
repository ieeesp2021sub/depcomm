from collections import Counter, defaultdict
import itertools
import igraph as ig
import numpy as np
import operator
from utils.Multigraph2graph import Multigraph2graph
from utils.ExportResult import ExportResult
from utils.Nx2igraph import nx2ig

def nepusz_modularity(G, cover):
	raise NotImplementedError("See the CONGA 2010 paper")

def zhang_modularity(G, cover):
	raise NotImplementedError("""See 'Identification of overlapping algorithms structure in complex networks using fuzzy C-means clustering'""")

def nicosia_modularity(G, cover):
	raise NotImplementedError("""See 'Extending the definition of modularity to directed graphs with overlapping communities'""")

def count_communities(G, cover):
	counts = {i.index : 0 for i in G.vs}
	for community in cover:
		for v in community:
			counts[v] += 1
	return counts

def get_weights(G):
	try:
		weights = G.es['weight']
	except KeyError:
		weights = [1 for e in G.es]
	return weights

def get_single_lazar_modularity(G, community, weights, counts):
	totalInternalWeight = sum(weights[G.es[e].index] for e in community)
	numVerticesInCommunity = len(community)
	numPossibleInternalEdges = numVerticesInCommunity * (numVerticesInCommunity - 1) / 2
	if numPossibleInternalEdges == 0: return 0
	edgeDensity = totalInternalWeight / numPossibleInternalEdges / numVerticesInCommunity
	interVsIntra = 0
	comm = set(community)
	for v in community:
		interVsIntraInternal = 0
		neighbors = G.neighbors(v)
		degree = len(neighbors)
		numCommunitiesWithin = counts[v]
		for n in neighbors:
			weight = weights[G.get_eid(v, n)]
			if n in comm:
				interVsIntraInternal += weight
			else:
				interVsIntraInternal -= weight
		interVsIntraInternal /= (degree * numCommunitiesWithin)
		interVsIntra += interVsIntraInternal
	return edgeDensity * interVsIntra

def lazar_modularity(G, cover):
	numCommunities = len(cover)
	totalModularity = 0
	weights = get_weights(G)
	counts = count_communities(G, cover)
	for c in cover:
		totalModularity += get_single_lazar_modularity(G, c, weights, counts)
	averageModularity = 1/numCommunities * totalModularity
	return averageModularity

class CrispOverlap(object):
	def __init__(self, graph, covers, modularities=None, optimal_count=None, modularity_measure="lazar"):
		self._measureDict = {"lazar" : lazar_modularity}
		self._covers = covers
		self._graph = graph
		self._optimal_count = optimal_count
		self._modularities = modularities
		if modularity_measure in self._measureDict:
			self._modularity_measure = modularity_measure
		else: raise KeyError("Modularity measure not found.")

	def __getitem__(self, numClusters):
		if not numClusters:
			raise KeyError("Number of clusters must be a positive integer.")
		return self._covers[numClusters]

	def __iter__(self):
		return (v for v in list(self._covers.values()))

	def __len__(self):
		return len(self._covers)

	def __bool__(self):
		return bool(self._covers)

	def __str__(self):
		return '{0} vertices in {1} possible covers.'.format(len(self._graph.vs), len(self._covers))

	def recalculate_modularities(self):
		modDict = {}
		for cover in self._covers.values():
			modDict[len(cover)] = self._measureDict[self._modularity_measure](self._graph, cover)
		self._modularities = modDict
		self._optimal_count = max(iter(self._modularities.items()), key=operator.itemgetter(1))[0]
		return self._modularities

	@property
	def modularities(self):
		if self._modularities:
			return self._modularities
		self._modularities = self.recalculate_modularities()
		return self._modularities

	@property
	def optimal_count(self):
		if self._optimal_count is not None:
			return self._optimal_count
		else:
			modularities = self.modularities
			self._optimal_count = max(list(modularities.items()), key=operator.itemgetter(1))[0]
			return self._optimal_count

	def make_fuzzy(self):
		pass


class Congo:
	def __init__(self,graph,number_communities,height):
		self.graph = Multigraph2graph(graph)
		self.graph = nx2ig(self.graph)
		self.number_communities = number_communities
		self.height = height

	def congo(self,g,filename,meth,issplit,ismergepath):

		result = self.congo_(self.graph,self.height)
		if self.number_communities == 0:
			cover = result._covers[result.optimal_count]
			self.number_communities = result.optimal_count
		else:
			cover = result._covers[self.number_communities]

		list_communities = []
		for i in range(0,self.number_communities):
			list_communities.append(cover._clusters[i])

		coms = []
		for c in list_communities:
			coms.append([self.graph.vs[x]['name'] for x in c])
		
		nodes = g.nodes()
		found = []
		a = []
		for x in coms:
			b = []
			for node in list(x):
				found.append(node)
				b.append(node)
			a.append(b)
		unfound = []
		for node in nodes:
			if node in found:
				continue
			else:
				unfound.append(node)
		if unfound:
			a.append(unfound)

		t = {}
		for index, com in enumerate(a):
			for node in com:
				if t.has_key(node):
					t[node].append(index)
				else:
					t[node] = [index]
		z = []
		for key in t:
			pr = ['0']*len(a)
			for i in t[key]:
				pr[i] = '1'
			z.append((key,pr))

		ExportResult.exportaffiliation(g, z, filename, meth, issplit, ismergepath)

	def congo_(self, OG, h):
		G = OG.copy()
		if not G.is_connected():
			raise RuntimeError("Congo only makes sense for connected graphs.")

		G.vs['CONGA_orig'] = [i.index for i in OG.vs]
		G.es['eb'] = 0
		G.vs['pb'] = [{uw : 0 for uw in itertools.combinations(G.neighbors(vertex), 2)} for vertex in G.vs]

		self.do_initial_betweenness(G, h)
		nClusters = 1

		allCovers = {nClusters : ig.VertexCover(OG)}
		while G.es:
			maxEdge, maxEb = max(enumerate(G.es['eb']), key=operator.itemgetter(1))
			G.vs['vb'] = G.betweenness(cutoff=h)

			vInteresting = [i for i, b in enumerate(G.vs['vb']) if 2 * b > maxEb]
			splitInstr = self.max_split_betweenness(G, vInteresting)

			if splitInstr is None or splitInstr[0] <= maxEb:
				split = self.delete_edge(G, maxEdge, h)
			else:
				split = self.split_vertex(G, splitInstr[1], splitInstr[2], h)

			if split:
				comm = G.components().membership
				cover = self.get_cover(G, OG, comm)
				nClusters += 1
				allCovers[nClusters] = cover

		return CrispOverlap(OG, allCovers)

	def do_initial_betweenness(self, G, h):
		all_pairs_shortest_paths = []
		pathCounts = Counter()
		for ver in G.vs:
			neighborhood = self.get_neighborhood_vertex(G, ver, h)
			neighborhood.remove(ver.index)
			s_s_shortest_paths = G.get_all_shortest_paths(ver, to=neighborhood)
			all_pairs_shortest_paths += s_s_shortest_paths

		for path in all_pairs_shortest_paths:
			pathCounts[(path[0], path[-1])] += 1

		for path in all_pairs_shortest_paths:
			if len(path) <= h + 1:
				self.update_betweenness(G, path, pathCounts[(path[0], path[-1])], operator.pos)

	def update_betweenness(self, G, path, count, op):
		weight = op(1./count)
		pos = 0
		while pos < len(path) - 2:
			G.vs[path[pos + 1]]['pb'][self.order_tuple((path[pos], path[pos + 2]))] += weight
			G.es[G.get_eid(path[pos], path[pos + 1])]['eb'] += weight
			pos += 1
		if pos < len(path) - 1:
			G.es[G.get_eid(path[pos], path[pos + 1])]['eb'] += weight

	def max_split_betweenness(self, G, vInteresting):
		maxSplitBetweenness = 0
		vToSplit = None
		for v in vInteresting:
			clique = self.create_clique(G, v, G.vs['pb'][v])
			if clique.size < 4:
				continue

			vMap = [[ve] for ve in G.neighbors(v)]

			while clique.size > 4:
				i,j,clique = self.reduce_matrix(clique)
				vMap[i] += vMap.pop(j)

			if clique[0,1] >= maxSplitBetweenness:
				maxSplitBetweenness = clique[0,1]
				vToSplit = v
				splitInstructions = vMap
		if vToSplit is None:
			return None

		return maxSplitBetweenness, vToSplit, splitInstructions

	def create_clique(self, G, v, pb):
		neighbors = G.neighbors(v)
		mapping = {neigh : i for i, neigh in enumerate(neighbors)}
		n = len(neighbors)

		clique = np.zeros((n, n))
		for uw, score in pb.items():
			clique[mapping[uw[0]], mapping[uw[1]]] = score
			clique[mapping[uw[1]], mapping[uw[0]]] = score
		
		np.fill_diagonal(clique, 0)
		return clique
	
	def reduce_matrix(self, M):
		i,j = self.mat_min(M)
		M[i,:] = M[j,:] + M[i,:]

		M = np.delete(M, (j), axis=0)
		M[:,i] = M[:,j] + M[:,i]
		M = np.delete(M, (j), axis=1)
		np.fill_diagonal(M,0)
		return i,j,M
	
	def mat_min(self, M):
		np.fill_diagonal(M, float('inf'))
		i,j = np.unravel_index(M.argmin(), M.shape)
		np.fill_diagonal(M,0)
		return i, j
	

	def get_neighborhood_vertex(self, G, v, h):
		return G.neighborhood(v, order=h)

	def get_neighborhood_edge(self, G, e, h):
		neigh = set(G.neighborhood(e[0], order=h-1))
		neigh.update(G.neighborhood(e[1], order=h-1))
		return list(neigh)

	def delete_edge(self, G, edge, h):
		tup = G.es[edge].tuple
		neighborhood = self.get_neighborhood_edge(G, tup, h)

		self.do_local_betweenness(G, neighborhood, h, operator.neg)

		G.delete_edges(edge)
		self.fix_betweennesses(G)
		self.do_local_betweenness(G, neighborhood, h, operator.pos)
		return self.check_for_split(G, tup)

	def fix_pair_betweennesses(self, G):
		for v in G.vs:
			toDel = []
			neededPairs = {uw for uw in itertools.combinations(G.neighbors(v), 2)}
			for pair in v['pb']:
				if pair not in neededPairs:
					toDel.append(pair)
			for d in toDel:
				del v['pb'][d]
			for pair in neededPairs:
				if pair not in v['pb']:
					v['pb'][pair] = 0

	def fix_edge_betweennesses(self, G):
		for e in G.es:
			if e['eb'] is None:
				e['eb'] = 0

	def fix_betweennesses(self, G):
		self.fix_pair_betweennesses(G)
		self.fix_edge_betweennesses(G)
		
	def split_vertex(self, G, vToSplit, instr, h):
		neighborhood = self.get_neighborhood_vertex(G, vToSplit, h)
		self.do_local_betweenness(G, neighborhood, h, operator.neg)
		new_index = G.vcount()
		G.add_vertex()
		G.vs[new_index]['CONGA_orig'] = G.vs[vToSplit]['CONGA_orig']
		G.vs[new_index]['pb'] = {uw : 0 for uw in itertools.combinations(G.neighbors(vToSplit), 2)}

		toAdd = list(zip(itertools.repeat(new_index), instr[0]))
		toDelete = list(zip(itertools.repeat(vToSplit), instr[0]))
		G.add_edges(toAdd)
		G.delete_edges(toDelete)
		neighborhood.append(new_index)
		self.fix_betweennesses(G)

		self.do_local_betweenness(G, neighborhood, h, operator.pos)
		return self.check_for_split(G, (vToSplit, new_index))

	def do_local_betweenness(self, G, neighborhood, h, op=operator.pos):
		all_pairs_shortest_paths = []
		pathCounts = Counter()
		for i, v in enumerate(neighborhood):
			s_s_shortest_paths = G.get_all_shortest_paths(v, to=neighborhood)
			all_pairs_shortest_paths += s_s_shortest_paths
		neighSet = set(neighborhood)
		neighSize = len(neighborhood)
		apsp = []
		for path in all_pairs_shortest_paths:
			if len(neighSet | set(path)) == neighSize:
				pathCounts[(path[0], path[-1])] += 1
				apsp.append(path)
		for path in apsp:
			if len(path) <= h + 1:
				self.update_betweenness(G, path, pathCounts[(path[0], path[-1])], op)

	def get_cover(self, G, OG, comm):
		coverDict = defaultdict(list)
		for i, community in enumerate(comm):
			coverDict[community].append(int(G.vs[i]['CONGA_orig']))
		return ig.clustering.VertexCover(OG, clusters=list(coverDict.values()))

	def vertex_betweeenness_from_eb(self, G, eb):
		components = G.components()
		membership = components.membership
		vbs = []
		for vertex in G.vs:
			numComponents = len(components[membership[vertex.index]])
			incidentEdges = G.incident(vertex)
			vb = .5 * (sum(G.es[e]['eb'] for e in incidentEdges) - (numComponents - 1))
			vbs.append(vb)
		return vbs

	def order_tuple(self, toOrder):
		if toOrder[0] <= toOrder[1]:
			return toOrder
		return (toOrder[1], toOrder[0])

	def check_for_split(self, G, edge):
		try:
			return not G.edge_disjoint_paths(source=edge[0], target=edge[1])
		except Exception as e:
			return False

	def matrix_min(mat):
		upperTri = np.triu_indices(mat.shape[0], 1)
		minDex = mat[upperTri].argmin()
		triN = mat.shape[0] - 1
		row = 0
		while minDex >= triN:
			minDex -= triN
			triN -= 1
			row += 1
		col = mat.shape[0] - triN + minDex
		return row, col


