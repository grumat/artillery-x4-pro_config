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
	from ..edit_cfg import LineFactory, FileBuffer
else:
	from edit_cfg import LineFactory, FileBuffer


def Test_001():
	ftest = os.path.join(current_dir, "test_line.txt")
	source = os.path.join(assets_dir, "artillery_X4_pro.grumat.cfg")
	buffer = FileBuffer()
	buffer.Load(source)
	with open(ftest, 'wt', encoding="utf-8") as fw:
		for line in buffer.lines:
			lt = expand_tabs(line.raw_content)
			if len(lt) > 46:
				lt = lt[:46] + '...'
			print(f"{lt:49} {repr(line)}", file=fw)
	if files_equal(ftest, os.path.join(current_dir, "results", "test_line-001.txt")):
		print(GREEN + "Test PASSED!" + NORMAL)
	else:
		print(RED + "Test FAILED!" + NORMAL)

def Test_002():
	ftest = os.path.join(current_dir, "test_line.txt")
	source = os.path.join(current_dir, "test-reference.cfg")
	buffer = FileBuffer()
	buffer.Load(source)
	with open(ftest, 'wt', encoding="utf-8") as fw:
		for line in buffer.lines:
			lt = expand_tabs(line.raw_content)
			if len(lt) > 46:
				lt = lt[:46] + '...'
			print(f"{lt:49} {repr(line)}", file=fw)
	if files_equal(ftest, os.path.join(current_dir, "results", "test_line-002.txt")):
		print(GREEN + "Test PASSED!" + NORMAL)
	else:
		print(RED + "Test FAILED!" + NORMAL)

def main():
	Test_001()
	Test_002()

if __name__ == "__main__":
	main()
