#
# -*- coding: UTF-8 -*-
#
# Spellchecker: words mline, mlines

import zlib
import bz2
import base64
from typing import TypeGuard, Any

from .line import MLine


def is_list_of_str(ml: Any) -> TypeGuard[list[str]]:
	return isinstance(ml, list) and (len(ml) == 0 or isinstance(ml[0], str))	# type: ignore

def is_list_of_mlines(ml: Any) -> TypeGuard[list[MLine]]:
	return isinstance(ml, list) and ml and not isinstance(ml[0], str)	# type: ignore

def EncodeMultiLine(ml : str | list[str] | list[MLine]) -> str:
	"""Long stuff is compressed and converted to base64 so that we can transmit over the serial line"""
	# MLines's: extract text only
	if isinstance(ml, str):
		stuff = ml
	# Any other list is considered having string
	elif is_list_of_str(ml):
		stuff = "".join(ml)
	elif is_list_of_mlines(ml):
		# Scan for trailing blank lines
		ml1 = ml
		last = len(ml1)
		while last > 0:
			last -= 1
			if not ml1[last].is_empty:
				break
		# Be sure to preserve last blank line
		last += 2
		if last < len(ml):
			ml1 = ml1[:last]
		stuff = "".join([l.line for l in ml1])
	else:
		# Handle unexpected cases (optional)
		raise ValueError("Unexpected type for 'ml'")
	# BZ2 compressor...
	pk = bz2.compress(stuff.encode('utf-8'))
	# ...then BASE64 encoder
	enc = base64.b64encode(pk)
	# Finally, back to internal string representation
	return enc.decode('utf-8')


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


def DecodeMultiLine(b64 : str) -> list[str]:
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

