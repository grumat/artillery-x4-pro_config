#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# Spellchecker: words gcode grumat

import sys
import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the 'assets' directory
project_dir = os.path.normpath(os.path.join(current_dir, '..'))
# Construct the path to the 'assets' directory
assets_dir = os.path.normpath(os.path.join(project_dir, 'assets'))

# Add the 'project_dir' directory to sys.path
sys.path.append(project_dir)
# Add the 'scripts' directory to sys.path
sys.path.append(assets_dir)

# Now you can import helper_functions as if it were a module
import edit_cfg	# type:ignore

def GetML(fh, var : str, cmd_line : list[str]):
	res = edit_cfg.EditConfig(cmd_line)
	if res.code != '*':
		raise Exception(f"{res}")
	fh.write(f"{var} = '{res.value}'\n")

def GetLine(fh, var : str, cmd_line : list[str]):
	res = edit_cfg.EditConfig(cmd_line)
	if res.code != '=':
		raise Exception(f"{res}")
	fh.write(f"{var} = '{res.value}'\n")

def main():
	fn = os.path.join(project_dir, "encoded_data.py")
	with open(fn, 'wt', encoding="utf-8") as fh:
		fh.write("#!/usr/bin/python3\n")
		fh.write("# -*- coding: UTF-8 -*-\n")
		fh.write("# This file is auto-generated: DO NOT EDIT!\n")
		fh.write("\n")
		fn_x4pro_grumat = os.path.join(assets_dir, "artillery_X4_pro.grumat.cfg")
		fn_x4plus_grumat = os.path.join(assets_dir, "artillery_X4_plus.grumat.cfg")
		fn_x4pro_upg = os.path.join(assets_dir, "artillery_X4_pro.upg.cfg")
		fn_x4plus_upg = os.path.join(assets_dir, "artillery_X4_plus.upg.cfg")
		GetML(fh, 'M600', ["GetKey", "gcode_macro M600", "gcode", fn_x4plus_grumat])
		GetML(fh, 'RESET_CFG_SWX4_PLUS', ["GetSave", fn_x4plus_grumat])
		GetML(fh, 'RESET_CFG_SWX4_PRO', ["GetSave", fn_x4pro_grumat])

		GetLine(fh, 'X_MAX_PRO', ["GetKey", "stepper_x", "position_max", fn_x4pro_upg ])
		GetLine(fh, 'X_MAX_PLUS', ["GetKey", "stepper_x", "position_max", fn_x4plus_upg ])
		GetLine(fh, 'Y_DIR_PRO', ["GetKey", "stepper_y", "dir_pin", fn_x4pro_upg ])
		GetLine(fh, 'Y_DIR_PLUS', ["GetKey", "stepper_y", "dir_pin", fn_x4plus_upg ])
		GetLine(fh, 'Y_MIN_PRO', ["GetKey", "stepper_y", "position_min", fn_x4pro_upg ])
		GetLine(fh, 'Y_MIN_PLUS', ["GetKey", "stepper_y", "position_min", fn_x4plus_upg ])
		GetLine(fh, 'Y_STOP_PRO', ["GetKey", "stepper_y", "position_endstop", fn_x4pro_upg ])
		GetLine(fh, 'Y_STOP_PLUS', ["GetKey", "stepper_y", "position_endstop", fn_x4plus_upg ])
		GetLine(fh, 'Y_MAX_PRO', ["GetKey", "stepper_y", "position_max", fn_x4pro_upg ])
		GetLine(fh, 'Y_MAX_PLUS', ["GetKey", "stepper_y", "position_max", fn_x4plus_upg ])
		GetLine(fh, 'Z_MAX_PRO', ["GetKey", "stepper_z", "position_max", fn_x4pro_upg ])
		GetLine(fh, 'Z_MAX_PLUS', ["GetKey", "stepper_z", "position_max", fn_x4plus_upg ])

if __name__ == "__main__":
	main()
