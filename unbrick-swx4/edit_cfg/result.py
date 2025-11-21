#
# -*- coding: UTF-8 -*-
#
# spellchecker:words MULT

from .loc import Loc, NO_LOC

class Result(object):
	def __init__(self, c : str, val : str | object, loc : Loc = NO_LOC):
		self.code : str = c
		self.value : str | object = val
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
	def IsKindOf(self, o : Result) -> bool:
		return (self.code == o.code) and (type(self.value) == type(o.value) and (self.value == o.value))

# General success result
OK = Result('.', "OK")
# Error returned when an argument is missing
NO_FN = Result('!', "FN")
# Error returned when an argument is missing
MISSING_ARG = Result('!', "ARG")
# Error returned when too many arguments are given
EXTRA_ARGS = Result('!', "ARG+")
# Data encoding invalid (Base64)
INV_ENC = Result('!', "ENC")
# Specified file does not exists
NO_FILE = Result('!', "FILE")
# You shall load the configuration file before writing
NO_READ = Result('!', "READ")
# No lines to be written (usually invalid call sequence or file)
EMPTY = Result('!', "EMPTY")
# Indicates that a multi-line key was found for an operation that can only handle single lines
ML_KEY = lambda loc : Result('!', "ML", loc)
# File has an invalid format (not a single section was found)
INV_FMT = Result('!', "FMT")
# The requested section was not found
NO_SECTION = Result('!', "SEC")
# More than one section matches your request
MULT_SECTION = Result('!', "SEC+")
# Error returned when a key was not found inside a section
NO_KEY = lambda loc : Result('!', "KEY", loc)
# More than one key matches your request (section has duplicates)
MULT_KEY = lambda loc : Result('!', "KEY+", loc)
# Invalid range (usually indicates an internal bug)
INV_RANGE = lambda loc : Result('!', "RANGE", loc)
