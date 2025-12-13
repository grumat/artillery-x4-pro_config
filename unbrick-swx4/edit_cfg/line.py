#
# -*- coding: UTF-8 -*-
#
# Spellchecker:	words libtools toggleable gcode

import re
from abc import ABC, abstractmethod
from typing import final
#from typing import Optional, List

from .loc import Loc
from .libtools import IsLikeGCode, GetHeadSpacesOfCommentedLine, StringEssence


class AnyBuffer(ABC):
	" An object that groups lines in a logical form "
	def __init__(self) -> None:
		super().__init__()
		self.lines : list[Line] = []
	@abstractmethod
	def GetTitle(self) -> str:
		return "Invalid Signature"
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
	def Sort(self):
		self.lines.sort(key = lambda line : line.line_no)
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
	def GetSingleLocation(self) -> Loc:
		locs = self.GetLocation()
		assert len(locs) > 0, "Empty buffers shall not exist!"
		return locs[0]
	def LinkList(self, lines : list[Line]) -> None:
		" Links a range of lines at once "
		for l in lines:
			self.Link(l)
	def GetPrologue(self, i : int) -> int:
		"""
		This locates the firs comment/blank line associated to current line. 
		The input line should not be a neutral line, and the return value is the same of the input 
		value if nothing is found.
		By convention every element will have blank line and comments as prefixes, never postfixes.
		"""
		assert (i >= 0) and (i <= len(self.lines)), "Invalid index"
		ref = self.lines[i]
		i -= 1
		if isinstance(ref, ContinuationLine):
			while i >= 0:
				l = self.lines[i]
				if not isinstance(l, (ContinuationEmptyLine, ContinuationCommentLine)):
					break
				i -= 1
		elif isinstance(ref, (PersistenceLine, SectionLine, IncludeLine, ValueLine, MultiLineStartLine)):
			while i >= 0:
				l = self.lines[i]
				if not isinstance(l, (EmptyLine, CommentLine)):
					break
				i -= 1
		else:
			raise RuntimeError(f"Unexpected line type {repr(ref)}")
		return i + 1
	@staticmethod
	def GetCrucialLines(lines : list[Line]) -> list[Line]:
		return [l for l in lines if (isinstance(l, ToggleableLine) and (l.inactive == False)) or isinstance(l, PersistenceLine)]
	@staticmethod
	def GetLinesEssence(lines : list[Line]) -> str:
		return '\n'.join([l.uncommented for l in AnyBuffer.GetCrucialLines(lines)])
	def GetLineEssence(self) -> str:
		return AnyBuffer.GetLinesEssence(self.lines)

class Line(ABC):	# ABC = Abstract Base Class
	COMMENT_EXTRACT = re.compile(r'^([^#;]*)[#;]?.*$')
	def __init__(self, line_no : int, raw_content: str, uncommented : str):
		self.buffer : AnyBuffer|None = None
		self.line_no = line_no
		self.raw_content = raw_content
		self.uncommented = uncommented
	@abstractmethod
	def _parse_(self) -> None:
		pass
	@abstractmethod
	def Update(self) -> None:
		pass
	@abstractmethod
	def __repr__(self):
		return f"Line(line_no=0, raw_content={self.raw_content}, uncommented={self.uncommented})"
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

@final
class EmptyLine(Line):
	def __init__(self, line_no : int, raw_content: str, uncommented : str):
		super().__init__(line_no, raw_content, uncommented)
		self._parse_()
	def _parse_(self) -> None:
		assert not self.raw_content.strip()
	def Update(self) -> None:
		raise RuntimeError("Empty lines are immutable")
	def __repr__(self):
		return f"EmptyLine(0, {repr(self.raw_content)}, {repr(self.uncommented)})"

@final
class CommentLine(Line):
	def __init__(self, line_no : int, raw_content: str, uncommented : str):
		super().__init__(line_no, raw_content, uncommented)
		self._parse_()
	def _parse_(self) -> None:
		assert self.raw_content.startswith(("#", ";"))
	def Update(self) -> None:
		raise RuntimeError("Only replacement allowed for this element")
	def __repr__(self):
		return f"CommentLine(0, {repr(self.raw_content)}, {repr(self.uncommented)})"

@final
class PersistenceLine(Line):
	def __init__(self, line_no : int, raw_content: str, uncommented : str):
		super().__init__(line_no, raw_content, uncommented)
		self._parse_()
	def _parse_(self) -> None:
		assert self.raw_content.startswith("#*#")
	def Update(self) -> None:
		raise RuntimeError("Only replacement allowed for this element")
	def __repr__(self):
		return f"PersistenceLine(0, {repr(self.raw_content)}, {repr(self.uncommented)})"

