#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sys
import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the 'assets' directory
assets_dir = os.path.normpath(os.path.join(current_dir, '..', 'assets'))

# Add the 'scripts' directory to sys.path
sys.path.append(assets_dir)

# Now you can import helper_functions as if it were a module
import edit_cfg

MODULAR_CONFIG = os.path.normpath(os.path.join(current_dir, "..", "..", "modular-config"))

def GetKey(fh, var : str, fn : str, sec : str, key : str):
	"Use for encoded multiline keys"
	edit_cfg.ARGS = [sec, key, fn]
	code, val, pos = edit_cfg.GetKey()
	if code != '*':
		raise Exception(f"{code}{val}")
	fh.write(f"{var} = '{val}'\r\n")

def main():
	fn = os.path.join(assets_dir, "encoded_data.py")
	with open(fn, 'wt', encoding="utf-8") as fh:
		fh.write("#!/usr/bin/python3\r\n")
		fh.write("# -*- coding: UTF-8 -*-\r\n")
		fh.write("# This file is auto-generated: DO NOT EDIT!\r\n")
		fh.write("\r\n")
		fn = os.path.join(MODULAR_CONFIG, "modules", "sw-x4-plus", "gcode.cfg")
		GetKey(fh, "M600", fn, "gcode_macro M600", "gcode")

if __name__ == "__main__":
	main()
