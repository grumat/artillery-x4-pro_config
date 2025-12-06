#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# Spellchecker: words gcode grumat endstop tupg

import sys
import os
import re
from typing import TYPE_CHECKING

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
if TYPE_CHECKING:
	from ..edit_cfg import *
else:
	from edit_cfg import *

def GetML(fh, var : str, cmd_line : list[str]):
	res = EditConfig(cmd_line)
	if res.code != '*':
		raise Exception(f"{res}")
	fh.write(f"{var} = '{res.value}'\n")

def GetLine(fh, var : str, cmd_line : list[str]) -> None:
	res = EditConfig(cmd_line)
	if res.code != '=':
		raise Exception(f"{res}")
	fh.write(f"{var} = '{res.value}'\n")

def GetCRC(fh, var : str, section : str, key : str, fname : str) -> None:
	res = EditConfig(["ListKey", section, key, fname])
	ld = res.GetSingleKeyList()
	fh.write(f"{var} = '{ld.crc}'\n")

def GetSecCRC(fh, var : str, section : str, fname : str) -> None:
	res = EditConfig(["ListSec", section, fname])
	lines = res.GetKeyList()
	if len(lines) != 1:
		raise ValueError("Invalid section '{section}'")
	fh.write(f"{var} = '{lines[0].crc}'\n")

