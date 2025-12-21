#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# Spellchecker: words gcode grumat endstop gcode tupg klipper tabified

import sys
import os
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

def expand_tabs(line: str, tab_size: int = 4) -> str:
	"""
	Expands tabs in the input string to spaces, respecting tab stops.

	Args:
		line: The input string containing tabs.
		tab_size: The number of columns between tab stops (default: 4).

	Returns:
		The string with tabs replaced by the appropriate number of spaces.
	"""
	result = []
	column = 0
	for char in line:
		if char == "\t":
			# Calculate how many spaces are needed to reach the next tab stop
			spaces_needed = tab_size - (column % tab_size)
			result.append(" " * spaces_needed)
			column += spaces_needed
		else:
			result.append(char)
			column += 1
	return "".join(result)

def _tabs_to_(left : str, tab_cnt = 13) -> str:
	col = len(expand_tabs(left)) + 1
	to_col = tab_cnt * 4
	if col >= to_col:
		n = 1
	else:
		to_col -= col
		n = to_col >> 2
	return '\t'*n


def GetKey(fh, var : str, section : str, key : str, cmd : Commands) -> None:
	res = cmd.GetKey(section, key)
	if isinstance(res, str):
		data = f"{var} = {repr(res)}"
		fh.write(data)
		fh.write(_tabs_to_(data))
		fh.write(f"# Plain value\n")
	elif isinstance(res, MultiLineData):
		fh.write(_tabs_to_(''))
		fh.write(f"# BASE64 of a multiline value\n")
		fh.write(f"{var} = {repr(res.b64)}\n")
	else:
		raise RuntimeError(f"Cannot find key '{key}' or section '{section}'")

def GetPersistenceB64(fh, var : str, cmd : Commands):
	res = cmd.GetPersistenceB64()
	fh.write(_tabs_to_(''))
	fh.write(f"# BASE64 of the persistence area\n")
	fh.write(f"{var} = {repr(res)}\n")

def GetCRC(fh, var : str, section : str, key : str, cmd : Commands) -> None:
	res = cmd.ListKey(section, key)
	if isinstance(res, KeyInfo):
		data = f"{var} = {repr(res.crc)}"
		fh.write(data)
		fh.write(_tabs_to_(data))
		fh.write(f"# CRC object of a value\n")
	else:
		raise RuntimeError(f"Cannot find key '{key}' or section '{section}'")

def GetSecCRC(fh, var : str, section : str, cmd : Commands) -> None:
	res = cmd.ListSection(section)
	if isinstance(res, SectionInfo):
		data = f"{var} = {repr(res.crc)}"
		fh.write(data)
		fh.write(_tabs_to_(data))
		fh.write(f"# CRC object of a section\n")
	else:
		raise RuntimeError(f"Cannot find section {section}")

def GetSecML(fh, var : str, section : str, cmd : Commands) -> None:
	res = cmd.ReadSec(section)
	if not isinstance(res, str):
		raise RuntimeError(f"Cannot find section {section}")
	fh.write(_tabs_to_(''))
	fh.write(f"# BASE64 of an entire section\n")
	fh.write(f"{var} = {repr(res)}\n")



