#
# -*- coding: UTF-8 -*-
#
# Spellchecker: words mline mlines gcode

import zlib
import bz2
import re
import base64
from unidecode import unidecode


def EncodeB64(info) -> str:
	payload = repr(info)
	# BZ2 compressor...
	pk = bz2.compress(payload.encode('utf-8'))
	# ...then BASE64 encoder
	enc = base64.b64encode(pk)
	# Finally, back to internal string representation
	return enc.decode('utf-8')

def DecodeB64(b64 : str):
	# Decode BASE64
	ba = base64.b64decode(b64.encode('utf-8'))
	# Decompress BZ2
	payload = bz2.decompress(ba).decode('utf-8')
	return eval(payload)


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

RESERVED = (
	'False',
	'True',
)

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


def IsLikeGCode(txt : str) -> bool:
	#orig = txt
	s, txt = _eval_i18n_(txt)
	# English chars only
	while len(txt) > 0:
		if txt[0].isspace():
			txt = txt.lstrip()
		elif txt.startswith(('{%', '%}')):
			s += 'g'
			txt = txt[2:]
		elif (m := PRINT.match(txt)):
			s = s.replace('x', '')	# cancel i18n occurrences
			s += 'gggg'
			txt = txt[2:]
		elif (m := GCODE.match(txt)) \
			or (m := GCODE2.match(txt)) \
			or (m := GCODE3.match(txt)) \
			or (m := GCODE4.match(txt)):
			s += 'g'
			txt = m[2]
		elif (m := IDENTIFIER.match(txt)):
			if WORD_LIKE.match(m[1]) \
				and (m[1] not in RESERVED):
				s += len(m[1]) == 1 and 'w' or 'W'
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
			#print (txt[0])
			s += txt[0]
			txt = txt[1:]
	pgm = 0
	nat = 0
	pgm += 3*s.count('g')
	pgm += 2*s.count('i')
	pgm += s.count('o')
	pgm += s.count('n')
	pgm += s.count('-n')
	pgm += s.count('w')
	pgm += 2*s.count('i=n')
	pgm += 2*s.count('i=w')
	pgm += 2*s.count('i=W')
	pgm += s.count('w=n')
	pgm += s.count('W=n')
	pgm += s.count('w=w')
	pgm += s.count('w=W')
	pgm += s.count('W=w')
	pgm += 2*s.count('w=i')
	pgm += 2*s.count('W=i')
	nat += s.count('W')
	nat += s.count('w')
	nat += s.count('x')
	nat += ((n := s.count('W')) > 3) and (2*n) or 0
	nat += ((n := s.count('n')) <= 3) and n or 0
	nat += s.endswith(('...', '.', ',', '!', '?'))
	#print (f'{s:20}: {pgm}:{nat}: {orig.strip()}')
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

