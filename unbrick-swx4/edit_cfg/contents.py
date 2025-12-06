#
# -*- coding: UTF-8 -*-
#
# Spellchecker: words MULT

import os
from abc import ABC, abstractmethod

from .sections import Section, SecLabel
from .loc import Loc
from .parser import CfgIterator, Context
from .line import Line, AnyBuffer, LineFactory, EmptyLine, IncludeLine, CommentLine, SectionLine, ValueLine, \
	MultiLineStartLine, ContinuationLine, ContinuationCommentLine, PersistenceLine, MLine
from .result import Result, NO_SECTION, MULT_SECTION, INV_RANGE
from .keys import Key


class FileBuffer(AnyBuffer):
	" An instance of this class holds all files of a files "
	def __init__(self) -> None:
		super().__init__()
	def Link(self, l : Line) -> None:
		assert False, "This is the root container and is not tracked"
		pass
	def Unlink(self, l : Line) -> None:
		assert False, "This is the root container and is not tracked"
		pass
	def Load(self, fname : str) -> None:
		with open(fname, 'rt', encoding="utf-8") as fr:
			factory = LineFactory()
			prev_line : Line|None = None
			for line in fr:
				line = line.rstrip()
				obj = factory.New(line, prev_line)
				if obj is not None:
					self.lines.append(obj)
					prev_line = obj
	def Save(self, fname : str) -> None:
		with open(fname, 'wt', encoding="utf-8") as fh:
			for line in self.lines:
				print(line.raw_content, file=fh)


class SectionBuffer(AnyBuffer):
	" This holds all lines belonging to a section"
	def __init__(self) -> None:
		super().__init__()
		self.header : SectionLine | None = None
	def Link(self, l : Line) -> None:
		assert isinstance(l, (EmptyLine, CommentLine, SectionLine, ValueLine, MultiLineStartLine, ContinuationLine, ContinuationCommentLine))
		super().Link(l)
		# Got a section header line
		if isinstance(l, SectionLine):
			# Never assigned? Give up if tracking an inactive section...
			if (self.header is None) or (self.header.inactive == True):
				self.header = l
	def Unlink(self, l : Line) -> None:
		super().Unlink(l)
		if l is self.header:
			self.header = None
	def __repr__(self) -> str:
		if self.header is None:
			return "Unknown section"
		else:
			return "S: " + self.header.section_name


class IncludeBuffer(AnyBuffer):
	" This holds all lines belonging to the include block "
	def __init__(self) -> None:
		super().__init__()
		self.header : IncludeLine | None = None
	def Link(self, l : Line) -> None:
		assert isinstance(l, (EmptyLine, CommentLine, IncludeLine))
		super().Link(l)
		if isinstance(l, IncludeLine):
			if (self.header is None) or (self.header.inactive == True):
				self.header = l
	def Unlink(self, l : Line) -> None:
		super().Unlink(l)
	def __repr__(self) -> str:
		if self.header is None:
			return "Unknown include"
		else:
			return "I: " + self.header.filename


class PersistenceBuffer(AnyBuffer):
	" This holds all lines belonging to the persistence block "
	def __init__(self) -> None:
		super().__init__()
	def Link(self, l : Line) -> None:
		super().Link(l)
	def Unlink(self, l : Line) -> None:
		super().Unlink(l)
	def __repr__(self) -> str:
		return "Persistence"


