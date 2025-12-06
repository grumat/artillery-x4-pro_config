#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# spellchecker: words grumat ftest

import os
import sys
from typing import TYPE_CHECKING

from test_utils import *


# Get the directory of the current script
current_dir = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
# Construct the path to the 'edit_cfg' library
lib_dir = os.path.normpath(os.path.join(current_dir, '..'))
# Construct the path to the 'assets' directory
assets_dir = os.path.normpath(os.path.join(lib_dir, 'assets'))

# Add the 'assets' directory to sys.path
sys.path.append(lib_dir)
sys.path.append(assets_dir)
# Now you can import helper_functions as if it were a module
if TYPE_CHECKING:
	from ..edit_cfg import Contents2
else:
	from edit_cfg import Contents2


def main():
	ftest = os.path.join(current_dir, "test_contents.txt")
	source = os.path.join(assets_dir, "artillery_X4_pro.grumat.cfg")
	contents = Contents2()
	contents.Load(source)
	with open(ftest, 'wt', encoding="utf-8") as fw:
		for line in contents.file_buffer.lines:
			msg = ""
			if line.buffer is None:
				msg += ' '*36
			else:
				msg += f"{repr(line.buffer):35} "
			lt = repr(line)
			if len(lt) > 56:
				msg += lt[:56] + '...'
			else:
				msg += f"{lt:59}"
			print(f"{msg} {line.raw_content}", file=fw)
	if files_equal(ftest, os.path.join(current_dir, "results", "test_contents-001.txt")):
		print(GREEN + "Test PASSED!" + NORMAL)
	else:
		print(RED + "Test FAILED!" + NORMAL)


if __name__ == "__main__":
	main()
