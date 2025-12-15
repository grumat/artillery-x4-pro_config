#
# -*- coding: UTF-8 -*-
#


class Loc(object):
	"""Line location in the source file (0-based indexes)"""
	def __init__(self, i_0 : int, i_n : int):
		self.idx_0 = i_0
		self.idx_n = i_n
	def __bool__(self):
		return self.idx_0 is not None
	def __str__(self):
		return self.idx_n and f"[{self.idx_0}:{self.idx_n}]" or f"[{self.idx_0}]"
	def __repr__(self):
		return f"Loc([{self.idx_0}:{self.idx_n}])"

