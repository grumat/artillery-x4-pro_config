#
# -*- coding: UTF-8 -*-
#
# Spellchecker: words mline, mlines

import zlib
import bz2
import re
import base64
from unidecode import unidecode
from typing import TypeGuard, Any


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