class ToggleableLine(Line):
	def __init__(self, line_no: int, raw_content: str, uncommented: str, inactive : bool, prefix = ';'):
		assert ';' in prefix, "Prefix option not validated. May not work out of the box..."
		self.prefix = prefix
		if inactive:
			pre = self.prefix
			# continuation lines starts with blanks, so the prefix
			if self.prefix.startswith(('\t', ' ')):
				raw_content = raw_content.lstrip()
				uncommented = uncommented.lstrip()
		else:
			pre = ''

		super().__init__(line_no, pre + raw_content, pre + uncommented)
		self.inactive = inactive
	def ActivateLine(self):
		" Reactivate a line "
		assert self.inactive, "Line is already active!"
		self.inactive = False
		new_pre = self.prefix.replace(';', '')
		l = len(self.prefix)
		if len(self.uncommented) >= l:
			self.uncommented = new_pre + self.uncommented[l:]
		if len(self.raw_content) >= l:
			self.raw_content = new_pre + self.raw_content[l:]
	def GetWouldBeRaw(self) -> str:
		if self.inactive:
			pre = self.prefix.replace(';', '')
			l = len(self.prefix)
			if len(self.raw_content) >= l:
				return pre + self.raw_content[l:]
		return self.raw_content
	def GetWouldBeUnc(self) -> str:
		if self.inactive:
			pre = self.prefix.replace(';', '')
			l = len(self.prefix)
			if len(self.uncommented) >= l:
				return pre + self.uncommented[l:]
		return self.uncommented

@final
class SectionLine(ToggleableLine):
	PATTERN = re.compile(r'^\[([a-zA-Z0-9_\-\ ]+)\]\s*$')
	def __init__(self, line_no : int, raw_content: str, uncommented : str, inactive = False):
		super().__init__(line_no, raw_content, uncommented, inactive)
		self.section_name = ""
		self._parse_()
	def __repr__(self):
		return f"SectionLine(0, {repr(self.GetWouldBeRaw())}, {repr(self.GetWouldBeUnc())}, {repr(self.inactive)})"
	def _parse_(self) -> None:
		match = self.PATTERN.match(self.GetWouldBeUnc())
		if not match:
			raise ValueError(f"Invalid section line: {self.raw_content}")
		self.section_name = match.group(1)
	def Update(self) -> None:
		self._update_(f'[{self.section_name}]')

@final
class IncludeLine(ToggleableLine):
	PATTERN = re.compile(r'^\[include\s+([^\s\[\]]+)\]\s*$')
	def __init__(self, line_no : int, raw_content: str, uncommented : str, inactive = False):
		super().__init__(line_no, raw_content, uncommented, inactive)
		self.filename = ""
		self._parse_()
	def __repr__(self):
		return f"IncludeLine(0, {repr(self.GetWouldBeRaw())}, {repr(self.GetWouldBeUnc())}, {repr(self.inactive)})"
	def _parse_(self) -> None:
		match = self.PATTERN.match(self.GetWouldBeUnc())
		if not match:
			raise ValueError(f"Invalid include line: {self.raw_content}")
		self.filename = match.group(1)
	def Update(self) -> None:
		self._update_(f'[include {self.filename}]')

@final
class ValueLine(ToggleableLine):
	PATTERN = re.compile(r'^([a-zA-Z0-9_]+)\s*[:=]\s*(.*)$')
	def __init__(self, line_no : int, raw_content: str, uncommented : str, inactive = False):
		super().__init__(line_no, raw_content, uncommented, inactive)
		self.key = ""
		self.value = ""
		self._parse_()
	def __repr__(self):
		return f"ValueLine(0, {repr(self.GetWouldBeRaw())}, {repr(self.GetWouldBeUnc())}, {repr(self.inactive)})"
	def _parse_(self) -> None:
		match = self.PATTERN.match(self.GetWouldBeUnc())
		if not match:
			raise ValueError(f"Invalid value line: {self.raw_content}")
		self.key, self.value = match.groups()
	def Update(self) -> None:
		self._update_(f"{self.key}: {self.value}")
	def SetValue(self, value : str):
		self.value = value
		self.Update()