def GetSecML(fh, var : str, section : str, fname : str) -> None:
	res = EditConfig(["ReadSec", section, fname])
	if res.code != '*':
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
		fn_x4pro_def = os.path.join(assets_dir, "artillery_X4_pro.def.cfg")
		fn_x4plus_def = os.path.join(assets_dir, "artillery_X4_plus.def.cfg")
		fn_x4pro_extra = os.path.join(assets_dir, "extras.pro.cfg")
		fn_x4plus_extra = os.path.join(assets_dir, "extras.plus.cfg")

		GetML(fh, 'M600', ["GetKey", "gcode_macro M600", "gcode", fn_x4plus_grumat])

		## Factory default persistence
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetML(fh, 'RESET_CFG_PRO', ["GetSave", fn_x4pro_upg])
		GetML(fh, 'RESET_CFG_PLUS', ["GetSave", fn_x4plus_upg])

		## stepper_x / stepper_y / stepper_z ranges
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
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

		## homing_override / gcode
		fh.write("\n")
		fh.write("# def:\t\tgrumat\n")
		fh.write("# upg:\t\tgrumat\n")
		fh.write("# grumat:\tY\n")
		GetCRC(fh, 'HOME_OVR_PRO_CRC', "homing_override", "gcode", fn_x4pro_grumat)
		GetCRC(fh, 'HOME_OVR_PLUS_CRC', "homing_override", "gcode", fn_x4plus_grumat)
		GetML(fh, 'HOME_OVR_PRO', ["GetKey", "homing_override", "gcode", fn_x4pro_grumat])
		GetML(fh, 'HOME_OVR_PLUS', ["GetKey", "homing_override", "gcode", fn_x4plus_grumat])

		## bed_mesh / mesh_max
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetLine(fh, 'MESH_MAX_PRO', ["GetKey", "bed_mesh", "mesh_max", fn_x4pro_upg ])
		GetLine(fh, 'MESH_MAX_PLUS', ["GetKey", "bed_mesh", "mesh_max", fn_x4plus_upg ])

		## gcode_macro G29 / gcode
		fh.write("\n")
		fh.write("# def:\t\tgrumat\n")
		fh.write("# upg:\t\tgrumat\n")
		fh.write("# grumat:\tY\n")
		GetCRC(fh, 'G29_PRO_CRC', "gcode_macro G29", "gcode", fn_x4pro_grumat )
		GetCRC(fh, 'G29_PLUS_CRC', "gcode_macro G29", "gcode", fn_x4plus_grumat )
		GetML(fh, 'G29_PRO', ["GetKey", "gcode_macro G29", "gcode", fn_x4pro_grumat])
		GetML(fh, 'G29_PLUS', ["GetKey", "gcode_macro G29", "gcode", fn_x4plus_grumat])

		## gcode_macro nozzle_wipe / gcode
		fh.write("\n")
		fh.write("# def:\t\tY\n")
		GetCRC(fh, 'WIPE_PRO_CRC_DEF', "gcode_macro nozzle_wipe", "gcode", fn_x4pro_def )
		GetCRC(fh, 'WIPE_PLUS_CRC_DEF', "gcode_macro nozzle_wipe", "gcode", fn_x4plus_def )
		GetML(fh, 'WIPE_PRO_DEF', ["GetKey", "gcode_macro nozzle_wipe", "gcode", fn_x4pro_def])
		GetML(fh, 'WIPE_PLUS_DEF', ["GetKey", "gcode_macro nozzle_wipe", "gcode", fn_x4plus_def])
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetCRC(fh, 'WIPE_PRO_CRC_UPG', "gcode_macro nozzle_wipe", "gcode", fn_x4pro_upg )
		GetCRC(fh, 'WIPE_PLUS_CRC_UPG', "gcode_macro nozzle_wipe", "gcode", fn_x4plus_upg )
		GetML(fh, 'WIPE_PRO_UPG', ["GetKey", "gcode_macro nozzle_wipe", "gcode", fn_x4pro_upg])
		GetML(fh, 'WIPE_PLUS_UPG', ["GetKey", "gcode_macro nozzle_wipe", "gcode", fn_x4plus_upg])

		## gcode_macro draw_line_only / gcode
		fh.write("\n")
		fh.write("# def:\t\tN\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetCRC(fh, 'LINE_ONLY_PRO_CRC', "gcode_macro draw_line_only", "gcode", fn_x4pro_upg )
		GetCRC(fh, 'LINE_ONLY_PLUS_CRC', "gcode_macro draw_line_only", "gcode", fn_x4plus_upg )
		GetML(fh, 'LINE_ONLY_PRO', ["GetKey", "gcode_macro draw_line_only", "gcode", fn_x4pro_upg])
		GetML(fh, 'LINE_ONLY_PLUS', ["GetKey", "gcode_macro draw_line_only", "gcode", fn_x4plus_upg])

		## gcode_macro draw_line / gcode
		fh.write("\n")
		fh.write("# def:\t\tY\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetCRC(fh, 'LINE_PRO_CRC_DEF', "gcode_macro draw_line", "gcode", fn_x4pro_def )
		GetCRC(fh, 'LINE_PLUS_CRC_DEF', "gcode_macro draw_line", "gcode", fn_x4plus_def )
		GetCRC(fh, 'LINE_PRO_CRC_UPG', "gcode_macro draw_line", "gcode", fn_x4pro_upg )
		GetCRC(fh, 'LINE_PLUS_CRC_UPG', "gcode_macro draw_line", "gcode", fn_x4plus_upg )

		## gcode_macro move_to_point_0 / gcode
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetCRC(fh, 'POINT0_PRO_CRC', "gcode_macro move_to_point_0", "gcode", fn_x4pro_upg )
		GetCRC(fh, 'POINT0_PLUS_CRC', "gcode_macro move_to_point_0", "gcode", fn_x4plus_upg )
		GetML(fh, 'POINT0_PRO', ["GetKey", "gcode_macro move_to_point_0", "gcode", fn_x4pro_upg])
		GetML(fh, 'POINT0_PLUS', ["GetKey", "gcode_macro move_to_point_0", "gcode", fn_x4plus_upg])

		## gcode_macro move_to_point_1 / gcode
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetCRC(fh, 'POINT1_PRO_CRC', "gcode_macro move_to_point_1", "gcode", fn_x4pro_upg )
		GetCRC(fh, 'POINT1_PLUS_CRC', "gcode_macro move_to_point_1", "gcode", fn_x4plus_upg )
		GetML(fh, 'POINT1_PRO', ["GetKey", "gcode_macro move_to_point_1", "gcode", fn_x4pro_upg])
		GetML(fh, 'POINT1_PLUS', ["GetKey", "gcode_macro move_to_point_1", "gcode", fn_x4plus_upg])

		## gcode_macro move_to_point_2 / gcode
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetCRC(fh, 'POINT2_PRO_CRC', "gcode_macro move_to_point_2", "gcode", fn_x4pro_upg )
		GetCRC(fh, 'POINT2_PLUS_CRC', "gcode_macro move_to_point_2", "gcode", fn_x4plus_upg )
		GetML(fh, 'POINT2_PRO', ["GetKey", "gcode_macro move_to_point_2", "gcode", fn_x4pro_upg])
		GetML(fh, 'POINT2_PLUS', ["GetKey", "gcode_macro move_to_point_2", "gcode", fn_x4plus_upg])

		## gcode_macro move_to_point_3 / gcode
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetCRC(fh, 'POINT3_PRO_CRC', "gcode_macro move_to_point_3", "gcode", fn_x4pro_upg )
		GetCRC(fh, 'POINT3_PLUS_CRC', "gcode_macro move_to_point_3", "gcode", fn_x4plus_upg )
		GetML(fh, 'POINT3_PRO', ["GetKey", "gcode_macro move_to_point_3", "gcode", fn_x4pro_upg])
		GetML(fh, 'POINT3_PLUS', ["GetKey", "gcode_macro move_to_point_3", "gcode", fn_x4plus_upg])

		## gcode_macro move_to_point_4 / gcode
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetCRC(fh, 'POINT4_PLUS_CRC', "gcode_macro move_to_point_4", "gcode", fn_x4plus_upg )
		GetML(fh, 'POINT4_PLUS', ["GetKey", "gcode_macro move_to_point_4", "gcode", fn_x4plus_upg])
		GetML(fh, 'POINT4_SEC_PLUS', ["ReadSec", "gcode_macro move_to_point_4", fn_x4plus_upg])

		## gcode_macro move_to_point_5 / gcode
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetCRC(fh, 'POINT5_PLUS_CRC', "gcode_macro move_to_point_5", "gcode", fn_x4plus_upg )
		GetML(fh, 'POINT5_PLUS', ["GetKey", "gcode_macro move_to_point_5", "gcode", fn_x4plus_upg])
		GetML(fh, 'POINT5_SEC_PLUS', ["ReadSec", "gcode_macro move_to_point_5", fn_x4plus_upg])

		## gcode_macro move_to_point_6 / gcode
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetCRC(fh, 'POINT6_PLUS_CRC', "gcode_macro move_to_point_6", "gcode", fn_x4plus_upg )
		GetML(fh, 'POINT6_PLUS', ["GetKey", "gcode_macro move_to_point_6", "gcode", fn_x4plus_upg])
		GetML(fh, 'POINT6_SEC_PLUS', ["ReadSec", "gcode_macro move_to_point_6", fn_x4plus_upg])

		## tmc2209 stepper_z / hold_current
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetLine(fh, 'HOLD_CURRENT_Z_LOW', ["GetKey", "tmc2209 stepper_z", "hold_current", fn_x4plus_upg ])
		GetLine(fh, 'HOLD_CURRENT_Z_HI', ["GetKey", "tmc2209 stepper_z", "hold_current", fn_x4pro_upg ])

		##  extruder / max_extrude_only_accel
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		fh.write("EXTRUDER_ACCEL_LOW = '6000'\n")
		fh.write("EXTRUDER_ACCEL_MID = '7000'\n")
		fh.write("EXTRUDER_ACCEL_HI = '8000'\n")

		##  tmc2209 extruder / run_current
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		fh.write("EXTRUDER_CURRENT_LOW = '0.8'\n")
		fh.write("EXTRUDER_CURRENT_MID = '0.9'\n")
		fh.write("EXTRUDER_CURRENT_HI = '1.0'\n")

		##  probe / x_offset
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		fh.write("PROBE_X_OFFSET = '-17'\n")
		fh.write("PROBE_Y_OFFSET = '17'\n")
		fh.write("PROBE_SPEED = '10.0'\n")
		fh.write("PROBE_SAMPLE = '2'\n")
		fh.write("PROBE_RESULT = 'average'\n")
		fh.write("PROBE_TOLERANCE = '0.03'\n")
		fh.write("PROBE_RETRIES = '3'\n")

		##  probe 180 / x_offset
		fh.write("\n")
		fh.write("# def:\t\tgrumat\n")
		fh.write("# upg:\t\tgrumat\n")
		fh.write("# grumat:\tY\n")
		fh.write("PROBE180_X_OFFSET = '-18'\n")
		fh.write("PROBE180_Y_OFFSET = '14'\n")
		fh.write("PROBE180_SPEED = '3.0'\n")
		fh.write("PROBE180_LIFT = '12.0'\n")
		fh.write("PROBE180_SAMPLE = '4'\n")
		fh.write("PROBE180_RESULT = 'median'\n")
		fh.write("PROBE180_TOLERANCE = '0.028'\n")
		fh.write("PROBE180_RETRIES = '5'\n")

		##  screws_tilt_adjust
		fh.write("\n")
		fh.write("# def:\t\tN\n")
		fh.write("# upg:\t\tN\n")
		fh.write("# grumat:\tY\n")
		GetSecCRC(fh, 'SCREWS_PRO_CRC', "screws_tilt_adjust", fn_x4pro_extra )
		GetSecCRC(fh, 'SCREWS_PLUS_CRC', "screws_tilt_adjust", fn_x4plus_extra )
		GetSecCRC(fh, 'SCREWS180_PRO_CRC', "screws_tilt_adjust", fn_x4pro_grumat )
		GetSecCRC(fh, 'SCREWS180_PLUS_CRC', "screws_tilt_adjust", fn_x4plus_grumat )
		GetSecML(fh, 'SCREWS_PRO', "screws_tilt_adjust", fn_x4pro_extra)
		GetSecML(fh, 'SCREWS_PLUS', "screws_tilt_adjust", fn_x4plus_extra)
		GetSecML(fh, 'SCREWS180_PRO', "screws_tilt_adjust", fn_x4pro_grumat)
		GetSecML(fh, 'SCREWS180_PLUS', "screws_tilt_adjust", fn_x4plus_grumat)

if __name__ == "__main__":
	main()
