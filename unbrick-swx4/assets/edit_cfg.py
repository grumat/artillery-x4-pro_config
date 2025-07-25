#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# This file contains lots of tools to edit `printer.cfg` Klipper files
# It has to be "minified" with the `minify_python_code.py` script and
# sent to the printer, so that local editing is possible.

import sys
import os
import re
import zlib
import bz2
import base64
import fnmatch
from typing import Callable

MODULE = sys.modules[__name__]
DF = r"/home/mks/klipper_config/printer.cfg"

class Loc(object):
	"""Line location in the source file (0-based indexes)"""
	def __init__(self, i_0 : int = None, i_n : int = None):
		self.idx_0 = i_0
		self.idx_n = i_n
	def __bool__(self):
		return self.idx_0 is not None
	def __str__(self):
		if self.idx_0:
			return self.idx_n and f"[{self.idx_0}:{self.idx_n}]" or f"[{self.idx_0}]"
		return "[]"
	def IsNoLoc(self):
		"""Test for empty location"""
		return self.idx_0 is None
	def IsRangeLoc(self):
		"""Test for multiple lines location"""
		return self.idx_n is not None
	def IsInRange(self, lno : int) -> bool:
		if self.idx_0 is not None:
			if self.idx_n is not None:
				return (self.idx_0 <= lno) and (lno < self.idx_n)
			else:
				return self.idx_0 == lno
		return True

NO_LOC = Loc()

class Res(object):
	def __init__(self, c : int, val : str, loc : Loc = NO_LOC):
		self.code = c
		self.value = val
		self.loc = loc
	def __str__(self):
		"""Default way to print this object, used for the terminal communication"""
		return f"{self.code}{self.value}"
	def IsError(self):
		"""Every error has to use the '!' code"""
		return self.code == '!'
	def __bool__(self):
		return not self.IsError()
	def IsOk(self):
		"""
		Every success operation with no arguments uses the '.' code. The '=' and '*' 
		codes are also used for successful operations returning results
		"""
		return self.code in ('.', '=', '*')
	def IsString(self):
		"""A simple string response uses the '=' code"""
		return self.code == '='
	def IsBase64(self):
		"""A response block encoded in base64 uses the '*' code"""
		return self.code == '*'
	def IsObject(self):
		"""By convention a alpha codes are reserved for objects"""
		return self.code.isalpha()
	def IsKindOf(self, o : 'Res') -> bool:
		return (self.code == o.code) and (type(self.value) == type(o.value) and (self.value == o.value))

# General success result
OK = Res('.', "OK")
# Error returned when an argument is missing
NO_FN = Res('!', "FN")
# Error returned when an argument is missing
MISSING_ARG = Res('!', "ARG")
# Error returned when too many arguments are given
EXTRA_ARGS = Res('!', "ARG+")
# Data encoding invalid (Base64)
INV_ENC = Res('!', "ENC")
# Specified file does not exists
NO_FILE = Res('!', "FILE")
# You shall load the configuration file before writing
NO_READ = Res('!', "READ")
# No lines to be written (usually invalid call sequence or file)
EMPTY = Res('!', "EMPTY")
# Indicates that a multi-line key was found for an operation that can only handle single lines
ML_KEY = lambda loc : Res('!', "ML", loc)
# File has an invalid format (not a single section was found)
INV_FMT = Res('!', "FMT")
# The requested section was not found
NO_SECTION = Res('!', "SEC")
# More than one section matches your request
MULT_SECTION = Res('!', "SEC+")
# Error returned when a key was not found inside a section
NO_KEY = lambda loc : Res('!', "KEY", loc)
# More than one key matches your request (section has duplicates)
MULT_KEY = lambda loc : Res('!', "KEY+", loc)
# Invalid range (usually indicates an internal bug)
INV_RANGE = lambda loc : Res('!', "RANGE", loc)


def EncodeMultiLine(ml : str) -> str:
	"""Long stuff is compressed and converted to base64 so that we can transmit over the serial line"""
	# MLines's: extract text only
	if isinstance(ml[0], MLine):
		ml : 'list[MLine]'
		# Scan for trailing blank lines
		last = len(ml)
		while last > 0:
			last -= 1
			if not ml[last].is_empty:
				break
		# Be sure to preserve last blank line
		last += 2
		if last < len(ml):
			ml = ml[:last]
		ml = "".join([l.line for l in ml])
	# Any other list is considered having string
	elif isinstance(ml, list):
		ml = "".join(ml)
	# BZ2 compressor...
	pk = bz2.compress(ml.encode('utf-8'))
	# ...then BASE64 encoder
	enc = base64.b64encode(pk)
	# Finally, back to internal string representation
	return enc.decode('utf-8')

