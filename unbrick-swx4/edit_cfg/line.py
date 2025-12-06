#
# -*- coding: UTF-8 -*-
#
# Spellchecker:	words libtools

import re
from abc import ABC, abstractmethod
#from typing import Optional, List

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
		from .libtools import StringEssence
		return StringEssence(self.line)
	def GetCRC(self, seed : int) -> int:
		from .libtools import StringCRC
		return StringCRC(self.line, seed)


class AnyBuffer(ABC):
	" An object that groups lines in a logical form "
	def __init__(self) -> None:
		super().__init__()
		self.lines : list[Line] = []
	def GetLocation(self) -> list[Loc]:
		" Returns the line locations that buffer owns "
		res = []
		loc = None
		for l in self.lines:
			if not loc:
				loc = Loc(l.line_no, l.line_no)
			elif loc.idx_n + 1 == l.line_no:
				loc.idx_n = l.line_no
			else:
				res.append(loc)
				loc = Loc(l.line_no, l.line_no)
		if loc is not None:
			res.append(loc)
		return res
	def LinkList(self, lines : list[Line]) -> None:
		" Links a range of lines at once "
		for l in lines:
			self.Link(l)
	@abstractmethod
	def Link(self, l : Line) -> None:
		" Links a line to this collection "
		assert l.buffer is None, "Cannot add a line that is already owned"
		# Takes ownership
		l.buffer = self
		self.lines.append(l)
	@abstractmethod
	def Unlink(self, l : Line) -> None:
		" Unlinks a line from this collection"
		assert l.buffer is self, "Line does not belong to this collection"
		self.lines.remove(l)
		l.buffer = None


class Line(ABC):	# ABC = Abstract Base Class
	COMMENT_EXTRACT = re.compile(r'^([^#;]*)[#;]?.*$')
	def __init__(self, line_no : int, raw_content: str, uncommented : str):
		self.buffer : AnyBuffer|None = None
		self.line_no = line_no
		self.raw_content = raw_content
		self.uncommented = uncommented
	@abstractmethod
	def Parse(self) -> None:
		pass
	@abstractmethod
	def Update(self) -> None:
		pass
	def __repr__(self) -> str:
		return f"{self.__class__.__name__}: {self.raw_content!r}"
	def __str__(self) -> str:
		return self.raw_content
	@staticmethod
	def UncommentLine(l : str) -> str:
		m = Line.COMMENT_EXTRACT.match(l)
		if m:
			l = m[1].rstrip()
		return l
	def _update_(self, uncomment : str) -> None:
		l = len(self.uncommented)
		if l < len(self.raw_content):
			tail = self.raw_content[l:]
		else:
			tail = ''
		self.uncommented = uncomment
		self.raw_content = uncomment + tail

class EmptyLine(Line):
	def Parse(self) -> None:
		assert not self.raw_content.strip()
	def Update(self) -> None:
		raise RuntimeError("Empty lines are immutable")

class CommentLine(Line):
	def Parse(self) -> None:
		assert self.raw_content.startswith(("#", ";"))
	def Update(self) -> None:
		raise RuntimeError("Only replacement allowed for this element")

class PersistenceLine(Line):
	def Parse(self) -> None:
		assert self.raw_content.startswith("#*#")
	def Update(self) -> None:
		raise RuntimeError("Only replacement allowed for this element")

class SectionLine(Line):
	PATTERN = re.compile(r'^\[([a-zA-Z0-9_\-\ ]+)\]\s*$')
	def __init__(self, line_no : int, raw_content: str, uncommented : str, inactive = False):
		pre = inactive  and ';' or ''
		super().__init__(line_no, pre + raw_content, pre + uncommented)
		self.section_name = ""
		self.inactive = inactive
	def Parse(self) -> None:
		match = self.PATTERN.match(self.uncommented[int(self.inactive):])
		if not match:
			raise ValueError(f"Invalid section line: {self.raw_content}")
		self.section_name = match.group(1)
	def Update(self) -> None:
		self._update_(f'[{self.section_name}]')

class IncludeLine(Line):
	PATTERN = re.compile(r'^\[include\s+([^\s\[\]]+)\]\s*$')
	def __init__(self, line_no : int, raw_content: str, uncommented : str, inactive = False):
		pre = inactive  and ';' or ''
		super().__init__(line_no, pre + raw_content, pre + uncommented)
		self.filename = ""
		self.inactive = inactive
	def Parse(self) -> None:
		match = self.PATTERN.match(self.uncommented[int(self.inactive):])
		if not match:
			raise ValueError(f"Invalid include line: {self.raw_content}")
		self.filename = match.group(1)
	def Update(self) -> None:
		self._update_(f'[include {self.filename}]')

class ValueLine(Line):
	PATTERN = re.compile(r'^([a-zA-Z0-9_]+)\s*[:=]\s*(.*)$')
	def __init__(self, line_no : int, raw_content: str, uncommented : str, inactive = False):
		pre = inactive and ';' or ''
		super().__init__(line_no, pre + raw_content, pre + uncommented)
		self.key = ""
		self.value = ""
		self.inactive = inactive
	def Parse(self) -> None:
		match = self.PATTERN.match(self.uncommented[int(self.inactive):])
		if not match:
			raise ValueError(f"Invalid value line: {self.raw_content}")
		self.key, self.value = match.groups()
	def Update(self) -> None:
		self._update_(f"{self.key}: {self.value}")

