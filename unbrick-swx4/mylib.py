#
# -*- coding: UTF-8 -*-

def TryParseInt(s, default=None) -> int | None:
	try:
		return int(s)
	except ValueError:
		return default