def DecodeMultiLine(b64 : str) -> list:
	"""Get BASE64 payload and convert to string list"""
	# Decode BASE64
	ba = base64.b64decode(b64.encode('utf-8'))
	# Decompress BZ2
	ml = bz2.decompress(ba).decode('utf-8')
	# Split lines into a list
	res = []
	t = ""
	for ch in ml:
		t += ch
		# Every entry stores a line
		if ch == '\n':
			res.append(t)
			t = ""
	# Don't forget the trailing line
	if t:
		res.append(t)
	return res


class Line(object):
	def __init__(self, l : str):
		self.raw = l
		self.unc = Line.UncommentLine(l)
	@staticmethod
	def UncommentLine(l : str) -> str:
		"""This removes line comments from the given line"""
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
		"""Total length of a raw line"""
		return len(self.raw)
	def IsLineEmpty(self) -> bool:
		"""Checks if a line is empty. Empty lines are most of the times ignored"""
		return not self.unc
	def HasLeadingBlanks(self):
		"""True if line has contents but starts with a leading space (multi-line values)"""
		return self.unc and self.unc[0].isspace()
	def HasKeyPattern(self):
		"""Does this line looks like a section key?"""
		return (not self.raw.startswith('[')) \
			and self.raw \
			and (self.raw[0].isalnum() or (self.raw[0] == '_')) \
			and (':' in self.unc)

class Context(object):
	"""Stores the context of the operation"""
	def __init__(self, args : list[str]):
		self.args = args
		self.cfg_file = None
		self.raw_lines : list[Line] = []
	def GetArg(self) -> str:
		"""Retrieves the next argument of the argument list"""
		if len(self.args):
			v = self.args[0]
			del self.args[0]
			return v
		return None
	def ReadLines(self) -> Res:
		"""Reads all lines of the configuration file and keep it in memory"""
		if not self.cfg_file:
			# Last argument allows you to set a custom cfg file
			self.cfg_file = self.GetArg()
			if not self.cfg_file:
				self.cfg_file = DF
			# Extra argument after file name. Not expected
			if self.args:
				return EXTRA_ARGS
			# Does the configuration file exists?
			if not os.path.exists(self.cfg_file):
				return NO_FILE
			# Now read all lines into buffer
			with open(self.cfg_file, "rt", encoding="UTF-8") as fh:
				for l in fh:
					self.raw_lines.append(Line(l))
		# Good!
		return OK
	def IsRangeValid(self, loc : Loc):
		if loc.idx_0 is not None:
			if (0 <= loc.idx_0) and (loc.idx_0 < len(self.raw_lines)):
				if loc.idx_n is None:
					return True
				if loc.idx_n > loc.idx_0:
					if (0 < loc.idx_n) and (loc.idx_n <= len(self.raw_lines)):
						return True
		return False
	def GetLines(self, loc : Loc):
		"""Returns a list of raw lines on the given range"""
		return [lr.raw for lr in self.raw_lines[loc.idx_0 : loc.idx_n]]
	def WriteLines(self) -> Res:
		"""Write the biffered lines into a temporary file, then replaces old instance"""
		# You cannot save before loading a configuration file
		if not self.cfg_file:
			return NO_READ
		# No contents (weird!)
		if not self.raw_lines:
			return EMPTY
		# Removes file extension
		tpl, _ = os.path.splitext(self.cfg_file)
		# Now search a file name that is really new
		idx = -1
		while True:
			idx += 1
			fn = f"{tpl}.{idx:03d}.cfg"
			if not os.path.exists(fn):
				break
		# Write the entire buffer into the temporary file
		with open(fn, "wt", encoding="UTF-8", newline='\n') as fh:
			fh.writelines([l.raw for l in self.raw_lines])
		# Success! Now delete old instance and replace file
		os.remove(self.cfg_file)
		os.rename(fn, self.cfg_file)
		# Success
		return OK
	def EditLine(self, loc : Loc, upt : str):
		"""Replaces old contents by new contents, preserving existing comments"""
		old : Line = self.raw_lines[loc.idx_0]
		valn = len(old.unc)
		rem = (valn >= 0) and (len(old.raw) > valn) and old.raw[valn:] or ""
		l = upt + rem
		if not l.endswith('\n'):
			l += '\n'
		self.raw_lines[loc.idx_0] = Line(l)
	def AddLines(self, loc : Loc, lines : list[str]) -> None:
		"""Lines have to be complete including LF"""
		# Locate neutral position
		ins = loc.idx_n or loc.idx_0
		if ins > 0:
			ins -= 1
			blank = False
			# Search for non-empty
			while ins > loc.idx_0:
				if self.raw_lines[ins].raw.strip():
					break
				ins -= 1
				blank = True
			ins += (1 + blank)
		else:
			ins = 0
		# Now insert lines
		for l in lines:
			self.raw_lines.insert(ins, Line(l))
			ins += 1
	def AddSectionLines(self, loc : Loc, lines : list[str]) -> None:
		ins = loc.idx_n or loc.idx_0
		if ins is None:
			ins = 0
		if not self.raw_lines[ins].IsLineEmpty():
			self.raw_lines.insert(ins, Line("\n"))
			self.raw_lines.insert(ins, Line("\n"))
		loc = Loc(ins + 1)
		self.AddLines(loc, lines)
	def DeleteRange(self, loc : Loc) -> None:
		"""Delete a range of lines"""
		if loc.idx_n is None:
			del self.raw_lines[loc.idx_0]
		else:
			del self.raw_lines[loc.idx_0:loc.idx_n]
	def DeleteRangeWithComments(self, loc : Loc) -> int:
		"""Similar to `DeleteRange()`, but includes prepending comment lines"""
		i_0 = loc.idx_0
		i_n = loc.idx_n or (i_0+1)
		while True:
			i_0 -= 1
			if i_0 < 0:
				break
			l = self.raw_lines[i_0].raw.strip()
			if not l:
				break
			if l[0] not in "#;":
				break
		i_0 += 1
		del self.raw_lines[i_0:i_n]
		return i_0
	def OvrSectionLines(self, loc : Loc, lines : list[str]) -> None:
		loc = Loc(self.DeleteRangeWithComments(loc))
		self.AddSectionLines(loc, lines)
	def IsLastFileArg(self, val : str):
		if len(self.args) or (not isinstance(val, str)):
			return False
		return val and os.path.exists(val)

