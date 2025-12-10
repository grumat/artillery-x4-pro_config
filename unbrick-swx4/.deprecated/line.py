

class MLine(object):
	"""Store the valuable part of a line"""
	def __init__(self, line : str, lno : int, has_raw_data=False):
		self.line = line
		# The valuable part has the size of the string, assuming that every other 
		# line content is part of a comment, if any
		self.loc = Loc(lno)
		self.is_empty = not line.strip()
		self.is_comment = self.is_empty and has_raw_data	# a entirely used for comment
	def GetEssence(self) -> bytes:
		from .libtools import StringEssence
		return StringEssence(self.line)
	def GetCRC(self, seed : int) -> int:
		from .libtools import StringCRC
		return StringCRC(self.line, seed)
