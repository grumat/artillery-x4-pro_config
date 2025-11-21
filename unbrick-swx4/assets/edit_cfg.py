#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# This file contains lots of tools to edit `printer.cfg` Klipper files
# It has to be "minified" with the `minify_python_code.py` script and
# sent to the printer, so that local editing is possible.

import sys
import os
import re
import zlib
import bz2
import base64
import fnmatch
from typing import Callable, Union, TypeGuard

MODULE = sys.modules[__name__]


def main(args : list[str]) -> Res:
	ctx = Context(args)
	res = NO_FN
	try:
		fn = ctx.GetArg()
		if fn:
			if hasattr(MODULE, fn):
				res = getattr(MODULE, fn)(ctx)
	except Exception as e:
		res = Res('!', "XCP: " + str(e))
	return res

if __name__ == "__main__":
	print(main(sys.argv[1:]))