class SecLabel(object):
	def __init__(self, label : str):
		self.labels = []
		if label:
			# Convert label into a list, splitting it on whitespaces
			# Because every `gcode_macro` is converted to uppercase in Klipper, we repeat this also
			for k in label.split():
				self.labels.append((self.labels and (self.labels[0] == "gcode_macro")) and k.strip().upper() or k.strip())
	def __bool__(self):
		return bool(self.labels)
	def __str__(self):
		return ' '.join(self.labels)
	def __repr__(self):
		return '[' + ' '.join(self.labels) + ']'
	def MatchesAll(self):
		# The '*' wildcard matches all patterns
		return self.labels and self.labels[0] == '*'
	def Match(self, pattern : 'SecLabel') -> bool:
		"""Allows you to search sections using file names wildcards"""
		# Matches all pattern?
		if pattern.MatchesAll():
			return True
		# Different token counts, is inherently different
		if len(self.labels) != len(pattern.labels):
			return False
		# Now compare token by token
		for i, s in enumerate(self.labels):
			if i:
				# no case sensitivity for tokens at the right side
				s = s.upper()
				m = pattern.labels[i].upper()
			else:
				# get match pattern
				m = pattern.labels[i]
			# Use file name match class as filter
			if not fnmatch.fnmatch(s, m):
				# Stop if anything is different
				return False
		# Success
		return True
	def IsInclude(self):
		return self.labels and (self.labels[0] == 'include')

def StringEssence(s : str) -> bytes:
	"""Reduces a string having identifiers and values to its essence. This normalizes strings with minor changes."""
	res = ""
	is_token = False
	try:
		# Takes first char to begin
		it = iter(s)
		ch = next(it)
		# Loop until end of string
		while True:
			# scan identifiers
			if ch.isalpha() or (ch == '_'):
				# Identifier following a generic token needs a space separator
				if is_token:
					res += ' '
				# Identifier is also a token
				is_token = True
				# Save first char of the identifier
				res += ch
				# Now collect the complete identifier
				ch = next(it)
				while ch.isalnum() or (ch == '_'):
					res += ch
					ch = next(it)
				# evaluation of current char continues on the next iteration
			elif ch.isnumeric():
				# Values following a generic token needs a space separator
				if is_token:
					res += ' '
				# A values is also a token
				is_token = True
				# Save first char of the value
				res += ch
				# Now collect the complete value
				ch = next(it)
				while ch.isnumeric() or (ch == '.'):
					res += ch
					ch = next(it)
				# evaluation of current char continues on the next iteration
			elif ch.isspace():
				# Any space alike (TAB, LF, CR...) is converted to space
				res += ' '
				# Non token element
				is_token = False
				# Ignore all following spaces
				ch = next(it)
				while ch.isspace():
					ch = next(it)
				# evaluation of current char continues on the next iteration
			else:
				# everything else is separator, etc
				is_token = False
				res += ch
				# continue on the next iteration
				ch = next(it)
	except StopIteration:
		pass
	# no trailing spaces
	return res.rstrip().encode()

