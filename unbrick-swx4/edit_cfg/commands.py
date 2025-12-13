#
# -*- coding: UTF-8 -*-
#
# Spellchecker: words fname libtools

from functools import total_ordering

from .contents import AnyBuffer, Contents, SectionBuffer
from .line import *
from .libtools import EncodeB64, DecodeB64, StringCRC


@total_ordering
class SectionInfo(object):
	" Stores very basic information about sections keys "
	def __init__(self, label : str, line_no : int, active : bool, is_head : bool, crc : int|str) -> None:
		# The label of the section. Sections can be split throughout the file; so uniqueness is not guaranteed
		self.label = label
		# Line where it happens, (same as value shown in a text editor)
		self.line_no = line_no
		# Section can be commented out
		self.active = active
		# A section is allowed to be split; if this is true, this the head of the section
		self.is_head = is_head
		# CRC of section
		if isinstance(crc, int):
			crc = f'{crc:08X}'
		self.crc = crc
	def __repr__(self) -> str:
		return f"SectionInfo({repr(self.label)}, {repr(self.line_no)}, {repr(self.active)}, {repr(self.is_head)}, {repr(self.crc)})"
	def __eq__(self, o):
		if not isinstance(o, SectionInfo):
			return False
		return self.label == o.label \
			and (self.line_no == o.line_no) \
			and (self.active == o.active) \
			and (self.is_head == o.is_head) \
			and (self.crc == o.crc)
	def __lt__(self, o):
		if not isinstance(o, SectionInfo):
			return False
		return self.label < o.label \
			and (self.label == o.label and self.line_no < o.line_no) \
			and (self.line_no == o.line_no and self.active < o.active) \
			and (self.active == o.active and self.is_head < o.is_head) \
			and (self.is_head == o.is_head and self.crc < o.crc)


@total_ordering
class KeyInfo(object):
	" Stores very basic information about section keys "
	def __init__(self, section : str, key : str, line_no : int, active : bool, is_multiline : bool, crc : int|str) -> None:
		self.section = section
		self.key = key
		# Line where it happens, (same as value shown in a text editor)
		self.line_no = line_no
		# Section can be commented out
		self.active = active
		self.is_multiline = is_multiline
		# CRC of line contents
		if isinstance(crc, int):
			crc = f'{crc:08X}'
		self.crc = crc
	def __repr__(self) -> str:
		return f"KeyInfo({repr(self.section)}, {repr(self.key)}, {repr(self.line_no)}, {repr(self.active)}, {repr(self.is_multiline)}, {repr(self.crc)})"
	def __eq__(self, o):
		if not isinstance(o, KeyInfo):
			return False
		return self.section == o.section \
			and (self.key == o.key) \
			and (self.line_no == o.line_no) \
			and (self.active == o.active) \
			and (self.is_multiline == o.is_multiline) \
			and (self.crc == o.crc)
	def __lt__(self, o):
		if not isinstance(o, KeyInfo):
			return False
		return self.section < o.section \
			and (self.section == o.section and self.key < o.key) \
			and (self.key == o.key and self.line_no < o.line_no) \
			and (self.line_no == o.line_no and self.active < o.active) \
			and (self.active == o.active and self.is_multiline < o.is_multiline) \
			and (self.is_multiline == o.is_multiline and self.crc < o.crc)


@total_ordering
class MultiLineData(object):
	" A class to explicitly transport B64 data having encoded contents of `list[Line]`"
	def __init__(self, data : str|list[Line], crc : str|None = None) -> None:
		if isinstance(data, str):
			self.b64 = data	# presumably a valid b64 string!
			assert crc is not None, "If using a B64 string, you have to provide a CRC value"
			self.crc = crc
		else:
			self.b64 = EncodeB64(repr(data))
			self.crc = crc or StringCRC(AnyBuffer.GetLinesEssence(data), 0)
	def __repr__(self) -> str:
		return f"MultiLineData({repr(self.b64)}, {repr(self.crc)})"
	def __str__(self) -> str:
		return self.b64
	def __eq__(self, o):
		if not isinstance(o, MultiLineData):
			return False
		return self.b64 == o.b64
	def __lt__(self, o):
		if not isinstance(o, MultiLineData):
			return False
		return self.b64 < o.b64
	def GetLines(self) -> list[Line]:
		data = eval(DecodeB64(self.b64))
		assert isinstance(data, list), "Invalid use of this class. B64 is valid but cannot be reinterpreted."
		assert len(data) == 0 or isinstance(data[0], Line),  "Invalid use of this class. B64 is valid but cannot be reinterpreted."
		return  data


