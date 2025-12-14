#
# -*- coding: UTF-8 -*-
#
# Spellchecker: words mline mlines gcode klipper bltouch

import zlib
import bz2
import re
import base64
from unidecode import unidecode


DEBUG_IS_LIKE_GCODE = 0


def EncodeB64(payload : str) -> str:
	# BZ2 compressor...
	pk = bz2.compress(payload.encode('utf-8'))
	# ...then BASE64 encoder
	enc = base64.b64encode(pk)
	# Finally, back to internal string representation
	return enc.decode('utf-8')

def DecodeB64(b64 : str) -> str:
	# Decode BASE64
	ba = base64.b64decode(b64.encode('utf-8'))
	# Decompress BZ2
	return bz2.decompress(ba).decode('utf-8')


PRINT = re.compile(r'M117\s+(.*)')
GCODE = re.compile(r'([GM][\d]+)\s*(.*)')
GCODE2 = re.compile(r'(params\.\w+)\s*(.*)')
GCODE3 = re.compile(r'(\|\s*default\([\d\.]+\))\s*(.*)')
GCODE4 = re.compile(r'(\|\s*(?:int|float))\s*(.*)')
IDENTIFIER = re.compile(r'([a-zA-Z_]\w*)\s*(.*)')
WORD_LIKE = re.compile(r'^(:?[A-Z]+|[a-zA-Z][a-z]*)$')
ID_VALUE = re.compile(r'([a-zA-Z_][\w\.]+)\s*(.*)')
SCALAR = re.compile(r'(\d+(?:\.\d+)?[a-zA-Z]{1,4})\b')
NUMBER = re.compile(r'(\d+(?:\.\d+)?)\s*(.*)')
QUOTE1 = re.compile(r'(.*?)(".*?")(.*)')
QUOTE2 = re.compile(r"(.*?)('.*?')(.*)")

RESERVED = {
	'False',
	'True',
}

KNOWN_GCODE = {
	# Standard G-codes
	"G0",
	"G1", 
	"G10", 
	"G11", 
	"G28", 
	"G4", 
	"G90", 
	"G91", 
	"G92", 
	"M104", 
	"M106", 
	"M107", 
	"M109", 
	"M112",
	"M114", 
	"M115", 
	"M117", 
	"M140", 
	"M18", 
	"M190", 
	"M25", 
	"M220", 
	"M221",
	"M400",
	"M82", 
	"M83", 
	"M84", 
	# Klipper extended commands
	"ACCELEROMETER_MEASURE", 
	"ACCELEROMETER_QUERY",
	"ACTIVATE_EXTRUDER", 
	"AXIS_TWIST_COMPENSATION_CALIBRATE",
	"BED_MESH_CALIBRATE", 
	"BED_MESH_CLEAR",
	"BED_MESH_MAP", 
	"BED_MESH_OFFSET", 
	"BED_MESH_OUTPUT", 
	"BED_MESH_PROFILE", 
	"BED_SCREWS_ADJUST",
	"BED_TILT_CALIBRATE", 
	"BLTOUCH_DEBUG", 
	"CALC_MEASURED_SKEW", 
	"CLEAR_LAST_FILE", 
	"DELTA_CALIBRATE", 
	"END_PRINT", 
	"EXCLUDE_OBJECT_DEFINE", 
	"EXCLUDE_OBJECT_END",
	"EXCLUDE_OBJECT_START", 
	"EXCLUDE_OBJECT", 
	"FIRMWARE_RESTART", 
	"FORCE_MOVE", 
	"GET_CURRENT_SKEW",
	"GET_RETRACTION",
	"NEOPIXEL_DISPLAY", 
	"QUERY_FILAMENT_SENSOR", 
	"RESTORE_DUAL_CARRIAGE_STATE",
	"RESTORE_GCODE_STATE",
	"SAVE_CONFIG",
	"SAVE_DUAL_CARRIAGE_STATE", 
	"SAVE_GCODE_STATE", 
	"SAVE_LAST_FILE", 
	"SAVE_VARIABLE", 
	"SET_DISPLAY_GROUP",
	"SET_DISPLAY_TEXT", 
	"SET_DUAL_CARRIAGE", 
	"SET_EXTRUDER_ROTATION_DISTANCE",
	"SET_FAN_SPEED", 
	"SET_FILAMENT_SENSOR",
	"SET_GCODE_VARIABLE",
	"SET_IDLE_TIMEOUT",
	"SET_KINEMATIC_POSITION",
	"SET_PIN",
	"SET_PRESSURE_ADVANCE", 
	"SET_RETRACTION", 
	"SET_SERVO", 
	"SET_SKEW", 
	"SET_TMC_CURRENT", 
	"SET_TMC_FIELD", 
	"SET_VELOCITY_LIMIT", 
	"SKEW_PROFILE", 
	"START_PRINT", 
	"STATUS", 
	"STEPPER_BUZZ", 
	"SYNC_EXTRUDER_MOTION", 
	"TUNING_TOWER", 
	"UPDATE_DELAYED_GCODE", 
}


def _eval_i18n_(txt : str) -> tuple[str, str]:
	txt = txt.strip().replace(r'\"', '`').replace(r"\'", '`')
	out = ''
	while len(txt) > 0:
		if (m := QUOTE1.match(txt)):
			out += ' ' + m[1] + ' s123 ' # s123 represents a generic string here, but in coincidence with an identifier
			txt = m[3]
		elif (m := QUOTE2.match(txt)):
			out += ' ' + m[1] + ' s123 ' # s123 represents a generic string here, but in coincidence with an identifier
			txt = m[3]
		else:
			out = txt
			break
	s = ''
	for ch in out:
		if ord(ch) > 127:
			s += 'x'
	return (s, unidecode(out))