def StringCRC(s : str, seed : int) -> int:
	"""Computes CRC of a string normalizing it with the `StringEssence` method"""
	return zlib.crc32(StringEssence(s), seed)

class MLine(object):
	"""Store the valuable part of a line"""
	def __init__(self, line : str, lno : int):
		self.line = line
		# The valuable part has the size of the string, assuming that every other 
		# line content is part of a comment, if any
		self.loc = Loc(lno)
		self.is_empty = not line.strip()
	def GetLoc(self):
		"""Return the position in the file"""
		return (self.idx,None)
	def GetEssence(self) -> bytes:
		return StringEssence(self.line)
	def GetCRC(self, seed : int) -> int:
		return StringCRC(self.line, seed)

class Key(object):
	"""Sections are composed of keys. Keys can have a single line of a multiple lines"""
	def __init__(self, label : str, lno : int, value):
		# Key name is given on construction
		self.name = label.strip()
		# And the valuable part line part
		self.loc = Loc(lno, lno)
		self.value = value.strip()
		# Multi lines entries don't have an argument on the same line, so convert
		if not self.value:
			self.value = []
	def __str__(self):
		return f"{self.name}:{str(self.value)}"
	def IsMultiLine(self):
		"""Indicates we are storing multiple lines"""
		return isinstance(self.value, list)
	def GetLoc(self):
		"""Returns the location"""
		if self.IsMultiLine():
			return self.loc
		else:
			return Loc(self.loc.idx_0)
	def GetMultiLineValue(self) -> list[str]:
		"""Returns the set of lines as list[str]"""
		ret = []
		for i in self.value:
			i : MLine
			ret.append(i.line)
		return ret
	def GetCRC():
		"""Evaluate contents and produces a CRC for it."""
		pass
	def GetCRC(self) -> int:
		seed = StringCRC(self.name + ':', 0)
		if self.IsMultiLine():
			for ml in self.value:
				ml : MLine
				seed = ml.GetCRC(seed)
		else:
			seed = StringCRC(self.value, seed)
		return seed

class Section(object):
	"""Sections are groups of keys"""
	def __init__(self, label : SecLabel, lno : int):
		self.name : SecLabel = isinstance(label, str) and SecLabel(label) or label
		self.loc = Loc(lno, lno)
		self.keys : list[Key] = []
	def GetLoc(self) -> Loc:
		"""Returns the location inside the list of lines"""
		return self.loc
	def GetLabel(self) -> str:
		"""Well formatted label, without brackets"""
		return str(self.name)
	def GetKey(self, k : str) -> list[Key]:
		"""
		Returns the key with the given name. Although not directly allowed, multiple 
		results is possible on a malformed configuration file.
		"""
		return [i for i in self.keys if i.name == k]
	def GetSingleKey(self, k : str) -> Res:
		"""Makes sure that only a single key is selected."""
		key = self.GetKey(k)
		if not key:
			return NO_KEY(self.GetLoc())
		if len(key) > 1:
			return MULT_KEY(self.GetLoc())
		key : Key = key[0]
		return Res('k', key, key.GetLoc())
	def GetCRC(self):
		"""Compute CRC of contents using `StringEssence()` method"""
		# Use label to start byte-stream
		ba = StringEssence(str(self.name))
		# Accumulate each CRC value into stream
		for k in self.keys:
			# CRC of lines
			crc = k.GetCRC()
			ba += (crc & 0xFFFFFFFF).to_bytes(4, byteorder='little')
		# Now that stream is ready, compute CRC
		return zlib.crc32(ba)

