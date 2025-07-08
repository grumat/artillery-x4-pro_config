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

def GetKeyML(fh, var : str, fn : str, sec : str, key : str):
	"Use for encoded multiline keys"
	ctx = edit_cfg.Context([sec, key, fn])
	res = edit_cfg.GetKey(ctx)
	if res.code != '*':
		raise Exception(f"{res}")
	fh.write(f"{var} = '{res.value}'\r\n")

def main():
	fn = os.path.join(assets_dir, "encoded_data.py")
	with open(fn, 'wt', encoding="utf-8") as fh:
		fh.write("#!/usr/bin/python3\n")
		fh.write("# -*- coding: UTF-8 -*-\n")
		fh.write("# This file is auto-generated: DO NOT EDIT!\n")
		fh.write("\n")
		fn = os.path.join(MODULAR_CONFIG, "modules", "sw-x4-plus", "gcode.cfg")
		GetKeyML(fh, "M600", fn, "gcode_macro M600", "gcode")

if __name__ == "__main__":
	main()
