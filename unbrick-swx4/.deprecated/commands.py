#
# -*- coding: UTF-8 -*-
#
# Spellchecker: words libtools MULT


from .parser import Context
from .sections import SecLabel, Section
from .result import Result, NO_LOC, MISSING_ARG, NO_SECTION, NO_KEY, INV_RANGE, ML_KEY, OK, INV_ENC, EMPTY, NO_FN
from .libtools import EncodeMultiLine, DecodeMultiLine
from .contents import Contents
from .keys import Key
from .loc import Loc


def ListSec(ctx : Context) -> Result:
	"""
	High level command to list keys:
		- arg0: section or pattern
		- arg1: configuration file name (optional)
	Returns:
		- MISSING_ARG : when command line parameters are missing
		- NO_SECTION: Section was not found
		- EXTRA_ARGS: If too many arguments were given
		- NO_FILE: If file was not found
		- String for single line responses
		- Encoding for multi line responses
	"""
	# Get section
	arg = ctx.GetArg()
	if arg and not ctx.IsLastFileArg(arg):
		arg = SecLabel(arg)
		# Load configuration file
		res = ctx.ReadLines()
		if not res:
			return res
		# Load contents
		c = Contents(ctx)
		c.Load()
		# Filter results
		hits = c.MatchSections(arg)
		if len(hits) > 1:
			# Handle multi-line responses
			res = "".join([f"{s.GetLabel()} @{s.GetLoc().idx_0} :{s.GetCRC():08X}\n" for s in hits])
			return Result('*', EncodeMultiLine(res), NO_LOC)
		elif len(hits) == 1:
			# Handle single line responses
			s = hits[0]
			return Result('=', f"{s.GetLabel()} @{s.GetLoc().idx_0} :{s.GetCRC():08X}\n", s.GetLoc())
		return NO_SECTION
	return MISSING_ARG


def ListKeys(ctx : Context) -> Result:
	"""
	High level command to return the list of keys, line numbers and CRC of a given section.
		- arg0: section name or line number. For line number use `@nnn` format
		- arg1: configuration file name (optional)
	Returns:
		- MISSING_ARG : when command line parameters are missing
		- NO_SECTION: Section was not found
		- EXTRA_ARGS: If too many arguments were given
		- NO_FILE: If file was not found
		- INV_RANGE: The given line value is out of range
		- String for single line responses
		- Encoding for multi line responses
	"""
	# Get section
	arg = ctx.GetArg()
	if arg and not ctx.IsLastFileArg(arg):
		# Load configuration file
		res = ctx.ReadLines()
		if not res:
			return res
		# Load contents
		c = Contents(ctx)
		c.Load()
		# Section by number?
		if arg.startswith('@'):
			res = c.GetSectionOfLine(int(arg[1:]))
		else:
			# Search for section
			res = c.GetSingleSection(SecLabel(arg))
		# Object was found?
		if res.IsObject():
			if not isinstance(res.value, Section):
				raise ValueError("Unexpected object type in 'result'")
			sec = res.value
			if ctx.IsRangeValid(sec.GetLoc()):
				if len(sec.keys) == 0:
					res = NO_KEY(sec.GetLoc())
				elif len(sec.keys) == 1:
					k = sec.keys[0]
					res = Result('=', f"{k.name} @{k.GetLoc().idx_0} :{k.GetCRC():08X}", k.GetLoc())
				else:
					t = "".join(f"{k.name} @{k.GetLoc().idx_0} :{k.GetCRC():08X}\n" for k in sec.keys)
					res = Result('*', EncodeMultiLine(t), NO_LOC)
			else:
				res = INV_RANGE(sec.GetLoc())	# bug?
		return res
	return MISSING_ARG