class CfgIterator(object):
	"""Allows to iterate over the configuration lines for contents detection"""
	def __init__(self, lines : list[Line], callback : Callable[[int], None] = None):
		self.it = iter(lines)
		self.callback = callback
		self.lno = -1
		self.rl : Line = None
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
		return self.rl.IsLineEmpty()
	def MatchesSection(self) -> bool:
		"""Returns true if a section start is found. This should close any multiline key or previous section"""
		return bool(self.m)
	def GetSectionLabel(self) -> str:
		"""The label of the detected section, in the case `MatchesSection` is true"""
		return bool(self.m) and self.m.group(1) or None
	def HasLeadingBlanks(self):
		"""True if line has contents but starts with a leading space (multi-line values)"""
		return self.rl.HasLeadingBlanks()
	def HasKeyPattern(self):
		"""Does this line looks like a section key?"""
		return (not self.m) and self.rl.HasKeyPattern()
	def CreateSection(self) -> Section:
		"""Create a Section instance, assuming that 'MatchesSection()' is true. At exit it moves to the next line"""
		s = Section(self.GetSectionLabel(), self.lno)
		return s
	def CreateKey(self) -> Key:
		"""Create a Section instance, assuming that 'HasKeyPattern()' is true"""
		k, v = self.rl.unc.split(':', 1)
		key = Key(k, self.lno, v)
		return key
	
class Contents(object):
	"""Store the entire contents of the configuration file"""
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
	def GetSingleSection(self, pat :SecLabel) -> Res:
		"""Makes sure that a single section matches the input pattern"""
		sec = self.MatchSections(pat)
		if not sec:
			return NO_SECTION
		if len(sec) > 1:
			return MULT_SECTION
		return Res('s', sec[0])
	def GetSectionOfLine(self, lno : int) -> Res:
		"""Searches the section that is on the given line number"""
		rng = Loc(lno)
		if not self.ctx.IsRangeValid(rng):
			return INV_RANGE(rng)
		for s in self.sections:
			if s.GetLoc().IsInRange(lno):
				return Res('s', s)
		return NO_SECTION
	def GetFirstSection(self) -> Section:
		for s in self.sections:
			if not s.name.IsInclude():
				return s
		return None
	def AddSectionLines(self, loc : Loc, data : list[str]) -> None:
		if self.save.idx_0 <= loc.idx_0:
			loc = Loc(self.save.idx_0 - 1)
		self.ctx.AddSectionLines(loc, data)


def ListSec(ctx : Context) -> Res:
	"""
	High level command to list keys:
		- arg0: section or pattern
		- arg1: configuration file name (optional)
	"""
	# Get section
	sec = ctx.GetArg()
	if sec and not ctx.IsLastFileArg(sec):
		sec = SecLabel(sec)
		# Load configuration file
		res = ctx.ReadLines()
		if not res:
			return res
		# Load contents
		c = Contents(ctx)
		c.Load()
		# Filter results
		hits = c.MatchSections(sec)
		if len(hits) > 1:
			# Handle multi-line responses
			res = "".join([f"{s.GetLabel()} @{s.GetLoc().idx_0} :{s.GetCRC():08X}\n" for s in hits])
			return Res('*', EncodeMultiLine(res), NO_LOC)
		elif len(hits) == 1:
			# Handle single line responses
			s = hits[0]
			return Res('=', f"{s.GetLabel()} @{s.GetLoc().idx_0} :{s.GetCRC():08X}\n", s.GetLoc())
		return NO_SECTION
	return MISSING_ARG

def ListKeys(ctx : Context) -> Res:
	"""
	High level command to return the list of keys, line numbers and CRC of a given section.
		- arg0: section name or line number. For line number use `@nnn` format
		- arg1: configuration file name (optional)
	"""
	# Get section
	sec = ctx.GetArg()
	if sec and not ctx.IsLastFileArg(sec):
		# Load configuration file
		res = ctx.ReadLines()
		if not res:
			return res
		# Load contents
		c = Contents(ctx)
		c.Load()
		# Section by number?
		if sec.startswith('@'):
			res = c.GetSectionOfLine(int(sec[1:]))
		else:
			# Search for section
			res = c.GetSingleSection(SecLabel(sec))
		# Object was found?
		if res.IsObject():
			s : Section = res.value
			if ctx.IsRangeValid(s.GetLoc()):
				if len(s.keys) == 0:
					res = NO_KEY(s.GetLoc())
				elif len(s.keys) == 1:
					k = s.keys[0]
					res = Res('=', f"{k.name} @{k.GetLoc().idx_0} :{k.GetCRC():08X}", k.GetLoc())
				else:
					t = "".join(f"{k.name} @{k.GetLoc().idx_0} :{k.GetCRC():08X}\n" for k in s.keys)
					res = Res('*', EncodeMultiLine(t), NO_LOC)
			else:
				res = INV_RANGE(s.GetLoc())	# bug?
		return res
	return MISSING_ARG
	