@final
class MultiLineStartLine(ToggleableLine):
	PATTERN = re.compile(r'^([a-zA-Z0-9_]+)\s*[:=]\s*$')
	def __init__(self, line_no : int, raw_content: str, uncommented : str, inactive = False):
		super().__init__(line_no, raw_content, uncommented, inactive)
		self.key = ""
		self._parse_()
	def __repr__(self):
		return f"MultiLineStartLine(0, {repr(self.GetWouldBeRaw())}, {repr(self.GetWouldBeUnc())}, {repr(self.inactive)})"
	def _parse_(self) -> None:
		match = self.PATTERN.match(self.GetWouldBeUnc())
		if not match:
			raise ValueError(f"Invalid multi-line start line: {self.raw_content}")
		self.key = match.group(1)
	def SetKey(self, key : str):
		self._update_(f"{key}:")
		self._parse_()
	def Update(self) -> None:
		raise RuntimeError("Only replacement allowed for this element")

@final
class ContinuationEmptyLine(Line):
	def __init__(self, line_no : int, raw_content: str, uncommented : str):
		super().__init__(line_no, raw_content, uncommented)
		self._parse_()
	def __repr__(self):
		return f"ContinuationEmptyLine(0, {repr(self.raw_content)}, {repr(self.uncommented)})"
	def _parse_(self) -> None:
		assert not self.raw_content.strip()
	def Update(self) -> None:
		raise RuntimeError("Empty lines are immutable")

@final
class ContinuationLine(ToggleableLine):
	PATTERN = re.compile(r'^(\s+).*$')
	def __init__(self, line_no : int, raw_content: str, uncommented : str, inactive = False):
		m = self.PATTERN.match(raw_content)
		assert m is not None, "Invalid continuation line"
		super().__init__(line_no, raw_content, uncommented, inactive, m[1]+';')
		self.content = ""
		self._parse_()
	def __repr__(self):
		return f"ContinuationLine(0, {repr(self.GetWouldBeRaw())}, {repr(self.GetWouldBeUnc())}, {repr(self.inactive)})"
	def _parse_(self) -> None:
		test = self.GetWouldBeUnc()
		if not test.startswith((" ", "\t")):
			raise ValueError(f"Invalid continuation line: {self.raw_content}")
		self.content = self.GetWouldBeRaw()
	def Update(self) -> None:
		raise RuntimeError("Only replacement allowed for this element")

@final
class ContinuationCommentLine(Line):
	PATTERN = re.compile(r'^\s+[#;]')
	PATTERN_POST = re.compile(r'^[;#]+(?=.*(\t.*\s|\s.*\t|\t{1,}| {3,}))')	# this is allowed only if previous line is also a continuation
	def __init__(self, line_no : int, raw_content: str, uncommented : str):
		super().__init__(line_no, raw_content, uncommented)
		self._parse_()
	def __repr__(self):
		return f"ContinuationCommentLine(0, {repr(self.raw_content)}, {repr(self.uncommented)})"
	def _parse_(self) -> None:
		match = self.PATTERN.match(self.raw_content)
		if not match:
			# For the case a continuation line was commented at the head of the line
			match = self.PATTERN_POST.match(self.raw_content)
			if not match:
				raise ValueError(f"Invalid continuation comment line: {self.raw_content}")
	def Update(self) -> None:
		raise RuntimeError("Only replacement allowed for this element")


class LineFactory(object):
	COMMENT_TEXT = re.compile(r'^[#;]+(.*)$')
	def __init__(self) -> None:
		self.line_no = 0
		self.unlock_persistence = False
	def _new_(self, raw_content: str, pre_line : Line|None) -> Line | None:
		self.line_no += 1
		is_continuation = isinstance(pre_line, (ContinuationCommentLine, ContinuationLine, MultiLineStartLine))
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
			# Takes the contents of the comment
			m = self.COMMENT_TEXT.match(raw_content)
			if m:
				# Before saying that we have a comment we want to check patterns for commented lines
				raw3 = m[1]
				raw2 = raw3.lstrip()
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
				if is_continuation and raw3.startswith((' ', '\t')):
					unc3 = Line.UncommentLine(raw3)
					return ContinuationLine(self.line_no, raw3, unc3, True)
			if is_continuation:
				m = ContinuationCommentLine.PATTERN_POST.match(raw_content)
				if m:
					return ContinuationCommentLine(self.line_no, raw_content, uncommented)
			return CommentLine(self.line_no, raw_content, uncommented)
		if is_continuation and raw_content[0].isspace():
			if stripped.startswith(("#", ";")):
				m = self.COMMENT_TEXT.match(stripped)
				if m:
					raw2 = m[1].strip()
					unc2 = Line.UncommentLine(raw2)
					if IsLikeGCode(unc2):
						spc = GetHeadSpacesOfCommentedLine(raw_content)
						return ContinuationLine(self.line_no, spc + raw2, spc + unc2, True)
				return ContinuationCommentLine(self.line_no, raw_content, uncommented)
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
		return obj