def ListKey(ctx : Context) -> Result:
	"""
	High level command to return the list of keys, line numbers and CRC of a given section.
		- arg0: section name or line number. For line number use `@nnn` format
		- arg1: key name
		- arg2: configuration file name (optional)
	Returns:
		- MISSING_ARG : when command line parameters are missing
		- NO_SECTION: Section was not found
		- EXTRA_ARGS: If too many arguments were given
		- NO_FILE: If file was not found
		- INV_RANGE: The given line value is out of range
		- String for single line responses
		- Encoding for multi line responses
	"""
	# Get section
	arg = ctx.GetArg()
	if arg and not ctx.IsLastFileArg(arg):
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
			# Section by number?
			if arg.startswith('@'):
				res = c.GetSectionOfLine(int(arg[1:]))
			else:
				# Search for section
				res = c.GetSingleSection(SecLabel(arg))
			# Object was found?
			if res.IsObject():
				if not isinstance(res.value, Section):
					raise ValueError("Unexpected object type in 'result'")
				sec = res.value
				if ctx.IsRangeValid(sec.GetLoc()):
					if len(sec.keys) == 0:
						res = NO_KEY(sec.GetLoc())
					else:
						res = sec.GetSingleKey(k)
						if res.IsObject():
							if not isinstance(res.value, Key):
								raise ValueError("Unexpected object type in 'result'")
							key = res.value
							res = Result('=', f"{key.name} @{key.GetLoc().idx_0} :{key.GetCRC():08X}", key.GetLoc())
					return res
				else:
					res = INV_RANGE(sec.GetLoc())	# bug?
			return res
	return MISSING_ARG


def GetKey(ctx : Context) -> Result:
	"""
	High level command to return the value of a key:
		- arg0: section
		- arg1: key
		- arg2: configuration file name (optional)
	The value is returned either as simple string or base64 for multi-line keys
	Returns:
		- MISSING_ARG : when command line parameters are missing
		- NO_SECTION: Section was not found
		- EXTRA_ARGS: If too many arguments were given
		- NO_FILE: If file was not found
		- MULT_SECTION: Multiple section was found
		- NO_SECTION: No section was found
		- INV_RANGE: The given line value is out of range
		- String for single line responses
		- Encoding for multi line responses
	"""
	# Get section
	arg = ctx.GetArg()
	if arg and not ctx.IsLastFileArg(arg):
		sec_label = SecLabel(arg)
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
			res = c.GetSingleSection(sec_label)
			if res.code != 's':
				return res
			if not isinstance(res.value, Section):
				raise ValueError("Unexpected object type in 'result'")
			sec = res.value
			if ctx.IsRangeValid(sec.GetLoc()):
				# Search for key
				res = sec.GetSingleKey(k)
				if res.IsObject():
					if not isinstance(res.value, Key):
						raise ValueError("Unexpected object type in 'result'")
					key = res.value
					if key.IsMultiLine():
						# Encode multiline response
						res.code = '*'
						res.value = EncodeMultiLine(key.value)
					else:
						# Simple response for single line
						res.code = '='
						res.value = key.GetSingleLineValue()
			else:
				res = INV_RANGE(sec.GetLoc())	# bug?
			return res
	return MISSING_ARG



def EditKey(ctx : Context) -> Result:
	"""
	High level command to edit a simple line key:
		- arg0: section
		- arg1: key
		- arg2: New value
		- arg3: configuration file name (optional)
	This command also adds a new key value if it does not exists.
	Returns:
		- MISSING_ARG : when command line parameters are missing
		- NO_SECTION: Section was not found
		- EXTRA_ARGS: If too many arguments were given
		- NO_FILE: If file was not found
		- MULT_SECTION: Multiple section was found
		- NO_SECTION: No section was found
		- INV_RANGE: The given line value is out of range
	"""
	# Get section
	arg = ctx.GetArg()
	if arg and not ctx.IsLastFileArg(arg):
		sec_label = SecLabel(arg)
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
				res = c.GetSingleSection(sec_label)
				if res.code != 's':
					return res
				if not isinstance(res.value, Section):
					raise ValueError("Unexpected object type in 'result'")
				sec = res.value
				if ctx.IsRangeValid(sec.GetLoc()):
					# Search for key
					res = sec.GetSingleKey(k)
					# Found a key?
					if res.IsKindOf(NO_KEY(NO_LOC)):
						# Append entry
						ctx.AddLines(sec.GetLoc(), [f"{k}: {data}\n"])
						# Writes results
						res = ctx.WriteLines()
					elif res.IsObject():
						if not isinstance(res.value, Key):
							raise ValueError("Unexpected object type in 'result'")
						# Modify existing line
						key = res.value
						if key.IsMultiLine():
							return ML_KEY(key.GetLoc())
						if key.GetSingleLineValue() == data:
							return OK
						# This method preserves comments
						ctx.EditLine(key.GetLoc(), f"{k}: {data}")
						# Writes results
						res = ctx.WriteLines()
				else:
					res = INV_RANGE(sec.GetLoc())	# bug?
				return res
	return MISSING_ARG