def GetKey(ctx : Context) -> Res:
	"""
	High level command to return the value of a key:
		- arg0: section
		- arg1: key
		- arg2: configuration file name (optional)
	The value is returned either as simple string or base64 for multi-line keys
	"""
	# Get section
	sec = ctx.GetArg()
	if sec and not ctx.IsLastFileArg(sec):
		sec = SecLabel(sec)
		# Get key
		k = ctx.GetArg()
		if k and not ctx.IsLastFileArg(k):
			# Load configuration file
			res = ctx.ReadLines()
			if not res:
				return res
			# Load contents
			c = Contents(ctx)
			c.Load()
			# Search for section
			res = c.GetSingleSection(sec)
			if res.code != 's':
				return res
			sec : Section = res.value
			if ctx.IsRangeValid(sec.GetLoc()):
				# Search for key
				res = sec.GetSingleKey(k)
				if res.IsObject():
					key : Key = res.value
					if key.IsMultiLine():
						# Encode multiline response
						res.code = '*'
						res.value = EncodeMultiLine(key.value)
					else:
						# Simple response for single line
						res.code = '='
						res.value = key.value
			else:
				res = INV_RANGE(sec.GetLoc())	# bug?
			return res
	return MISSING_ARG

def EditKey(ctx : Context) -> Res:
	"""
	High level command to edit a simple line key:
		- arg0: section
		- arg1: key
		- arg2: New value
		- arg3: configuration file name (optional)
	This command also adds a new key value if it does not exists.
	"""
	# Get section
	sec = ctx.GetArg()
	if sec and not ctx.IsLastFileArg(sec):
		sec = SecLabel(sec)
		# Get key
		k = ctx.GetArg()
		if k and not ctx.IsLastFileArg(k):
			# Data to be updated
			data = ctx.GetArg()
			if data and not ctx.IsLastFileArg(data):
				# Load configuration file
				res = ctx.ReadLines()
				if not res:
					return res
				# Load contents
				c = Contents(ctx)
				c.Load()
				# Search for section
				res = c.GetSingleSection(sec)
				if res.code != 's':
					return res
				sec : Section = res.value
				if ctx.IsRangeValid(sec.GetLoc()):
					# Search for key
					res = sec.GetSingleKey(k)
					# Found a key?
					if res.IsKindOf(NO_KEY(NO_LOC)):
						# Append entry
						ctx.AddLines(sec.GetLoc(), [f"{k}:{data}\n"])
						# Writes results
						res = ctx.WriteLines()
					elif res.IsObject():
						# Modify existing line
						key : Key = res.value
						if key.IsMultiLine():
							return ML_KEY(key.GetLoc())
						if key.value == data:
							return OK
						# This method preserves comments
						ctx.EditLine(key.GetLoc(), f"{k}:{data}")
						# Writes results
						res = ctx.WriteLines()
				else:
					res = INV_RANGE(sec.GetLoc())	# bug?
				return res
	return MISSING_ARG

def EditKeyML(ctx : Context) -> Res:
	"""
	High level command to edit a multiline key:
		- arg0: section
		- arg1: key
		- arg2: base64 encoded and encrypted data (use `EncodeMultiLine`)
		- arg3: configuration file name (optional)
	This command also adds a new key value if it does not exists.
	"""
	# Get section
	sec = ctx.GetArg()
	if sec and not ctx.IsLastFileArg(sec):
		sec = SecLabel(sec)
		# Get key
		k = ctx.GetArg()
		if k and not ctx.IsLastFileArg(k):
			# Data to be updated
			data = ctx.GetArg()
			if data and not ctx.IsLastFileArg(data):
				try:
					data = DecodeMultiLine(data)
				except:
					return INV_ENC
				# Load configuration file
				res = ctx.ReadLines()
				if not res:
					return res
				# Load contents
				c = Contents(ctx)
				c.Load()
				# Search for section
				res = c.GetSingleSection(sec)
				if res.code != 's':
					return res
				sec : Section = res.value
				if ctx.IsRangeValid(sec.GetLoc()):
					# Search for key
					res = sec.GetSingleKey(k)
					# Found a key?
					if res.IsObject():
						# Modify existing line
						key : Key = res.value
						if not key.IsMultiLine():
							return ML_KEY(key.GetLoc())
						if key.value == data:
							return OK
						# Use section location
						loc = key.GetLoc()
						# But keep the key line
						loc.idx_0 += 1
						# Remove old contents
						ctx.DeleteRange(loc)
						# Insert new data
						loc.idx_n = loc.idx_0
						ctx.AddLines(loc, data)
						# Writes results
						res = ctx.WriteLines()
					elif res.IsKindOf(NO_KEY(NO_LOC)):
						# Append entry
						data.insert(0, f"{k}:\n")
						ctx.AddLines(sec.GetLoc(), data)
						# Writes results
						res = ctx.WriteLines()
				else:
					res = INV_RANGE(sec.GetLoc())	# bug?
				return res
	return MISSING_ARG

