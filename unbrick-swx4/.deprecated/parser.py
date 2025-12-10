#
# -*- coding: UTF-8 -*-
#
# Spellchecker:	words MULT valn klipper


import os
import re
from typing import Callable, Optional

from .loc import Loc
from .result import Result, EXTRA_ARGS, NO_FILE, OK, NO_READ, EMPTY
from .line import Line
from .sections import Section, SecLabel
from .keys import Key


DF = r"/home/mks/klipper_config/printer.cfg"


class CfgIterator(object):
	"""Allows to iterate over the configuration lines for contents detection"""
	def __init__(self, lines : list[Line], callback : Optional[Callable[[int], None]] = None):
		self.it = iter(lines)
		self.callback = callback
		self.lno = -1
		self.rl : Line
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
		tmp = self.GetSectionLabel()
		if tmp is None:
			raise ValueError("Unexpected return value for 'CfgIterator.GetSectionLabel'")
		s = Section(SecLabel(tmp), self.lno)
		return s
	def CreateKey(self) -> Key:
		"""Create a Section instance, assuming that 'HasKeyPattern()' is true"""
		if self.rl is None:
			raise ValueError("Unexpected type for 'self.rl'")
		if '=' in self.rl.unc:
			k, v = self.rl.unc.split('=', 1)
		else:
			k, v = self.rl.unc.split(':', 1)
		key = Key(k, self.lno, v)
		return key


class Context(object):
	""" Stores the context of the operation: file name, all lines and command line arguments """
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
		return ""
	def ReadLines(self) -> Result:
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
	def WriteLines(self) -> Result:
		"""Write the buffered lines into a temporary file, then replaces old instance"""
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
		# Handle unexpected case
		if loc.idx_0 is None:
			raise ValueError("Unexpected type for 'loc'")
		old : Line = self.raw_lines[loc.idx_0]
		valn = len(old.unc)
		rem = (valn >= 0) and (len(old.raw) > valn) and old.raw[valn:] or ""
		l = upt + rem
		if not l.endswith('\n'):
			l += '\n'
		self.raw_lines[loc.idx_0] = Line(l)
	def AddLines(self, loc : Loc, lines : list[str]) -> None:
		"""Lines have to be complete including LF"""
		# Handle unexpected case
		if loc.idx_0 is None:
			raise ValueError("Unexpected type for 'loc'")
		# Locate neutral position
		ins = loc.idx_n or loc.idx_0
		if ins > 0:
			# Append to tail?
			if ins < len(self.raw_lines):
				ins -= 1
				# Search for non-empty
				while ins > loc.idx_0:
					if self.raw_lines[ins].raw.strip():
						break
					ins -= 1
				ins += 1
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
		# Handle unexpected case
		if loc.idx_0 is None:
			raise ValueError("Unexpected type for 'loc'")
		if loc.idx_n is None:
			del self.raw_lines[loc.idx_0]
		else:
			del self.raw_lines[loc.idx_0:loc.idx_n]
	def DeleteRangeWithComments(self, loc : Loc) -> int:
		"""Similar to `DeleteRange()`, but includes prepending comment lines"""
		# Handle unexpected case
		if loc.idx_0 is None:
			raise ValueError("Unexpected type for 'loc'")
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