def EditKeyML(ctx : Context) -> Result:
	"""
	High level command to edit a multiline key:
		- arg0: section
		- arg1: key
		- arg2: base64 encoded and encrypted data (use `EncodeMultiLine`)
		- arg3: configuration file name (optional)
	This command also adds a new key value if it does not exists.
	"""
	# Get section
	arg = ctx.GetArg()
	if arg and not ctx.IsLastFileArg(arg):
		sec_label = SecLabel(arg)
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
				res = c.GetSingleSection(sec_label)
				if res.code != 's':
					return res
				if not isinstance(res.value, Section):
					raise ValueError("Unexpected object type in 'result'")
				sec = res.value
				if ctx.IsRangeValid(sec.GetLoc()):
					# Search for key
					res = sec.GetSingleKey(k)
					# Found a key?
					if res.IsObject():
						if not isinstance(res.value, Key):
							raise ValueError("Unexpected object type in 'result'")
						# Modify existing line
						key = res.value
						if not key.IsMultiLine():
							return ML_KEY(key.GetLoc())
						if key.GetMultiLineValue() == data:
							return OK
						# Use section location
						loc = key.GetLoc()
						if loc.idx_0 is None:
							raise ValueError("Unexpected object type in 'loc'")
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


def DelKey(ctx : Context) -> Result:
	"""
	High level command to delete a key:
		- arg0: section
		- arg1: key
		- arg2: configuration file name (optional)
	"""
	# Get section
	arg = ctx.GetArg()
	if arg and not ctx.IsLastFileArg(arg):
		sec_label = SecLabel(arg)
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
			res = c.GetSingleSection(sec_label)
			if res.code != 's':
				return res
			if not isinstance(res.value, Section):
				raise ValueError("Unexpected object type in 'result'")
			sec = res.value
			if ctx.IsRangeValid(sec.GetLoc()):
				# Search for key
				res = sec.GetSingleKey(k)
				# Found a key?
				if res.IsObject():
					if not isinstance(res.value, Key):
						raise ValueError("Unexpected object type in 'result'")
					# Modify existing line
					key = res.value
					ctx.DeleteRange(key.GetLoc())
					res = ctx.WriteLines()
			else:
				res = INV_RANGE(sec.GetLoc())	# bug?
			return res
	return MISSING_ARG


def RenSec(ctx : Context) -> Result:
	"""
	High level command to rename a section:
		- arg0: old section name
		- arg1: new section name
		- arg2: configuration file name (optional)
	"""
	# Get old section name
	arg = ctx.GetArg()
	if arg and not ctx.IsLastFileArg(arg):
		sec_label_old = SecLabel(arg)
		# Get new section name
		arg = ctx.GetArg()
		if arg and not ctx.IsLastFileArg(arg):
			sec_label_new = SecLabel(arg)
			# Load configuration file
			res = ctx.ReadLines()
			if not res:
				return res
			# Load contents
			c = Contents(ctx)
			c.Load()
			# locate section
			res = c.GetSingleSection(sec_label_old)
			if res.IsObject():
				if not isinstance(res.value, Section):
					raise ValueError("Unexpected object type in 'result'")
				s = res.value
				if ctx.IsRangeValid(s.GetLoc()):
					ctx.EditLine(s.GetLoc(), f"[{sec_label_new}]")
					res = ctx.WriteLines()
				else:
					res = INV_RANGE(s.GetLoc())	# bug?
			return res
	return MISSING_ARG


def DelSec(ctx : Context) -> Result:
	"""
	High level command to delete a section:
		- arg0: section name or line number. For line number use `@nnn` format
		- arg1: configuration file name (optional)
	"""
	# Get section or number
	arg = ctx.GetArg()
	if arg and not ctx.IsLastFileArg(arg):
		# Load configuration file
		res = ctx.ReadLines()
		if not res:
			return res
		# Load contents
		c = Contents(ctx)
		c.Load()
		if arg.startswith('@'):
			# Locate section by line number
			res = c.GetSectionOfLine(int(arg[1:]))
		else:
			# locate section
			res = c.GetSingleSection(SecLabel(arg))
		# Object was found?
		if res.IsObject():
			if not isinstance(res.value, Section):
				raise ValueError("Unexpected object type in 'result'")
			s = res.value
			if ctx.IsRangeValid(s.GetLoc()):
				# Remove section, including preceding comment lines
				ctx.DeleteRangeWithComments(s.GetLoc())
				# Write buffer
				res = ctx.WriteLines()
			else:
				res = INV_RANGE(s.GetLoc())	# bug?
		return res
	return MISSING_ARG