def _count_triplets_(txt :str, any_of_1 : str, center : str, any_of_2 : str) -> int:
	cnt = 0
	i = 1
	while (i + 2) < len(txt):
		if txt[i-1] in any_of_1 \
			and txt[i] == center \
			and txt[i+1] in any_of_2:
			cnt += 1
		i += 1
	return cnt

def IsLikeGCode(txt : str) -> bool:
	if DEBUG_IS_LIKE_GCODE:
		orig = txt
	s, txt = _eval_i18n_(txt)
	# English chars only
	while len(txt) > 0:
		if txt[0].isspace():
			txt = txt.lstrip()
		elif txt.startswith(('{%', '%}')):
			s += 'gg'
			txt = txt[2:]
		elif (m := PRINT.match(txt)):
			s = s.replace('x', '')	# cancel i18n occurrences
			s += 'gg'
			txt = txt[2:]
		elif (m := GCODE.match(txt)):
			s += 'g'
			if (len(s) == 0) and (m[1].upper() in KNOWN_GCODE):
				s += 'g'
			txt = m[2]
		elif (m := GCODE2.match(txt)) \
			or (m := GCODE3.match(txt)) \
			or (m := GCODE4.match(txt)):
			s += 'g'
			txt = m[2]
		elif (m := IDENTIFIER.match(txt)):
			if WORD_LIKE.match(m[1]) \
				and (m[1] not in RESERVED):
				s += len(m[1]) == 1 and 'w' or 'W'
			elif (len(s) == 0) and (m[1].upper() in KNOWN_GCODE):
				s += 'gg'
			else:
				s += 'i'
			txt = m[2]
		elif (m := ID_VALUE.match(txt)):
			s += 'i'
			txt = m[2]
		elif (m := SCALAR.match(txt)):
			s += 'w'
			start, end = m.span()
			txt = txt[end:]
		elif (m := NUMBER.match(txt)):
			s += 'n'
			txt = m[2]
		elif txt[0] in ',.=-':
			s += txt[0]
			txt = txt[1:]
		elif txt[0] in '{}<>/[]*':
			s += 'o'
			txt = txt[1:]
		elif ord(txt[0]) > 127:
			if not s.endswith('x'):
				s += 'x'
			txt = txt[1:]
		else:
			if DEBUG_IS_LIKE_GCODE:
				print (txt[0])
			s += txt[0]
			txt = txt[1:]
	pgm = 0
	nat = 0
	pgm += 5*s.count('g')
	pgm += 3*s.count('i')
	pgm += 2*s.count('o')
	pgm += s.count('n')
	pgm += 3*s.count('-n')
	pgm += s.count('w')
	pgm += 6*_count_triplets_(s, "i", '=',  "i")
	pgm += 5*_count_triplets_(s, "i", '=',  "inw")
	pgm += 5*_count_triplets_(s, "inwW", '=',  "i")
	pgm += 4*_count_triplets_(s, "i", '=',  "W")
	pgm += 5*_count_triplets_(s, "w", '=',  "in")
	pgm += 4*_count_triplets_(s, "w", '=',  "w")
	pgm += 3*_count_triplets_(s, "W", '=',  "Winw")
	pgm += 3*_count_triplets_(s, "w", '=',  "W")
	pgm += 5*_count_triplets_(s, "i", '.',  "Ww")
	pgm += 5*_count_triplets_(s, "Ww", '.',  "i")
	pgm += 4*_count_triplets_(s, "W", '.',  "w")
	pgm += 4*_count_triplets_(s, "w", '.',  "W")
	pgm += 3*_count_triplets_(s, "W", '.',  "W")
	nat += s.count('W')
	nat += s.count('w')
	nat += s.count('x')
	nat += ((n := s.count('W')) > 3) and (2*n) or 0
	nat += ((n := s.count('n')) <= 3) and n or 0
	nat += s.endswith(('...', '.', ',', '!', '?'))
	if DEBUG_IS_LIKE_GCODE:
		print (f'{s:20}: {pgm}:{nat}: {orig.strip()}')
	return pgm >= nat


def GetHeadSpacesOfCommentedLine(txt : str) -> str:
	res = ''
	for ch in txt:
		if ch.isspace():
			res += ch
		elif ch in ';#':
			if len(res):
				break
		else:
			break
	return res


def _string_essence_(s : str) -> bytes:
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


class StringEssence(bytes):
	def __new__(cls, value : str|bytes):
		if isinstance(value, str):
			value = _string_essence_(value)
		return super().__new__(cls, value)
	def __init__(self, value : str|bytes):
		pass
	def __repr__(self):
		return f"StringEssence({super().__repr__()})"
	def GetCRC(self, seed = 0):
		return CrcKey(zlib.crc32(self, seed))


class CrcKey(int):
	"""A subclass of int for representing CRC32 values."""

	def __new__(cls, value: int|str|bytes) -> CrcKey:
		if isinstance(value, bytes):
			# Compute CRC32 for the string
			crc = zlib.crc32(value, 0)
			return super().__new__(cls, crc)
		elif isinstance(value, str):
			# Compute CRC32 for the string
			crc = zlib.crc32(value.encode('utf-8'), 0)
			return super().__new__(cls, crc)
		elif isinstance(value, int):
			# Directly assign the integer
			return super().__new__(cls, value)
		else:
			assert False, "CrcKey must be initialized with int or str"
	def __init__(self, value: int|str|bytes) -> None:
		# __init__ is only for type hints and documentation
		pass
	def __repr__(self) -> str:
		return f"CrcKey(0x{self:08X})"


def StringCRC(s : str, seed : int|CrcKey) -> CrcKey:
	"""Computes CRC of a string normalizing it with the `_string_essence_` method"""
	return CrcKey(zlib.crc32(_string_essence_(s), seed))

