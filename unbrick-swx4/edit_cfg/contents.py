#
# -*- coding: UTF-8 -*-
#
# Spellchecker: words MULT klipper

import os
from abc import ABC, abstractmethod

from .loc import Loc
from .line import Line, AnyBuffer, LineFactory, EmptyLine, IncludeLine, CommentLine, SectionLine, ValueLine, \
	MultiLineStartLine, ContinuationEmptyLine, ContinuationLine, ContinuationCommentLine, PersistenceLine


class FileBuffer(AnyBuffer):
	" An instance of this class holds all files of a files "
	def __init__(self) -> None:
		super().__init__()
	def GetTitle(self) -> str:
		return "File Buffer"
	def Link(self, l : Line) -> None:
		assert False, "This is the root container and is not tracked"
		pass
	def Unlink(self, l : Line) -> None:
		assert False, "This is the root container and is not tracked"
		pass
	def Load(self, fname : str) -> None:
		" Loads a Klipper-compatible file "
		with open(fname, 'rt', encoding="utf-8") as fr:
			factory = LineFactory()
			prev_line : Line|None = None
			for line in fr:
				line = line.rstrip()
				obj = factory.New(line, prev_line)
				if obj is not None:
					self.lines.append(obj)
					if not isinstance(obj, EmptyLine):
						prev_line = obj
	def Save(self, fname : str) -> None:
		" Store all contents to a Klipper-compatible file "
		with open(fname, 'wt', encoding="utf-8") as fh:
			for line in self.lines:
				print(line.raw_content, file=fh)
	def UpdateLineNumbers(self):
		" Should be called to re-sequence the line numbers after contents edition "
		for i, l in enumerate(self.lines):
			l.line_no = i+1
	def _remove_line_(self, idx : int) -> None:
		" Unregister a line and removes one line of the file buffer "
		l = self.lines[idx]
		if l.buffer is not None:
			l.buffer.Unlink(l)
		self.lines.remove(l)
	def RemoveLine(self, idx : int):
		self._remove_line_(idx)
		self.UpdateLineNumbers()
	def RemoveLines(self, i_from : int, i_to : int):
		" Removes the range of lines indexed between i_from and i_to, inclusive "
		while i_from <= i_to:
			self._remove_line_(i_from)
			i_from += 1
		self.UpdateLineNumbers()
	def _insert_line_(self, idx : int, l : Line, reg : AnyBuffer) -> None:
		l.line_no = idx+1
		self.lines.insert(idx, l)
		reg.Link(l)
	def InsertLine(self, idx : int, l : Line, reg : AnyBuffer) -> None:
		self._insert_line_(idx, l, reg)
		self.UpdateLineNumbers()
	def GetInsertIdxAtTop(self) -> int:
		pos = None
		for i, l in enumerate(self.lines):
			if isinstance(l, (CommentLine, EmptyLine)):
				if pos is None:
					pos = i
			elif isinstance(l, (SectionLine, PersistenceLine)):
				break
			else:
				pos = None
		return (pos is not None) and pos or 0
	def GetInsertIdxAtBottom(self) -> int:
		pos = None
		for i, l in enumerate(self.lines):
			if isinstance(l, (CommentLine, EmptyLine)):
				if pos is None:
					pos = i
			elif isinstance(l, PersistenceLine):
				break
			else:
				pos = None
		if pos is None:
			return len(self.lines)
		return pos