def ReadSec(ctx : Context) -> Result:
	"""
	This high level method reads all lines of a section, including its header line 
	and comments. 
		- arg0: section name or line number. For line number use `@nnn` format
		- arg1: configuration file name (optional)
	"""
	# Get section or number
	arg = ctx.GetArg()
	if arg and not ctx.IsLastFileArg(arg):
		# Load configuration file
		res = ctx.ReadLines()
		if not res:
			return res
		# Load contents
		c = Contents(ctx)
		c.Load()
		if arg.startswith('@'):
			# Locate section by line number
			res = c.GetSectionOfLine(int(arg[1:]))
		else:
			# locate section
			res = c.GetSingleSection(SecLabel(arg))
		if res.IsObject():
			if not isinstance(res.value, Section):
				raise ValueError("Unexpected object type in 'result'")
			s = res.value
			if ctx.IsRangeValid(s.GetLoc()):
				loc = s.GetLoc()
				if loc.idx_0 is None:
					raise ValueError("Invalid location")
				if loc.idx_n:
					loc.idx_n += 1
				else:
					loc.idx_n = loc.idx_0 + 1
				lines = ctx.GetLines(loc)
				if not lines:
					res = EMPTY
				elif len(lines) == 0:
					res = Result('=', lines[0], s.GetLoc())
				else:
					res = Result('*', EncodeMultiLine(lines), s.GetLoc())
			else:
				res = INV_RANGE(s.GetLoc())	# bug?
		return res
	return MISSING_ARG


def AddSec(ctx : Context) -> Result:
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
	arg = ctx.GetArg()
	if arg and not ctx.IsLastFileArg(arg):
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
			loc : Loc | None = None
			if arg.startswith('@top'):
				s = c.GetFirstSection()
				if s:
					loc = Loc(s.GetLoc().idx_0)
					if loc.idx_0 is None:
						raise ValueError('Invalid Location object')
					if loc.idx_0 > 0:
						loc.idx_0 -= 1
				res = OK
			elif arg.startswith('@bottom'):
				res = OK
				if c.sections:
					res = Result('s', c.sections[-1], c.sections[-1].GetLoc())
			elif arg.startswith('@'):
				# Locate section by line number
				res = c.GetSectionOfLine(int(arg[1:]))
			else:
				# locate section
				res = c.GetSingleSection(SecLabel(arg))
			# Get location
			if loc:
				pass
			elif res.IsOk():
				loc = Loc(c.save.idx_0)
			if res.IsObject():
				if not isinstance(res.value, Section):
					raise ValueError("Unexpected object type in 'result'")
				# Objects results are of Section type
				s = res.value
				# Insert at the bottom
				loc = Loc(s.GetLoc().idx_n)
			# Execute only if no errors found
			if not res.IsError():
				if loc is None:
					raise ValueError("Invalid location value")
				c.AddSectionLines(loc, data)
				res = ctx.WriteLines()
			return res
	return MISSING_ARG


def OvrSec(ctx : Context) -> Result:
	"""
	This high level method replaces an entire section, including its header line, 
	with the given base64 encoded contents. The content of the base64 is not validated
	and written as is.
		- arg0: section name or line number. For line number use `@nnn` format
		- arg1: base64 encoded data (use `EncodeMultiLine`)
		- arg1: configuration file name (optional)
	"""
	# Get section or number
	arg = ctx.GetArg()
	if arg and not ctx.IsLastFileArg(arg):
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
			if arg.startswith('@'):
				# Locate section by line number
				res = c.GetSectionOfLine(int(arg[1:]))
			else:
				# locate section
				res = c.GetSingleSection(SecLabel(arg))
			# Execute only if no errors found
			if res.IsObject():
				if not isinstance(res.value, Section):
					raise ValueError("Unexpected object type in 'result'")
				s = res.value
				ctx.OvrSectionLines(s.GetLoc(), data)
				res = ctx.WriteLines()
			return res
	return MISSING_ARG


def GetSave(ctx : Context) -> Result:
	# Load configuration file
	res = ctx.ReadLines()
	if res:
		# Load contents
		c = Contents(ctx)
		c.Load()
		lines = c.GetPersistence()
		res = Result('*', EncodeMultiLine(lines), c.save)
	return res


def Save(ctx : Context) -> Result:
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
		c.ReplacePersistence(data)
		return ctx.WriteLines()
	return MISSING_ARG

