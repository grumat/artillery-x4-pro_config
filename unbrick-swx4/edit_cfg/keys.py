#
# -*- coding: UTF-8 -*-
#
# Spellchecker:	words libtools


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
		self.value = [MLine(value.strip(), lno)]
		# Multi lines entries don't have an argument on the same line, so convert
		if not self.value:
			self.value = []
	def __str__(self):
		return f"{self.name}:{str(self.value)}"
	def __repr__(self):
		return f"Key({self.name}:{str(self.value)})"
	def ShrinkIfEmpty(self):
		"""Remove unnecessary lines of the key"""
		# Remove every empty tail line, as long as a single entry exists
		while len(self.value) > 1:
			if self.value[-1].is_empty and (self.value[-1].is_comment == False):
				del self.value[-1]
			else:
				break
		# Fix the line range
		if len(self.value):
			last = self.value[-1]
			if last.loc.idx_0 is None:
				raise ValueError("Invalid Location value")
			if last.loc.idx_n is None:
				self.loc.idx_n = last.loc.idx_0 + 1
			else:
				self.loc.idx_n = last.loc.idx_n
	def GetLoc(self):
		"""Returns the location"""
		if isinstance(self.value, list):
			return self.loc
		else:
			return Loc(self.loc.idx_0)
	def IsMultiLine(self):
		"""Return true if value occupies multiple line"""
		return len(self.value) > 1
	def GetSingleLineValue(self) -> str:
		"""Returns the s single line value"""
		if len(self.value) > 1:
			raise RuntimeError("Method cannot be used for an object with multiline value")
		return len(self.value) == 1 and self.value[0].line or ''
	def GetMultiLineValue(self) -> list[str]:
		"""Returns the set of lines as list[str]"""
		if len(self.value) <= 1:
			raise RuntimeError("Method cannot be used for an object with multiline value")
		return [ml.line for ml in self.value]
	def GetCRC(self) -> int:
		"""Evaluate contents and produces a CRC for it."""
		seed = StringCRC(self.name + ':', 0)
		if self.IsMultiLine():
			for ml in self.value:
				ml : MLine
				seed = ml.GetCRC(seed)
		else:
			seed = StringCRC(self.GetSingleLineValue(), seed)
		return seed

