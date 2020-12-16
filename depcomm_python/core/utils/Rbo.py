import math

class Rbo:

	def __init__(self, list1, list2, p):
		self.rbo_min = self._rbo_min(list1, list2, p)
		self.rbo_res = self._rbo_res(list1, list2, p)
		self.rbo_ext = self._rbo_ext(list1, list2, p)

	def set_at_depth(self, lst, depth):
		ans = set()
		for v in lst[:depth]:
			if isinstance(v, set):
				ans.update(v)
			else:
				ans.add(v)
		return ans

	def raw_overlap(self, list1, list2, depth):
		set1, set2 = self.set_at_depth(list1, depth), self.set_at_depth(list2, depth)
		return len(set1.intersection(set2)), len(set1), len(set2)

	def overlap(self, list1, list2, depth):
		return self.agreement(list1, list2, depth) * min(depth, len(list1), len(list2))

	def agreement(self, list1, list2, depth):
		len_intersection, len_set1, len_set2 = self.raw_overlap(list1, list2, depth)
		return 2.0 * len_intersection / (len_set1 + len_set2)

	def _rbo_min(self, list1, list2, p, depth=None):
		depth = min(len(list1), len(list2)) if depth is None else depth
		x_k = self.overlap(list1, list2, depth)
		log_term = x_k * math.log(1 - p)
		sum_term = sum(
				1.0* p ** d / d * (self.overlap(list1, list2, d) - x_k) for d in range(1, depth + 1)
				)
		return (1 - p) / p * (sum_term - log_term)

	def _rbo_res(self, list1, list2, p):
		S, L = sorted((list1, list2), key=len)
		s, l = len(S), len(L)
		x_l = self.overlap(list1, list2, l)
		f = int(math.ceil(l + s - x_l))
		term1 = s * sum(1.0 * p ** d / d for d in range(s + 1, f + 1))
		term2 = l * sum(1.0 * p ** d / d for d in range(l + 1, f + 1))
		term3 = x_l * (math.log(1 / (1 - p)) - sum(1.0 * p ** d / d for d in range(1, f + 1)))
		return 1.0 * p ** s + p ** l - p ** f - (1 - p) / p * (term1 + term2 + term3)

	def _rbo_ext(self, list1, list2, p):
		S, L = sorted((list1, list2), key=len)
		s, l = len(S), len(L)
		x_l = self.overlap(list1, list2, l)
		x_s = self.overlap(list1, list2, s)
		sum1 = sum(1.0 * p ** d * self.agreement(list1, list2, d) for d in range(1, l + 1))
		sum2 = sum(1.0 * p ** d * x_s * (d - s) / s / d for d in range(s + 1, l + 1))
		term1 = 1.0 * (1 - p) / p * (sum1 + sum2)
		term2 = 1.0 * p ** l * ((x_l - x_s) / l + x_s / s)
		return term1 + term2

	