class Contents2(object):
	def __init__(self) -> None:
		self.file_buffer = FileBuffer()
		self.includes : list[IncludeBuffer] = []
		self.sections : list[SectionBuffer] = []
		self.persistence = PersistenceBuffer()

	def _collect_include_(self, start : int, i : int) -> int:
		include = IncludeBuffer()
		i += 1
		include.LinkList(self.file_buffer.lines[start: i])
		self.includes.append(include)
		return i
	
	def _collect_section_(self, start : int, i : int) -> int:
		top = i
		i += 1
		while i < len(self.file_buffer.lines):
			obj = self.file_buffer.lines[i]
			if isinstance(obj, MultiLineStartLine):
				i2 = i + 1
				while i2 < len(self.file_buffer.lines):
					obj2 = self.file_buffer.lines[i2]
					if isinstance(obj2, (ContinuationLine, ContinuationCommentLine, CommentLine, EmptyLine)):
						i2 += 1
					else:
						break
				i = i2
			elif isinstance(obj, (ValueLine, EmptyLine, CommentLine, ContinuationCommentLine)):
				i += 1
			else:
				break
		# Strip at the end; blank lines and comments are always header of the next section
		while i >= top:
			i -= 1
			obj = self.file_buffer.lines[i]
			if not isinstance(obj, (EmptyLine, CommentLine)):
				i += 1
				break
		sec = SectionBuffer()
		sec.LinkList(self.file_buffer.lines[start:i])
		self.sections.append(sec)
		return i

	def _collect_persistence_(self, start : int, i : int) -> int:
		i += 1
		while i < len(self.file_buffer.lines):
			obj = self.file_buffer.lines[i]
			if isinstance(obj, PersistenceLine):
				i += 1
			else:
				raise ValueError(f"Line {i + 1}: Unexpected line type found in Persistence block: '{repr(obj)}'")
		self.persistence.LinkList(self.file_buffer.lines[start:i])
		return i

	def _collect0_(self):
		start = 0
		i = 0
		while i < len(self.file_buffer.lines):
			obj = self.file_buffer.lines[i]
			if isinstance(obj, (EmptyLine, CommentLine)):
				i += 1
			elif isinstance(obj, IncludeLine):
				start = i = self._collect_include_(start, i)
			elif isinstance(obj, SectionLine):
				start = i = self._collect_section_(start, i)
			elif isinstance(obj, PersistenceLine):
				start = i = self._collect_persistence_(start, i)
			else:
				raise ValueError(f"Line {i + 1}: Unexpected line type found in file: '{repr(obj)}'")
				

	def Load(self, fname : str) -> None:
		assert len(self.file_buffer.lines) == 0, "Object already has contents"
		self.file_buffer.Load(fname)
		self._collect0_()


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
				self.cur_sect.AddKey(self.cur_key)
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
					try:
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
								if self.cur_key.loc.idx_n is None:
									raise ValueError("Key location has an unexpected state")
								it.NextLine()
								# If the key is multi-line mode, we have to fetch all lines
								if it.IsLineEmpty() or it.HasLeadingBlanks():
									try:
										# This flag marks True if the last line that was seen is blank
										while True:
											if it.rl is None:
												raise ValueError("Line instance shall have a contents")
											has_raw_data = (it.rl.raw.strip() != '')
											if it.rl.raw:
												if it.rl.raw[0].isspace():
													# This collect even commented out lines
													self.cur_key.value.append(MLine(it.rl.unc+'\n', it.lno, has_raw_data))
												else:
													break
											else:
												self.cur_key.value.append(MLine('\n', it.lno, has_raw_data))
											it.NextLine()
										self.cur_key.ShrinkIfEmpty()
									except StopIteration:
										self.cur_key.ShrinkIfEmpty()
										raise
								self.cur_sect.AddKey(self.cur_key)
								self.cur_key = None
							else:
								self.sections.append(self.cur_sect)
								self.cur_sect = None
								break
					except StopIteration:
						if self.cur_sect:
							if self.cur_key:
								self.cur_key.ShrinkIfEmpty()
								self.cur_sect.AddKey(self.cur_key)
								self.cur_key = None
							self.cur_sect.GetLoc().idx_n
							self.sections.append(self.cur_sect)
							self.cur_sect = None
						raise
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
	def GetFirstSection(self) -> Section | None:
		for s in self.sections:
			if not s.name.IsInclude():
				return s
		return None
	def GetPersistence(self) -> list[str]:
		if self.save.idx_0 is None:
			raise ValueError("Unexpected type for 'Loc")
		return self.ctx.GetLines(self.save)
	def ReplacePersistence(self, data : list[str]) -> None:
		if self.save.idx_0 is None:
			raise ValueError("Unexpected type for 'Loc")
		self.ctx.DeleteRange(self.save)
		self.save.idx_n = self.save.idx_0
		self.ctx.AddLines(self.save, data)
		self.save.idx_n = self.save.idx_0 + len(data)
	def AddSectionLines(self, loc : Loc, data : list[str]) -> None:
		if (self.save.idx_0 is None) or (loc.idx_0 is None):
			raise ValueError("Unexpected type for 'Loc")
		if self.save.idx_0 <= loc.idx_0:
			loc = Loc(self.save.idx_0 - 1)
		self.ctx.AddSectionLines(loc, data)

