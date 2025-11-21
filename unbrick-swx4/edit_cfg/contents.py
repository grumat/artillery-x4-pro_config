#
# -*- coding: UTF-8 -*-
#
# Spellchecker: words MULT

from .context import Context
from .sections import Section, SecLabel
from .loc import Loc
from .parser import CfgIterator
from .line import MLine
from .result import Result, NO_SECTION, MULT_SECTION, INV_RANGE


class Contents(object):
	"""Store the entire metadata contents of the configuration file"""
	def __init__(self, ctx : Context):
		self.ctx = ctx
		self.sections : list[Section] = []
		self.save = Loc()
		self.cur_sect = None
		self.cur_key = None
	def UpdLineNo_(self, lno : int):
		"""This callback updates line counters of section/keys being parsed"""
		if self.cur_sect:
			self.cur_sect.loc.idx_n = lno
		if self.cur_key:
			self.cur_key.loc.idx_n = lno
		if self.save.idx_0 is not None:
			self.save.idx_n = lno
	def CloseData_(self, it : CfgIterator):
		# Just don't forget to add remainder instances
		if self.cur_sect:
			if self.cur_key:
				self.cur_sect.keys.append(self.cur_key)
				self.cur_key = None
			self.sections.append(self.cur_sect)
			self.cur_sect = None
		# Read until the end
		while True:
			it.NextLine()
	def Load(self) -> None:
		"""Identifies the contents of the configuration file and populate itself"""
		# Configuration iterator
		it = CfgIterator(self.ctx.raw_lines, self.UpdLineNo_)
		# First line
		it.NextLine()
		while True:
			try:
				# Persistence block?
				if it.IsPersistenceBlock():
					self.save.idx_0 = it.lno
					self.CloseData_(it)
				# Ignore empty lines, on the file scope
				elif it.IsLineEmpty():
					it.NextLine()
				elif it.MatchesSection():
					# A section was found. Now gathers all lines belonging to this section
					self.cur_sect = it.CreateSection()
					it.NextLine()
					while(True):
						# Persistence block?
						if it.IsPersistenceBlock():
							self.save.idx_0 = it.lno
							self.CloseData_(it)
						# Ignore 'non-key' patterns (or a syntax error?)
						elif it.IsLineEmpty() or it.HasLeadingBlanks():
							it.NextLine()
						elif it.HasKeyPattern():
							# Found a "key:..." pattern
							self.cur_key = it.CreateKey()
							it.NextLine()
							# If the key is multi-line mode, we have to fetch all lines
							if self.cur_key.IsMultiLine():
								# This flag marks True if the last line that was seen is blank
								blank = False
								while True:
									if it.rl.raw:
										if it.rl.raw[0].isspace():
											# This collect even commented out lines
											self.cur_key.value.append(MLine(it.rl.unc+'\n', it.lno))
											blank = it.IsLineEmpty()
										else:
											# Skip the last empty line on transition
											if blank:
												self.cur_key.loc.idx_n -= 1
											break
									else:
										blank = True
									it.NextLine()
							self.cur_sect.keys.append(self.cur_key)
							self.cur_key = None
						else:
							self.sections.append(self.cur_sect)
							self.cur_sect = None
							break
				else:
					it.NextLine()
			except StopIteration:
				break
	def MatchSections(self, pat :SecLabel) -> list[Section]:
		"""Returns a list of sections matching the section pattern"""
		return [s for s in self.sections if s.name.Match(pat)]
	def GetSingleSection(self, pat :SecLabel) -> Result:
		"""Makes sure that a single section matches the input pattern"""
		sec = self.MatchSections(pat)
		if not sec:
			return NO_SECTION
		if len(sec) > 1:
			return MULT_SECTION
		return Result('s', sec[0])
	def GetSectionOfLine(self, lno : int) -> Result:
		"""Searches the section that is on the given line number"""
		rng = Loc(lno)
		if not self.ctx.IsRangeValid(rng):
			return INV_RANGE(rng)
		for s in self.sections:
			if s.GetLoc().IsInRange(lno):
				return Result('s', s)
		return NO_SECTION
	def GetFirstSection(self) -> Section:
		for s in self.sections:
			if not s.name.IsInclude():
				return s
		return None
	def AddSectionLines(self, loc : Loc, data : list[str]) -> None:
		if (self.save.idx_0 is None) or (loc.idx_0 is None):
			raise ValueError("Unexpected type for 'Loc")
		if self.save.idx_0 <= loc.idx_0:
			loc = Loc(self.save.idx_0 - 1)
		self.ctx.AddSectionLines(loc, data)

