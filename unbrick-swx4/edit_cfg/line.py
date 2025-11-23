#
# -*- coding: UTF-8 -*-
#
# Spellchecker:	words libtools

from .loc import Loc

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
		from libtools import StringEssence
		return StringEssence(self.line)
	def GetCRC(self, seed : int) -> int:
		from libtools import StringCRC
		return StringCRC(self.line, seed)


class Line(object):
	""" Stores a copy of a line and its uncommented version """
	def __init__(self, l : str):
		self.raw = l
		self.unc = Line.UncommentLine(l)
	@staticmethod
	def UncommentLine(l : str) -> str:
		""" This removes line comments from the given line """
		# Blanks at the right side are ignored
		l = l.rstrip()
		# Skip empty lines
		if l:
			# Locate line comment symbol
			pos = l.find('#')
			# not found?
			if pos < 0:
				# Alternative line comment
				pos = l.find(';')
			# Clear the command, if found
			if pos >= 0:
				l = l[:pos].rstrip()
		# Returns only 'clean' lines
		return l
	def GetLen(self):
		""" Total length of a raw line """
		return len(self.raw)
	def IsLineEmpty(self) -> bool:
		""" Checks if a line is empty. Empty lines are most of the times ignored """
		return not self.unc
	def HasLeadingBlanks(self):
		""" True if line has contents but starts with a leading space (multi-line values) """
		return self.unc and self.unc[0].isspace()
	def HasKeyPattern(self):
		""" Does this line looks like a section key? """
		return (not self.raw.startswith('[')) \
			and self.raw \
			and (self.raw[0].isalnum() or (self.raw[0] == '_')) \
			and ((':' in self.unc) or ('=' in self.unc))