def DelKey(ctx : Context) -> Res:
	"""
	High level command to delete a key:
		- arg0: section
		- arg1: key
		- arg2: configuration file name (optional)
	"""
	# Get section
	sec = ctx.GetArg()
	if sec and not ctx.IsLastFileArg(sec):
		sec = SecLabel(sec)
		# Get key
		k = ctx.GetArg()
		if k and not ctx.IsLastFileArg(k):
			# Load configuration file
			res = ctx.ReadLines()
			if not res:
				return res
			# Load contents
			c = Contents(ctx)
			c.Load()
			# Search for section
			res = c.GetSingleSection(sec)
			if res.code != 's':
				return res
			sec : Section = res.value
			if ctx.IsRangeValid(sec.GetLoc()):
				# Search for key
				res = sec.GetSingleKey(k)
				# Found a key?
				if res.IsObject():
					# Modify existing line
					key : Key = res.value
					ctx.DeleteRange(key.GetLoc())
					res = ctx.WriteLines()
			else:
				res = INV_RANGE(sec.GetLoc())	# bug?
			return res
	return MISSING_ARG

def RenSec(ctx : Context) -> Res:
	"""
	High level command to rename a section:
		- arg0: old section name
		- arg1: new section name
		- arg2: configuration file name (optional)
	"""
	# Get old section name
	old = ctx.GetArg()
	if old and not ctx.IsLastFileArg(old):
		old = SecLabel(old)
		# Get new section name
		sec = ctx.GetArg()
		if sec and not ctx.IsLastFileArg(sec):
			sec = SecLabel(sec)
			# Load configuration file
			res = ctx.ReadLines()
			if not res:
				return res
			# Load contents
			c = Contents(ctx)
			c.Load()
			# locate section
			res = c.GetSingleSection(old)
			if res.IsObject():
				s : Section = res.value
				if ctx.IsRangeValid(s.GetLoc()):
					ctx.EditLine(s.GetLoc(), f"[{sec}]")
					res = ctx.WriteLines()
				else:
					res = INV_RANGE(s.GetLoc())	# bug?
			return res
	return MISSING_ARG

def DelSec(ctx : Context) -> Res:
	"""
	High level command to delete a section:
		- arg0: section name or line number. For line number use `@nnn` format
		- arg1: configuration file name (optional)
	"""
	# Get section or number
	sec = ctx.GetArg()
	if sec and not ctx.IsLastFileArg(sec):
		# Load configuration file
		res = ctx.ReadLines()
		if not res:
			return res
		# Load contents
		c = Contents(ctx)
		c.Load()
		if sec.startswith('@'):
			# Locate section by line number
			res = c.GetSectionOfLine(int(sec[1:]))
		else:
			# locate section
			res = c.GetSingleSection(SecLabel(sec))
		# Object was found?
		if res.IsObject():
			s : Section = res.value
			if ctx.IsRangeValid(s.GetLoc()):
				# Remove section, including preceding comment lines
				ctx.DeleteRangeWithComments(s.GetLoc())
				# Write buffer
				res = ctx.WriteLines()
			else:
				res = INV_RANGE(s.GetLoc())	# bug?
		return res
	return MISSING_ARG