class Commands(object):
	def __init__(self, fname) -> None:
		self.fname = fname
		self.contents = Contents()
		self.contents.Load(fname)

	def Save(self):
		self.contents.file_buffer.Save(self.fname)

	def ListSections(self, qry : str) -> list[SectionInfo]:
		res = []
		for s in self.contents.file_buffer.MatchSection(qry):
			is_head = False
			crc = 0
			if isinstance(s.buffer, SectionBuffer):
				is_head = (s.buffer.header is s)
				if is_head:
					crc = StringCRC(s.buffer.GetLineEssence(), 0)
			res.append(SectionInfo(s.section_name, s.line_no, not s.inactive, is_head, crc))
		return res
	def ListSectionsB64(self, qry : str) -> str:
		return EncodeB64(repr(self.ListSections(qry)))

	def ListSection(self, section : str) -> SectionInfo | None:
		buffer = self.contents.FindSection(section)
		if buffer and buffer.header:
			crc = StringCRC(buffer.GetLineEssence(), 0)
			return SectionInfo(buffer.header.section_name, buffer.header.line_no, not buffer.header.inactive, True, crc)

	def ReadSec(self, section : str) -> str|None:
		sec_buf = self.contents.FindSection(section)
		if sec_buf is not None:
			return EncodeB64(repr(sec_buf.lines))

	def RenSec(self, old_name : str, new_name : str) -> int|None:
		" Renames a section. "
		buffer = self.contents.FindSection(old_name)
		if buffer:
			return buffer.RenSection(new_name)

	def DelSec(self, section : str) -> int|None:
		" Renames a section. "
		buffer = self.contents.FindSection(section)
		if buffer:
			ml = buffer.lines[:]	# shallow copy
			pos = self.contents.file_buffer.RemoveLineList(ml)
			self.contents.sections.remove(buffer)
			return pos

	def ListKey(self, section : str, key : str) -> KeyInfo | None:
		" Returns meta-data for a given key. "
		" If the key does not exists `None` is returned. "
		buffer = self.contents.FindSection(section)
		if buffer:
			l = buffer.FindAnyKey(key)
			if isinstance(l, ValueLine):
				crc = StringCRC(l.uncommented, 0)
				return KeyInfo(section, l.key, l.line_no, not l.inactive, False, crc)
			elif isinstance(l, MultiLineStartLine):
				ml = buffer.GetMultiLine(l)
				if ml:
					crc = StringCRC(AnyBuffer.GetLinesEssence(ml), 0)
				else:
					crc = 0
				return KeyInfo(section, l.key, l.line_no, not l.inactive, False, crc)

	def ListKeys(self, section : str) -> list[KeyInfo]:
		" Filters the list of section returning meta-data for each Section that matches the search criteria."
		" This is similar to the `dir` command on the prompt, accepting wildcards as filters. "
		res = []
		buffer = self.contents.FindSection(section)
		if buffer:
			for l in buffer.lines:
				crc = 0
				if isinstance(l, ValueLine):
					crc = StringCRC(l.uncommented, 0)
					res.append(KeyInfo(section, l.key, l.line_no, not l.inactive, False, crc))
				elif isinstance(l, MultiLineStartLine):
					ml = buffer.GetMultiLine(l)
					if ml:
						crc = StringCRC(AnyBuffer.GetLinesEssence(ml), 0)
					res.append(KeyInfo(section, l.key, l.line_no, not l.inactive, True, crc))
		return res
	def ListKeysB64(self, section : str) -> str:
		" Filters the list of section returning meta-data for each Section that matches the search criteria."
		" This is similar to the `dir` command on the prompt, accepting wildcards as filters. "
		" The result is an encoded base64 string, ideal for transport on normal strings. Decode with: "
		"    eval(DecodeB64(data))"
		return EncodeB64(repr(self.ListKeys(section)))

	def GetKey(self, section : str, key : str) -> str|MultiLineData|None:
		buffer = self.contents.FindSection(section)
		if buffer:
			l = buffer.FindAnyKey(key)
			if isinstance(l, ValueLine):
				return l.value
			elif isinstance(l, MultiLineStartLine):
				ml = buffer.GetMultiLine(l)
				if ml:
					return MultiLineData(ml)

	def EditKey(self, section : str, key : str, value : str) -> bool|None:
		" Allows to edit simple value. If the key does not exists a new is appended. "
		" Multi-line values aren't supported here, since they can only be integrally replaced. "
		buffer = self.contents.FindSection(section)
		if buffer:
			l = buffer.FindAnyKey(key)
			if isinstance(l, ValueLine):
				l.SetValue(value)
				return True
			elif isinstance(l, MultiLineStartLine):
				return False
			else:
				buffer.AppendValue(key, value)
				return True

	def EditKeyML(self, section : str, key : str, value : str) -> bool|None:
		" Allows to replace the entire multi-line key. If the key does not exists a new is appended. "
		" Note that Multi-line values replaces the entire data block, including heading comments and "
		" the key itself. THis means that wrong data excludes any preexisting line containing a key. "
		buffer = self.contents.FindSection(section)
		nl = eval(DecodeB64(value))

		assert isinstance(nl, list), "Unexpected contents!"
		assert len(nl) > 0, "We need some contents to be replaced. Consider one of the delete methods."
		assert isinstance(nl[0], Line), "Unexpected contents!"

		if buffer:
			l = buffer.FindAnyKey(key)
			if isinstance(l, ValueLine):
				return False
			elif isinstance(l, MultiLineStartLine):
				ml = buffer.GetMultiLine(l)
				if ml is not None:
					pos = self.contents.file_buffer.RemoveLineList(ml)
					self.contents.file_buffer.InsertLineList(pos, nl, buffer)
					return True
			else:
				for l in nl:
					if isinstance(l, MultiLineStartLine):
						if l.key != key:
							l.SetKey(key)
				buffer.AppendValueML(nl)
				return True

	def DelKey(self, section : str, key : str) -> bool|None:
		" Removes a key from a section. "
		" Returns `None` if section does not exists, `False` if key does not exists or `True` if key was removed "
		buffer = self.contents.FindSection(section)
		if buffer:
			l = buffer.FindAnyKey(key)
			if isinstance(l, ValueLine):
				ml = buffer.FindValueRange(key)
			elif isinstance(l, MultiLineStartLine):
				ml = buffer.GetMultiLine(l)
			else:
				return False
			if ml is None:
				return False
			self.contents.file_buffer.RemoveLineList(ml)
			return True

	def GetPersistenceB64(self) -> str:
		return EncodeB64(repr([l.raw_content for l in self.contents.persistence.lines]))