class MultiLineStartLine(Line):
	PATTERN = re.compile(r'^([a-zA-Z0-9_]+)\s*[:=]\s*$')
	def __init__(self, line_no : int, raw_content: str, uncommented : str, inactive = False):
		pre = inactive and ';' or ''
		super().__init__(line_no, pre + raw_content, pre + uncommented)
		self.key = ""
		self.inactive = inactive
	def Parse(self) -> None:
		match = self.PATTERN.match(self.uncommented[int(self.inactive):])
		if not match:
			raise ValueError(f"Invalid multi-line start line: {self.raw_content}")
		self.key = match.group(1)
	def Update(self) -> None:
		raise RuntimeError("Only replacement allowed for this element")

class ContinuationLine(Line):
	def __init__(self, line_no : int, raw_content: str, uncommented : str):
		super().__init__(line_no, raw_content, uncommented)
		self.content = ""
	def Parse(self) -> None:
		if not self.uncommented.startswith((" ", "\t")):
			raise ValueError(f"Invalid continuation line: {self.raw_content}")
		self.content = self.raw_content.strip()
	def Update(self) -> None:
		raise RuntimeError("Only replacement allowed for this element")

class ContinuationCommentLine(Line):
	PATTERN = re.compile(r'^\s+[#;]')
	PATTERN_POST = re.compile(r'^[;#]+(?=.*(\t.*\s|\s.*\t|\t{1,}| {3,}))')	# this is allowed only if previous line is also a continuation
	def Parse(self) -> None:
		match = self.PATTERN.match(self.raw_content)
		if not match:
			# For the case a continuation line was commented at the head of the line
			match = self.PATTERN_POST.match(self.raw_content)
			if not match:
				raise ValueError(f"Invalid continuation comment line: {self.raw_content}")
	def Update(self) -> None:
		raise RuntimeError("Only replacement allowed for this element")


class LineFactory(object):
	COMMENT_TEXT = re.compile(r'^[#;]+\s*(.*)$')
	def __init__(self) -> None:
		self.line_no = 0
		self.unlock_persistence = False
	def _new_(self, raw_content: str, pre_line : Line|None) -> Line | None:
		self.line_no += 1
		raw_content = raw_content.rstrip()
		uncommented = Line.UncommentLine(raw_content)
		stripped = raw_content.strip()
		if not stripped:
			if self.unlock_persistence:
				return None
			return EmptyLine(self.line_no, raw_content, uncommented)
		elif raw_content.startswith("#*#"):
			if self.unlock_persistence or ("---- SAVE_CONFIG ----" in raw_content):
				self.unlock_persistence = True
				return PersistenceLine(self.line_no, raw_content, uncommented)
		if self.unlock_persistence:
			raise ValueError(f"Unexpected line after persistence: {raw_content}")
		if raw_content.startswith(("#", ";")):
			# First, make sure this isn't a setup line that was commented out
			m = self.COMMENT_TEXT.match(raw_content)
			if m:
				raw2 = m[1]
				# inactive line can also have comments
				unc2 = Line.UncommentLine(raw2)
				# Include line found
				if uncommented.lower().startswith("[include"):
					return IncludeLine(self.line_no, raw_content, uncommented, True)
				# Multi-line pattern found?
				m = MultiLineStartLine.PATTERN.match(unc2)
				if m:
					return MultiLineStartLine(self.line_no, raw2, unc2, True)
				# Value-line pattern found?
				m = ValueLine.PATTERN.match(unc2)
				if m:
					return ValueLine(self.line_no, raw2, unc2, True)
				# Section head found?
				m = SectionLine.PATTERN.match(unc2)
				if m:
					return SectionLine(self.line_no, raw2, unc2, True)
			if pre_line:
				if isinstance(pre_line, (ContinuationCommentLine, ContinuationLine, MultiLineStartLine, ValueLine)):
					m = ContinuationCommentLine.PATTERN_POST.match(raw_content)
					if m:
						return ContinuationCommentLine(self.line_no, raw_content, uncommented)
			return CommentLine(self.line_no, raw_content, uncommented)
		if raw_content[0].isspace():
			if stripped.startswith(("#", ";")):
				return ContinuationCommentLine(self.line_no, raw_content, uncommented)
			else:
				return ContinuationLine(self.line_no, raw_content, uncommented)
		if uncommented.startswith("[") and uncommented.endswith("]"):
			if uncommented.lower().startswith("[include"):
				return IncludeLine(self.line_no, raw_content, uncommented)
			else:
				return SectionLine(self.line_no, raw_content, uncommented, False)
		elif re.match(r"^[a-zA-Z0-9_]+[\s]*[:=]", uncommented):
			if uncommented.endswith("=") or uncommented.endswith(":"):
				return MultiLineStartLine(self.line_no, raw_content, uncommented)
			else:
				return ValueLine(self.line_no, raw_content, uncommented)
		else:
			raise ValueError(f"Unrecognized line: {raw_content}")
	def New(self, raw_content: str, pre_line : Line|None) -> Line | None:
		obj = self._new_(raw_content, pre_line)
		if obj is not None:
			obj.Parse()
		return obj