def ReadSec(ctx : Context) -> Res:
	"""
	This high level method reads all lines of a section, including its header line 
	and comments. 
		- arg0: section name or line number. For line number use `@nnn` format
		- arg1: configuration file name (optional)
	"""
	# Get section or number
	sec = ctx.GetArg()
	if sec and not ctx.IsLastFileArg(sec):
		# Load configuration file
		res = ctx.ReadLines()
		if not res:
			return res
		# Load contents
		c = Contents(ctx)
		c.Load()
		if sec.startswith('@'):
			# Locate section by line number
			res = c.GetSectionOfLine(int(sec[1:]))
		else:
			# locate section
			res = c.GetSingleSection(SecLabel(sec))
		if res.IsObject():
			s : Section = res.value
			if ctx.IsRangeValid(s.GetLoc()):
				lines = ctx.GetLines(s.GetLoc())
				if not lines:
					res = EMPTY
				elif len(lines) == 0:
					res = Res('=', lines[0], s.GetLoc())
				else:
					res = Res('*', EncodeMultiLine(lines), s.GetLoc())
			else:
				res = INV_RANGE(s.GetLoc())	# bug?
		return res
	return MISSING_ARG

def AddSec(ctx : Context) -> Res:
	"""
	This high level method adds an entire section after the position of the given section.
		- arg0: indicates location where new section has to be added. It can be:
			- A section name.
			- A line number that indicates the section. For line number use `@nnn` format.
			- `@top` to insert before the first section.
			- `@bottom` to insert after the last section but before the persistence block
		- arg1: base64 encoded data (use `EncodeMultiLine`)
		- arg1: configuration file name (optional)
	"""
	# Get section or number
	sec = ctx.GetArg()
	if sec and not ctx.IsLastFileArg(sec):
		# Get base64 data
		data = ctx.GetArg()
		if data and not ctx.IsLastFileArg(data):
			# Load configuration file
			res = ctx.ReadLines()
			if not res:
				return res
			try:
				data = DecodeMultiLine(data)
			except:
				return INV_ENC
			# Load contents
			c = Contents(ctx)
			c.Load()
			loc : Loc = None
			if sec.startswith('@top'):
				s = c.GetFirstSection()
				if s:
					loc = Loc(s.GetLoc().idx_0)
					if loc.idx_0 > 0:
						loc.idx_0 -= 1
				res = OK
			elif sec.startswith('@bottom'):
				res = OK
				if c.sections:
					res = Res('s', c.sections[-1], c.sections[-1].GetLoc())
			elif sec.startswith('@'):
				# Locate section by line number
				res = c.GetSectionOfLine(int(sec[1:]))
			else:
				# locate section
				res = c.GetSingleSection(SecLabel(sec))
			# Get location
			if loc:
				pass
			elif res.IsOk():
				loc = Loc(c.save.idx_0)
			if res.IsObject():
				# Objects results are of Section type
				s : Section = res.value
				# Insert at the bottom
				loc = Loc(s.GetLoc().idx_n)
			# Execute only if no errors found
			if not res.IsError():
				c.AddSectionLines(loc, data)
				res = ctx.WriteLines()
			return res
	return MISSING_ARG

def OvrSec(ctx : Context) -> Res:
	"""
	This high level method replaces an entire section, including its header line, 
	with the given base64 encoded contents. The content of the base64 is not validated
	and written as is.
		- arg0: section name or line number. For line number use `@nnn` format
		- arg1: base64 encoded data (use `EncodeMultiLine`)
		- arg1: configuration file name (optional)
	"""
	# Get section or number
	sec = ctx.GetArg()
	if sec and not ctx.IsLastFileArg(sec):
		# Get base64 data
		data = ctx.GetArg()
		if data and not ctx.IsLastFileArg(data):
			# Load configuration file
			res = ctx.ReadLines()
			if not res:
				return res
			try:
				data = DecodeMultiLine(data)
			except:
				return INV_ENC
			# Load contents
			c = Contents(ctx)
			c.Load()
			if sec.startswith('@'):
				# Locate section by line number
				res = c.GetSectionOfLine(int(sec[1:]))
			else:
				# locate section
				res = c.GetSingleSection(SecLabel(sec))
			# Execute only if no errors found
			if res.IsObject():
				s : Section = res.value
				ctx.OvrSectionLines(s.GetLoc(), data)
				res = ctx.WriteLines()
			return res
	return MISSING_ARG

def main(args : list[str]) -> Res:
	ctx = Context(args)
	res = NO_FN
	try:
		fn = ctx.GetArg()
		if fn:
			if hasattr(MODULE, fn):
				res = getattr(MODULE, fn)(ctx)
	except Exception as e:
		res = Res('!', "XCP: " + str(e))
	return res

if __name__ == "__main__":
	print(main(sys.argv[1:]))