def main():
	fn_x4pro_grumat = Commands(os.path.join(assets_dir, "artillery_X4_pro.grumat.cfg"))
	fn_x4plus_grumat = Commands(os.path.join(assets_dir, "artillery_X4_plus.grumat.cfg"))
	fn_x4pro_upg = Commands(os.path.join(assets_dir, "artillery_X4_pro.upg.cfg"))
	fn_x4plus_upg = Commands(os.path.join(assets_dir, "artillery_X4_plus.upg.cfg"))
	fn_x4pro_def = Commands(os.path.join(assets_dir, "artillery_X4_pro.def.cfg"))
	fn_x4plus_def = Commands(os.path.join(assets_dir, "artillery_X4_plus.def.cfg"))
	fn_x4pro_extra = Commands(os.path.join(assets_dir, "extras.pro.cfg"))
	fn_x4plus_extra = Commands(os.path.join(assets_dir, "extras.plus.cfg"))
	fn = os.path.join(project_dir, "encoded_data.py")
	with open(fn, 'wt', encoding="utf-8") as fh:
		fh.write("#!/usr/bin/python3\n")
		fh.write("# -*- coding: UTF-8 -*-\n")
		fh.write("# This file is auto-generated: DO NOT EDIT!\n")
		fh.write("\n")
		fh.write("from edit_cfg import LinesB64, CrcKey\n")
		fh.write("\n")

		## Basic
		fh.write("CONFIG_FILE = '/home/mks/klipper_config/printer.cfg'\n")


		## Factory default persistence
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetPersistenceB64(fh, 'RESET_CFG_PRO', fn_x4pro_upg)
		GetPersistenceB64(fh, 'RESET_CFG_PLUS', fn_x4plus_upg)

		## stepper_x / stepper_y / stepper_z ranges
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetKey(fh, 'X_MAX_PRO', "stepper_x", "position_max", fn_x4pro_upg )
		GetKey(fh, 'X_MAX_PLUS', "stepper_x", "position_max", fn_x4plus_upg )
		GetKey(fh, 'Y_DIR_PRO', "stepper_y", "dir_pin", fn_x4pro_upg )
		GetKey(fh, 'Y_DIR_PLUS', "stepper_y", "dir_pin", fn_x4plus_upg )
		GetKey(fh, 'Y_MIN_PRO', "stepper_y", "position_min", fn_x4pro_upg )
		GetKey(fh, 'Y_MIN_PLUS', "stepper_y", "position_min", fn_x4plus_upg )
		GetKey(fh, 'Y_STOP_PRO', "stepper_y", "position_endstop", fn_x4pro_upg )
		GetKey(fh, 'Y_STOP_PLUS', "stepper_y", "position_endstop", fn_x4plus_upg )
		GetKey(fh, 'Y_MAX_PRO', "stepper_y", "position_max", fn_x4pro_upg )
		GetKey(fh, 'Y_MAX_PLUS', "stepper_y", "position_max", fn_x4plus_upg )
		GetKey(fh, 'Z_MAX_PRO', "stepper_z", "position_max", fn_x4pro_upg )
		GetKey(fh, 'Z_MAX_PLUS', "stepper_z", "position_max", fn_x4plus_upg )

		## homing_override / gcode
		fh.write("\n")
		fh.write("# def:\t\tgrumat\n")
		fh.write("# upg:\t\tgrumat\n")
		fh.write("# grumat:\tY\n")
		GetCRC(fh, 'HOME_OVR_PRO_CRC', "homing_override", "gcode", fn_x4pro_grumat)
		GetKey(fh, 'HOME_OVR_PRO', "homing_override", "gcode", fn_x4pro_grumat)
		GetCRC(fh, 'HOME_OVR_PLUS_CRC', "homing_override", "gcode", fn_x4plus_grumat)
		GetKey(fh, 'HOME_OVR_PLUS', "homing_override", "gcode", fn_x4plus_grumat)

		## bed_mesh / mesh_max
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetKey(fh, 'MESH_MAX_PRO', "bed_mesh", "mesh_max", fn_x4pro_upg )
		GetKey(fh, 'MESH_MAX_PLUS', "bed_mesh", "mesh_max", fn_x4plus_upg )

		## gcode_macro G29 / gcode
		fh.write("\n")
		fh.write("# def:\t\tgrumat\n")
		fh.write("# upg:\t\tgrumat\n")
		fh.write("# grumat:\tY\n")
		GetCRC(fh, 'G29_PRO_CRC', "gcode_macro G29", "gcode", fn_x4pro_grumat )
		GetKey(fh, 'G29_PRO', "gcode_macro G29", "gcode", fn_x4pro_grumat)
		GetCRC(fh, 'G29_PLUS_CRC', "gcode_macro G29", "gcode", fn_x4plus_grumat )
		GetKey(fh, 'G29_PLUS', "gcode_macro G29", "gcode", fn_x4plus_grumat)

		## gcode_macro nozzle_wipe / gcode
		fh.write("\n")
		fh.write("# def:\t\tY\n")
		GetCRC(fh, 'WIPE_PRO_CRC_DEF', "gcode_macro nozzle_wipe", "gcode", fn_x4pro_def )
		GetKey(fh, 'WIPE_PRO_DEF', "gcode_macro nozzle_wipe", "gcode", fn_x4pro_def)
		GetCRC(fh, 'WIPE_PLUS_CRC_DEF', "gcode_macro nozzle_wipe", "gcode", fn_x4plus_def )
		GetKey(fh, 'WIPE_PLUS_DEF', "gcode_macro nozzle_wipe", "gcode", fn_x4plus_def)
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetCRC(fh, 'WIPE_PRO_CRC_UPG', "gcode_macro nozzle_wipe", "gcode", fn_x4pro_upg )
		GetKey(fh, 'WIPE_PRO_UPG', "gcode_macro nozzle_wipe", "gcode", fn_x4pro_upg)
		GetCRC(fh, 'WIPE_PLUS_CRC_UPG', "gcode_macro nozzle_wipe", "gcode", fn_x4plus_upg )
		GetKey(fh, 'WIPE_PLUS_UPG', "gcode_macro nozzle_wipe", "gcode", fn_x4plus_upg)

		## gcode_macro draw_line_only / gcode
		fh.write("\n")
		fh.write("# def:\t\tN\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetSecCRC(fh, 'LINE_ONLY_PRO_CRC_UPG', "gcode_macro draw_line_only", fn_x4pro_upg )
		GetSecML(fh, 'LINE_ONLY_PRO_UPG', "gcode_macro draw_line_only", fn_x4pro_upg)
		GetSecCRC(fh, 'LINE_ONLY_PRO_CRC_GRU', "gcode_macro draw_line_only", fn_x4pro_grumat )
		GetSecML(fh, 'LINE_ONLY_PRO_GRU', "gcode_macro draw_line_only", fn_x4pro_grumat)
		GetSecCRC(fh, 'LINE_ONLY_PLUS_CRC_UPG', "gcode_macro draw_line_only", fn_x4plus_upg )
		GetSecML(fh, 'LINE_ONLY_PLUS_UPG', "gcode_macro draw_line_only", fn_x4plus_upg)
		GetSecCRC(fh, 'LINE_ONLY_PLUS_CRC_GRU', "gcode_macro draw_line_only", fn_x4plus_grumat )
		GetSecML(fh, 'LINE_ONLY_PLUS_GRU', "gcode_macro draw_line_only", fn_x4plus_grumat)

		## gcode_macro draw_line / gcode
		fh.write("\n")
		fh.write("# def:\t\tY\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetCRC(fh, 'LINE_PRO_CRC_DEF', "gcode_macro draw_line", "gcode", fn_x4pro_def )
		GetKey(fh, 'LINE_PRO_DEF', "gcode_macro draw_line", "gcode", fn_x4pro_def )
		GetCRC(fh, 'LINE_PLUS_CRC_DEF', "gcode_macro draw_line", "gcode", fn_x4plus_def )
		GetKey(fh, 'LINE_PLUS_DEF', "gcode_macro draw_line", "gcode", fn_x4plus_def )
		GetCRC(fh, 'LINE_PRO_CRC_UPG', "gcode_macro draw_line", "gcode", fn_x4pro_upg )
		GetKey(fh, 'LINE_PRO_UPG', "gcode_macro draw_line", "gcode", fn_x4pro_upg )
		GetCRC(fh, 'LINE_PLUS_CRC_UPG', "gcode_macro draw_line", "gcode", fn_x4plus_upg )
		GetKey(fh, 'LINE_PLUS_UPG', "gcode_macro draw_line", "gcode", fn_x4plus_upg )

		## gcode_macro move_to_point_0 / gcode
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetCRC(fh, 'POINT0_PRO_CRC', "gcode_macro move_to_point_0", "gcode", fn_x4pro_upg )
		GetKey(fh, 'POINT0_PRO', "gcode_macro move_to_point_0", "gcode", fn_x4pro_upg)
		GetCRC(fh, 'POINT0_PLUS_CRC', "gcode_macro move_to_point_0", "gcode", fn_x4plus_upg )
		GetKey(fh, 'POINT0_PLUS', "gcode_macro move_to_point_0", "gcode", fn_x4plus_upg)

		## gcode_macro move_to_point_1 / gcode
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetCRC(fh, 'POINT1_PRO_CRC', "gcode_macro move_to_point_1", "gcode", fn_x4pro_upg )
		GetKey(fh, 'POINT1_PRO', "gcode_macro move_to_point_1", "gcode", fn_x4pro_upg)
		GetCRC(fh, 'POINT1_PLUS_CRC', "gcode_macro move_to_point_1", "gcode", fn_x4plus_upg )
		GetKey(fh, 'POINT1_PLUS', "gcode_macro move_to_point_1", "gcode", fn_x4plus_upg)

		## gcode_macro move_to_point_2 / gcode
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetCRC(fh, 'POINT2_PRO_CRC', "gcode_macro move_to_point_2", "gcode", fn_x4pro_upg )
		GetKey(fh, 'POINT2_PRO', "gcode_macro move_to_point_2", "gcode", fn_x4pro_upg)
		GetCRC(fh, 'POINT2_PLUS_CRC', "gcode_macro move_to_point_2", "gcode", fn_x4plus_upg )
		GetKey(fh, 'POINT2_PLUS', "gcode_macro move_to_point_2", "gcode", fn_x4plus_upg)

		## gcode_macro move_to_point_3 / gcode
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetCRC(fh, 'POINT3_PRO_CRC', "gcode_macro move_to_point_3", "gcode", fn_x4pro_upg )
		GetKey(fh, 'POINT3_PRO', "gcode_macro move_to_point_3", "gcode", fn_x4pro_upg)
		GetCRC(fh, 'POINT3_PLUS_CRC', "gcode_macro move_to_point_3", "gcode", fn_x4plus_upg )
		GetKey(fh, 'POINT3_PLUS', "gcode_macro move_to_point_3", "gcode", fn_x4plus_upg)

		## gcode_macro move_to_point_4 / gcode
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetSecCRC(fh, 'POINT4_PLUS_CRC', "gcode_macro move_to_point_4", fn_x4plus_upg )
		GetSecML(fh, 'POINT4_SEC_PLUS', "gcode_macro move_to_point_4", fn_x4plus_upg)

		## gcode_macro move_to_point_5 / gcode
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetSecCRC(fh, 'POINT5_PLUS_CRC', "gcode_macro move_to_point_5", fn_x4plus_upg )
		GetSecML(fh, 'POINT5_SEC_PLUS', "gcode_macro move_to_point_5", fn_x4plus_upg)

		## gcode_macro move_to_point_6 / gcode
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetSecCRC(fh, 'POINT6_PLUS_CRC', "gcode_macro move_to_point_6", fn_x4plus_upg )
		GetSecML(fh, 'POINT6_SEC_PLUS', "gcode_macro move_to_point_6", fn_x4plus_upg)

		## exclude_object
		fh.write("\n")
		fh.write("# def:\t\tN\n")
		fh.write("# upg:\t\tN\n")
		fh.write("# grumat:\tN\n")
		GetSecCRC(fh, 'EXCLUDE_OBJECT_CRC', "exclude_object", fn_x4pro_extra )
		GetSecML(fh, 'EXCLUDE_OBJECT', "exclude_object", fn_x4pro_extra )

		## tmc2209 stepper_z / hold_current
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		GetKey(fh, 'HOLD_CURRENT_Z_LOW', "tmc2209 stepper_z", "hold_current", fn_x4plus_upg )
		GetKey(fh, 'HOLD_CURRENT_Z_HI', "tmc2209 stepper_z", "hold_current", fn_x4pro_upg )

		##  extruder / max_extrude_only_accel
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		fh.write("EXTRUDER_ACCEL_LOW = '6000'\t\t\t\t\t\t# Plain value\n")
		fh.write("EXTRUDER_ACCEL_MID = '7000'\t\t\t\t\t\t# Plain value\n")
		fh.write("EXTRUDER_ACCEL_HI = '8000'\t\t\t\t\t\t# Plain value\n")

		##  tmc2209 extruder / run_current
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		fh.write("EXTRUDER_CURRENT_LOW = '0.8'\t\t\t\t\t# Plain value\n")
		fh.write("EXTRUDER_CURRENT_MID = '0.9'\t\t\t\t\t# Plain value\n")
		fh.write("EXTRUDER_CURRENT_HI = '1.0'\t\t\t\t\t\t# Plain value\n")

		##  probe
		fh.write("\n")
		fh.write("# def:\t\tupg\n")
		fh.write("# upg:\t\tY\n")
		fh.write("# grumat:\tupg\n")
		fh.write("PROBE_X_OFFSET = '-17'\t\t\t\t\t\t\t# Plain value\n")
		fh.write("PROBE_Y_OFFSET = '17'\t\t\t\t\t\t\t# Plain value\n")
		fh.write("PROBE_SPEED = '10.0'\t\t\t\t\t\t\t# Plain value\n")
		fh.write("PROBE_SAMPLE = '2'\t\t\t\t\t\t\t\t# Plain value\n")
		fh.write("PROBE_RESULT = 'average'\t\t\t\t\t\t# Plain value\n")
		fh.write("PROBE_TOLERANCE = '0.03'\t\t\t\t\t\t# Plain value\n")
		fh.write("PROBE_RETRIES = '3'\t\t\t\t\t\t\t\t# Plain value\n")

		##  probe 180
		fh.write("\n")
		fh.write("# def:\t\tgrumat\n")
		fh.write("# upg:\t\tgrumat\n")
		fh.write("# grumat:\tY\n")
		fh.write("PROBE180_X_OFFSET = '-18'\t\t\t\t\t\t# Plain value\n")
		fh.write("PROBE180_Y_OFFSET = '14'\t\t\t\t\t\t# Plain value\n")
		fh.write("PROBE180_SPEED = '3.0'\t\t\t\t\t\t\t# Plain value\n")
		fh.write("PROBE180_LIFT = '12.0'\t\t\t\t\t\t\t# Plain value\n")
		fh.write("PROBE180_SAMPLE = '4'\t\t\t\t\t\t\t# Plain value\n")
		fh.write("PROBE180_RESULT = 'median'\t\t\t\t\t\t# Plain value\n")
		fh.write("PROBE180_TOLERANCE = '0.028'\t\t\t\t\t# Plain value\n")
		fh.write("PROBE180_RETRIES = '5'\t\t\t\t\t\t\t# Plain value\n")

		##  screws_tilt_adjust
		fh.write("\n")
		fh.write("# def:\t\tN\n")
		fh.write("# upg:\t\tN\n")
		fh.write("# grumat:\tY\n")
		GetSecCRC(fh, 'SCREWS_PRO_CRC', "screws_tilt_adjust", fn_x4pro_extra )
		GetSecML(fh, 'SCREWS_PRO', "screws_tilt_adjust", fn_x4pro_extra)
		GetSecCRC(fh, 'SCREWS_PLUS_CRC', "screws_tilt_adjust", fn_x4plus_extra )
		GetSecML(fh, 'SCREWS_PLUS', "screws_tilt_adjust", fn_x4plus_extra)
		GetSecCRC(fh, 'SCREWS180_PRO_CRC', "screws_tilt_adjust", fn_x4pro_grumat )
		GetSecML(fh, 'SCREWS180_PRO', "screws_tilt_adjust", fn_x4pro_grumat)
		GetSecCRC(fh, 'SCREWS180_PLUS_CRC', "screws_tilt_adjust", fn_x4plus_grumat )
		GetSecML(fh, 'SCREWS180_PLUS', "screws_tilt_adjust", fn_x4plus_grumat)

		##  temperature_sensor
		fh.write("\n")
		fh.write("# def:\t\tN\n")
		fh.write("# upg:\t\tN\n")
		fh.write("# grumat:\tY\n")
		GetSecML(fh, 'HOST_TEMP', "temperature_sensor rpi_cpu", fn_x4pro_grumat)
		GetSecML(fh, 'MCU_TEMP', "temperature_sensor mcu_temp", fn_x4pro_grumat)

		##  M600 Support
		fh.write("\n")
		fh.write("# def:\t\tV1\n")
		fh.write("# upg:\t\tV1\n")
		fh.write("# grumat:\tV2\n")
		GetSecCRC(fh, 'BEEPER_CRC_UPG', "output_pin BEEPER_pin", fn_x4pro_upg )
		GetSecML(fh, 'BEEPER_UPG', "output_pin BEEPER_pin", fn_x4pro_upg )
		GetSecCRC(fh, 'M300_CRC_UPG', "gcode_macro M300", fn_x4pro_upg )
		GetSecML(fh, 'M300_UPG', "gcode_macro M300", fn_x4pro_upg )
		GetSecCRC(fh, 'M600_CRC_UPG', "gcode_macro M600", fn_x4pro_upg )
		GetSecML(fh, 'M600_UPG', "gcode_macro M600", fn_x4pro_upg )
		GetSecCRC(fh, 'M600_CRC_GRU', "gcode_macro M600", fn_x4pro_grumat )
		GetSecML(fh, 'M600_GRU', "gcode_macro M600", fn_x4pro_grumat )
		GetSecCRC(fh, 'T600_CRC_UPG', "gcode_macro T600", fn_x4pro_upg )
		GetSecML(fh, 'T600_UPG', "gcode_macro T600", fn_x4pro_upg )

		##  PAUSE Macro
		fh.write("\n")
		fh.write("# def:\t\tV1\n")
		fh.write("# upg:\t\tV2\n")
		fh.write("# grumat:\tV3\n")
		GetCRC(fh, 'PAUSE_CRC_DEF', "gcode_macro PAUSE", "gcode", fn_x4pro_def )
		GetKey(fh, 'PAUSE_DEF', "gcode_macro PAUSE", "gcode", fn_x4pro_def )
		GetCRC(fh, 'PAUSE_CRC_UPG', "gcode_macro PAUSE", "gcode", fn_x4pro_upg )
		GetKey(fh, 'PAUSE_UPG', "gcode_macro PAUSE", "gcode", fn_x4pro_upg )
		GetCRC(fh, 'PAUSE_CRC_GRU', "gcode_macro PAUSE", "gcode", fn_x4pro_grumat )
		GetKey(fh, 'PAUSE_GRU', "gcode_macro PAUSE", "gcode", fn_x4pro_grumat )

if __name__ == "__main__":
	main()
