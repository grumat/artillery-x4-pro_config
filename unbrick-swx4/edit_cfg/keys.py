#
# -*- coding: UTF-8 -*-
#
# Spellchecker:	words libtools


from typing import TypeGuard

from .loc import Loc
from .line import MLine
from .libtools import StringCRC


class Key(object):
	""" Sections are composed of keys. Keys can have a single line of a multiple lines """
	def __init__(self, label : str, lno : int, value : str):
		# Key name is given on construction
		self.name = label.strip()
		# And the valuable part line part
		self.loc = Loc(lno, lno)
		self.value : str | list[MLine] = value.strip()
		# Multi lines entries don't have an argument on the same line, so convert
		if not self.value:
			self.value = []
	def __str__(self):
		return f"{self.name}:{str(self.value)}"
	def IsMultiLine(self) -> TypeGuard[list[MLine]]: # type: ignore
		"""Indicates we are storing multiple lines"""
		return isinstance(self.value, list)
	def GetLoc(self):
		"""Returns the location"""
		if isinstance(self.value, list):
			return self.loc
		else:
			return Loc(self.loc.idx_0)
	def GetMultiLineValue(self) -> list[str]:
		"""Returns the set of lines as list[str]"""
		ret = []
		if isinstance(self.value, list):
			for i in self.value:
				i : MLine
				ret.append(i.line)
		return ret
	def GetCRC(self) -> int:
		"""Evaluate contents and produces a CRC for it."""
		seed = StringCRC(self.name + ':', 0)
		if isinstance(self.value, list):
			for ml in self.value:
				ml : MLine
				seed = ml.GetCRC(seed)
		else:
			seed = StringCRC(self.value, seed)
		return seed

