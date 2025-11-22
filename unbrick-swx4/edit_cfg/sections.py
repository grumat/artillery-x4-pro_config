#
# -*- coding: UTF-8 -*-
#
# Spellchecker:	words MULT libtools

import fnmatch
import zlib

from .loc import Loc
from .keys import Key
from .result import Result, NO_KEY, MULT_KEY
from .libtools import StringEssence


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
	def Match(self, pattern : SecLabel) -> bool:
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
	def GetSingleKey(self, k : str) -> Result:
		"""Makes sure that only a single key is selected."""
		key_list = self.GetKey(k)
		if not key_list:
			return NO_KEY(self.GetLoc())
		if len(key_list) > 1:
			return MULT_KEY(self.GetLoc())
		key : Key = key_list[0]
		return Result('k', key, key.GetLoc())
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