class SectionBuffer(AnyBuffer):
	" This holds all lines belonging to a section"
	def __init__(self, file_buffer : FileBuffer) -> None:
		super().__init__()
		self.header : SectionLine | None = None
		self.file_buffer = file_buffer
	def Link(self, l : Line) -> None:
		assert isinstance(l, (EmptyLine, CommentLine, SectionLine, ValueLine, MultiLineStartLine, ContinuationEmptyLine, ContinuationLine, ContinuationCommentLine))
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
	def GetTitle(self) -> str:
		if self.header is None:
			return "Unknown section"
		else:
			return "S: " + self.header.section_name
	def FindValue(self, key : str) -> ValueLine | None:
		" Find key/value value, spot on. An active entry has priority over inactive ones. "
		inactive = None
		for l in self.lines:
			if isinstance(l, ValueLine):
				if l.key == key:
					if l.inactive:
						inactive = l
					else:
						return l
		# fallback to inactive line option
		return inactive
	def FindValueRange(self, key : str) -> list[Line]:
		" Find key/value value, including prologue comments and blank lines "
		top = None
		for i, l in enumerate(self.lines):
			if (top is None) and isinstance(l, (EmptyLine, CommentLine) ):
				top = i
			if isinstance(l, ValueLine):
				if l.key == key:
					if top is None:
						return self.lines[i:i+1]
					else:
						return self.lines[top:i+1]
				top = None
			elif isinstance(l, (SectionLine, MultiLineStartLine, ContinuationLine, ContinuationCommentLine)):
				top = None
		return []
	def UpdateValue(self, key : str, value) -> bool:
		" Update simple values "
		v = self.FindValue(key)
		if v:
			if v.inactive:
				v.ActivateLine()
			# Update value
			v.value = value
			# Apply to buffer
			v._update_(f"{v.key}: {v.value}")
			return True
		return False
	def FindMultiLineKey(self, key : str) -> MultiLineStartLine | None:
		" Find key value of a multiline entry, spot on. An active entry has priority over inactive ones. "
		inactive = None
		for l in self.lines:
			if isinstance(l, MultiLineStartLine):
				if l.key == key:
					if l.inactive:
						inactive = l
					else:
						return l
		# fallback to inactive line option
		return inactive
	def FindMultiLine(self, key : str) -> tuple[MultiLineStartLine, list[Line]] | None:
		head = self.FindMultiLineKey(key)
		if head is not None:
			top = self.GetPrologue(self.lines.index(head))
			i = top + 1
			while i < len(self.lines):
				if not isinstance(self.lines[i], (ContinuationLine, ContinuationCommentLine, ContinuationEmptyLine)):
					break
				i += 1
			return (head, self.lines[top:i])
		return None
	def GetMultiLine(self, key : str, skip_head = False) -> list[Line]|None:
		" Return the range of lines belonging to multi-line key. Lines are uncommented "
		ml = self.FindMultiLine(key)
		if ml is not None:
			head, lines = ml
			i = skip_head and lines.index(head) or 0
			assert i >= 0, "FindMultiLine() implementation fault"
			return lines[i:]
	def DeleteMultiLine(self, key : str) -> int|None:
		" Removes the entire contents of a multi-line value. This includes head comments and keys "
		ml = self.FindMultiLine(key)
		if ml is not None:
			lines : list[Line]
			head, lines = ml
			assert len(lines) > 0, "FindMultiLine() implementation fault"
			pos = lines[0].line_no-1
			self.file_buffer.RemoveLines(pos, lines[-1].line_no-1)
			return pos
	@staticmethod
	def FixContents(buffer : FileBuffer, i:int, edge:int) -> int:
		" Eventually reclassify a file buffer according to value type "
		while i < edge:
			obj = buffer.lines[i]
			if isinstance(obj, MultiLineStartLine):
				top_ml = i
				i2 = i + 1
				while i2 < edge:
					obj2 = buffer.lines[i2]
					if isinstance(obj2, (ContinuationLine, ContinuationCommentLine, CommentLine, EmptyLine, ContinuationEmptyLine)):
						i2 += 1
					else:
						break
				i = i2
				# since we captured comment lines and empty lines, they could belong to the next value, just go watch back a bit
				while (top_ml < i2):
					i2 -= 1
					if not isinstance(buffer.lines[i2], (CommentLine, EmptyLine)):
						# Makes sure that the range of multi-lines have only "continuation lines"
						while top_ml < i2:
							obj2 = buffer.lines[top_ml]
							if isinstance(obj2, CommentLine):
								nl = ContinuationCommentLine(obj2.line_no, obj2.raw_content, obj2.uncommented)
								nl.Parse()
								buffer.lines[top_ml] = nl
							elif isinstance(obj2, EmptyLine):
								nl = ContinuationEmptyLine(obj2.line_no, obj2.raw_content, obj2.uncommented)
								nl.Parse()
								buffer.lines[top_ml] = nl
							top_ml += 1
						break
				i = i2 + 1
			elif isinstance(obj, (ValueLine, EmptyLine, CommentLine, ContinuationCommentLine)):
				i += 1
			else:
				break
		# continue from...
		return i

	def UpdateMultiline(self, key : str, lines : list[str]):
		" Replaces an entire Multi-line value by a new contents "
		pos = self.DeleteMultiLine(key)
		if pos is None:
			pos = self.file_buffer.GetInsertIdxAtBottom()
		assert True, "TODO"

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
	def GetTitle(self) -> str:
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
	def GetTitle(self) -> str:
		return "Persistence"


class Contents(object):
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
	
	def _collect_section_(self, start : int, i : int, head : SectionLine) -> int:
		top = i
		i = SectionBuffer.FixContents(self.file_buffer, i + 1, len(self.file_buffer.lines))
		# Strip at the end; blank lines and comments are always header of the next section
		while i >= top:
			i -= 1
			obj = self.file_buffer.lines[i]
			if not isinstance(obj, (EmptyLine, CommentLine)):
				i += 1
				break
		# Klipper allows split of sections
		sec = self.FindSection(head.section_name) or SectionBuffer(self.file_buffer)
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
				start = i = self._collect_section_(start, i, obj)
			elif isinstance(obj, PersistenceLine):
				start = i = self._collect_persistence_(start, i)
			else:
				raise ValueError(f"Line {i + 1}: Unexpected line type found in file: '{repr(obj)}'")

	def Load(self, fname : str) -> None:
		" Loads a Klipper-compatible file and groups line in logical structure "
		assert len(self.file_buffer.lines) == 0, "Object already has contents"
		self.file_buffer.Load(fname)
		self._collect0_()

	def FindSection(self, label : str) -> SectionBuffer | None:
		for sec in self.sections:
			if sec.header is None:
				loc = sec.GetSingleLocation()
				raise RuntimeError("Section in line range {str(loc)} was not correctly parsed")
			if sec.header.section_name == label:
				return sec
		return None
	
