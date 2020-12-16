from utils.Multigraph2graph import Multigraph2graph
import networkx as nx
from utils.ExportResult import ExportResult
import Queue
from operator import itemgetter
from collections import defaultdict
from multiprocessing import Pool

class NISE:
	def __init__(self,graph,
			seed_num,
			ninf,
			expansion,
			stopping,
			nworkers,
			nruns,
			alpha,
			maxexpand,
			delta):
		self.graph = Multigraph2graph(graph)
		self.seed_num = seed_num
		self.ninf = ninf
		self.expansion = expansion
		self.stopping = stopping
		self.nworkers = nworkers
		self.nruns = nruns
		self.alpha = alpha
		self.maxexpand = maxexpand
		self.delta = delta
	
	def nise(self, filename, meth, issplit, ismergepath):
		seeds = self.seeding(self.graph, self.seed_num)

		g, maps = self.nx_node_integer_mapping(self.graph)
		if maps is not None:
			rev_map = {v: k for k, v in maps.items()}
			seeds = [rev_map[s] for s in seeds]

		if self.ninf:
			seeds = self.neighbor_inflation(g, seeds)

		communities = self.growclusters(
				g, 
				seeds, 
				self.expansion, 
				self.stopping, 
				self.nworkers, 
				self.nruns, 
				self.alpha, 
				self.maxexpand, 
				False)

		communities = self.remove_duplicates(g, communities, self.delta)
		communities = list(communities)

		if maps is not None:
			coms = []
			for com in communities:
				coms.append([maps[n] for n in com])
			nx.relabel_nodes(g, maps, False)
		else:
			coms = communities

		print coms

	def seeding(self,graph, seed_num):
		nodes = list(set(graph.nodes()))
		T = []
		for node in nodes:
			degree = graph.degree(node)
			T.append((node,degree))
		T.sort(key=lambda x:x[1], reverse=True)
		seeds = []
		for i in T[:seed_num]:
			seeds.append(i[0])
		return seeds

	def compute_local_pagerank(self, G, r, p, alpha, epsilon, max_push_count, q):
		for node, res in r.items():
			if res > epsilon * G.degree(node):
				q.put(node)

		push_count = 0
		while q.empty() == False and push_count < max_push_count:
			push_count += 1
			u = q.get()
			du = G.degree(u) * 1.0
			moving_prob = r[u] - 0.5 * epsilon * du
			r[u] = 0.5 * epsilon * du
			p[u] = p.get(u, 0.0) + (1 - alpha) * moving_prob

			neighbor_update = alpha * moving_prob / du

			for nbr in G.neighbors(u):
				nbrdeg = G.degree(nbr)
				rxold = r.get(nbr, 0.0)
				rxnew = rxold + neighbor_update
				r[nbr] = rxnew
			if rxnew > epsilon * nbrdeg >= rxold:
				q.put(nbr)

		return push_count

	def cluster_from_sweep(self, G, p, community):
		p_sorted = sorted(p.items(), key=itemgetter(1), reverse=True)

		conductance = list()
		volume = list()
		cutsize = list()

		i = 0
		rank = dict()
		for node, ppr in p_sorted:
			rank[node] = i
			i += 1

		total_degree, curcutsize, curvolume, i = 2.0 * G.number_of_edges(), 0, 0, 0
		for node, ppr in p_sorted:
			deg = G.degree(node) * 1.0
			change = deg * 1.0
			for nbr in G.neighbors(node):
				if rank.get(nbr, -1) != -1 and rank.get(nbr, -1) < rank[node]:
					change -= 2

			curcutsize += change
			curvolume += deg

			cutsize.append(curcutsize)
			volume.append(curvolume)
			if curvolume == 0 or total_degree - curvolume == 0:
				conductance.append(1.0)
			else:
				conductance.append(curcutsize / min(curvolume, total_degree - curvolume))

		lastind = len(conductance)
		mincond = float('INF')
		mincondind = 0
		for i in range(lastind):
			if conductance[i] <= mincond:
				mincond = conductance[i]
				mincondind = i

		for i in range(min(mincondind + 1, len(p_sorted))):
			community.append(p_sorted[i][0])

		return mincond

	def pprgrow4(self, G, seed, alpha, targetvol):
		p = dict()
		r = dict()
		q = Queue.Queue()
		community = list()

		for s in seed:
			r[s] = 1.0 / (len(seed) * 1.0)

		pr_eps = 1.0 / max(10.0 * targetvol, 100.0)
		maxsteps = 1.0 / (pr_eps * (1.0 - alpha))
		maxsteps = min(maxsteps, 0.5 * (2.0 ** 32 - 1.0))

		nsteps = self.compute_local_pagerank(G, r, p, alpha, pr_eps, int(maxsteps), q)
		if nsteps == 0:
			p = r

		for node, pr in p.items():
			pr *= 1.0 / max(G.degree(node), 1.0)

		mincond = self.cluster_from_sweep(G, p, community)
		return community, mincond

	def pprgrow(self, args):
		seed, G, stopping, nruns, alpha, maxexpand, fast = args
		expandseq = [2, 3, 4, 5, 10, 15]
		expands = list()
		curmod = 1
		while len(expands) < nruns:
			temp = [curmod * i for i in expandseq]
			for i in temp:
				expands.append(i)
			curmod *= 10

		expands = expands[:nruns]
		maxdeg = max(dict(G.degree(G.nodes())).values())
		bestcond = float('INF')

		if fast == True:
			expands = [1000]

		for ei in range(len(expands)):
			if fast == True:
				curexpand = expands[ei]
			else:
				if isinstance(seed, int):
					seed = [seed]
				curexpand = expands[ei] * len(seed) + maxdeg
			assert len(seed) > 0.0
			if curexpand > maxexpand:
				continue
			if stopping == 'cond':
				curset, cond = self.pprgrow4(G, seed, alpha, curexpand)
				if cond < bestcond:
					bestcond = cond

		return curset

	def growclusters(self, G, seeds, expansion, stopping, nworkers, nruns, alpha, maxexpand, fast):
		if maxexpand == float('INF'):
			maxexpand = G.number_of_edges()

		ns = len(seeds)
		communities = list()
		if nworkers == 1:
			for i in range(ns):
				seed = seeds[i]
				curset = self.pprgrow((seed, G, stopping, nruns, alpha, maxexpand, fast))
				communities.append(curset)

		else:
			slen = len(seeds)
			args = zip(seeds, [G] * slen, [stopping] * slen, [nruns] * slen, [alpha] * slen, \
					[maxexpand] * slen, [fast] * slen)
			p = Pool(nworkers)
			if expansion == 'ppr':
				communities = p.map(pprgrow, args)
		return communities

	def remove_duplicates(self, G, communities, delta):
		node2com = defaultdict(list)
		com_id = 0
		for comm in communities:
			for node in comm:
				node2com[node].append(com_id)
			com_id += 1

		deleted = dict()
		for i in range(len(communities)):
			comm = communities[i]
			if deleted.get(i, 0) == 0:
				nbrnodes = nx.node_boundary(G, comm)
				for nbr in nbrnodes:
					nbrcomids = node2com[nbr]
					for nbrcomid in nbrcomids:
						if i != nbrcomid and deleted.get(i, 0) == 0 and deleted.get(nbrcomid, 0) == 0:
							nbrcom = communities[nbrcomid]
							distance = 1.0 - (len(set(comm) & set(nbrcom)) * 1.0 / (min(len(comm), len(nbrcom)) * 1.0))
							if distance <= delta:
								deleted[i] = 1
								for node in comm:
									node2com[node].remove(i)

		for i in range(len(communities)):
			if deleted.get(i, 0) == 1:
				communities[i] = []
		
		communities = filter(lambda c: c != [], communities)
		return communities
	
	def neighbor_inflation(self, G, seeds):
		for i in range(len(seeds)):
			seed = seeds[i]
			egonet = [seed]
			for s in G.neighbors(seed):
				egonet.append(s)
			seeds[i] = list(set(egonet))
		return seeds

	def nx_node_integer_mapping(self,graph):
		convert = False
		for nid in graph.nodes():
			if isinstance(nid, str):
				convert = True
				break

		if convert:
			node_map = {}
			label_map = {}
			if isinstance(graph, nx.Graph):
				for nid, name in enumerate(graph.nodes()):
					node_map[nid] = name
					label_map[name] = nid

				nx.relabel_nodes(graph, label_map, copy=False)
				return graph, node_map
			else:
				raise ValueError("graph must be a networkx Graph object")
		return graph, None

