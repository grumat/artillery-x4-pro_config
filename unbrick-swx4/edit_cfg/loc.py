#
# -*- coding: UTF-8 -*-
#


class Loc(object):
	"""Line location in the source file (0-based indexes)"""
	def __init__(self, i_0 : int | None = None, i_n : int | None = None):
		self.idx_0 = i_0
		self.idx_n = i_n
	def __bool__(self):
		return self.idx_0 is not None
	def __str__(self):
		if self.idx_0:
			return self.idx_n and f"[{self.idx_0}:{self.idx_n}]" or f"[{self.idx_0}]"
		return "[]"
	def IsNoLoc(self):
		"""Test for empty location"""
		return self.idx_0 is None
	def IsRangeLoc(self):
		"""Test for multiple lines location"""
		return self.idx_n is not None
	def IsInRange(self, lno : int) -> bool:
		if self.idx_0 is not None:
			if self.idx_n is not None:
				return (self.idx_0 <= lno) and (lno < self.idx_n)
			else:
				return self.idx_0 == lno
		return True

NO_LOC = Loc()
