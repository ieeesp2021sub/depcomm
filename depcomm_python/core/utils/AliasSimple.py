import numpy as np

class AliasSimple:

	@classmethod
	def alias_setup(cls, probs):
		K = len(probs)
		q = np.zeros(K)
		J = np.zeros(K, dtype=np.int)

		smaller = []
		larger = []
		for kk, prob in enumerate(probs):
			q[kk] = K*prob
			if q[kk] < 1.0:
				smaller.append(kk)
			else:
				larger.append(kk)

		while len(smaller) > 0 and len(larger) > 0:
			small = smaller.pop()
			large = larger.pop()

			J[small] = large
			q[large] = q[large] + q[small] - 1.0
			if q[large] < 1.0:
				smaller.append(large)
			else:
				larger.append(large)

		return J, q

	@classmethod
	def alias_draw(cls, J, q):
		K = len(J)

		kk = int(np.floor(np.random.rand()*K))
		if np.random.rand() < q[kk]:
			return kk
		else:
			return J[kk]


