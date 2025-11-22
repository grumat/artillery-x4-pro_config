#
# -*- coding: UTF-8 -*-
#
# Spellchecker:	words MULT libtools

#from .loc import NO_LOC, Loc
from .result import Result, OK, NO_FN, MISSING_ARG, EXTRA_ARGS, INV_ENC, NO_FILE, NO_READ, EMPTY, ML_KEY, INV_FMT, NO_SECTION, MULT_SECTION, NO_KEY, MULT_KEY, INV_RANGE
from .parser import Context
#from .sections import SecLabel
from .libtools import StringEssence, EncodeMultiLine, DecodeMultiLine
from . import commands


def main(args : list[str]) -> Result:
	ctx = Context(args)
	res = NO_FN
	try:
		fn = ctx.GetArg()
		if fn:
			if hasattr(commands, fn):
				res = getattr(commands, fn)(ctx)
	except Exception as e:
		res = Result('!', "XCP: " + str(e))
	return res

