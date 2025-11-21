#
# -*- coding: UTF-8 -*-
#


import re
from typing import Callable, Optional

from .line import Line
from .sections import Section
from .keys import Key


class CfgIterator(object):
	"""Allows to iterate over the configuration lines for contents detection"""
	def __init__(self, lines : list[Line], callback : Optional[Callable[[int], None]] = None):
		self.it = iter(lines)
		self.callback = callback
		self.lno = -1
		self.rl : Line | None = None
		self.m = None
		self.pat = re.compile(r"\[(.+)\]")
		self.save = False
	def NextLine(self):
		"""Moves one line further"""
		self.lno += 1
		self.rl = next(self.it)
		self.save = self.rl.raw.startswith("#*#")
		self.m = (self.rl.unc and (self.rl.unc[0] == '[')) and self.pat.match(self.rl.unc) or None
		if self.callback:
			self.callback(self.lno)
	def IsPersistenceBlock(self) -> bool:
		"""Klipper stores persistence on the bottom of the file"""
		return self.save
	def IsLineEmpty(self) -> bool:
		"""Checks if a line is empty. Empty lines are most of the times ignored"""
		if self.rl is None:
			raise ValueError("Unexpected type for 'self.rl'")
		return self.rl.IsLineEmpty()
	def MatchesSection(self) -> bool:
		"""Returns true if a section start is found. This should close any multiline key or previous section"""
		return bool(self.m)
	def GetSectionLabel(self) -> str | None:
		"""The label of the detected section, in the case `MatchesSection` is true"""
		return self.m and self.m.group(1) or None
	def HasLeadingBlanks(self):
		"""True if line has contents but starts with a leading space (multi-line values)"""
		if self.rl is None:
			raise ValueError("Unexpected type for 'self.rl'")
		return self.rl.HasLeadingBlanks()
	def HasKeyPattern(self):
		"""Does this line looks like a section key?"""
		if self.rl is None:
			raise ValueError("Unexpected type for 'self.rl'")
		return (not self.m) and self.rl.HasKeyPattern()
	def CreateSection(self) -> Section:
		"""Create a Section instance, assuming that 'MatchesSection()' is true. At exit it moves to the next line"""
		s = Section(self.GetSectionLabel(), self.lno)
		return s
	def CreateKey(self, sep : str) -> Key:
		"""Create a Section instance, assuming that 'HasKeyPattern()' is true"""
		if self.rl is None:
			raise ValueError("Unexpected type for 'self.rl'")
		k, v = self.rl.unc.split(sep, 1)
		key = Key(k, self.lno, v)
		return key

