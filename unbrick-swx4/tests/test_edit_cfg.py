#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# spellchecker: words gcode endstop EPCOS mainboard neopixel

import sys
import os
import shutil
import shlex
import types

from typing import TYPE_CHECKING

# Get the directory of the current script
current_dir = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
# Construct the path to the 'edit_cfg' library
lib_dir = os.path.normpath(os.path.join(current_dir, '..'))
# Construct the path to the 'assets' directory
assets_dir = os.path.normpath(os.path.join(lib_dir, 'assets'))
# File compare samples
results_dir = os.path.join(current_dir, 'results')

# Add the 'assets' directory to sys.path
sys.path.append(lib_dir)
sys.path.append(assets_dir)
# Now you can import helper_functions as if it were a module
if TYPE_CHECKING:
	from ..edit_cfg import *
	from .. import encoded_data
else:
	from edit_cfg import *
	import encoded_data

from test_utils import *

test_file = os.path.join(current_dir, 'test.cfg')

class Tee:
	def __init__(self, filepath, mode='wt'): # 'a' for append, 'w' for overwrite
		self.filepath = filepath
		self.mode = mode
		self.terminal = sys.stdout
		self.log_file = None # Will be opened when write is first called or explicitly

	def write(self, message):
		self.terminal.write(message) # Write to console
		if self.log_file is None:
			# Lazy open the file when the first message is written
			# This handles cases where the script might exit before any print
			try:
				self.log_file = open(self.filepath, self.mode, encoding="utf-8")
			except IOError as e:
				self.terminal.write(f"\nError opening log file {self.filepath}: {e}\n")
				self.log_file = None # Prevent further attempts if it fails
				return
		self.log_file.write(message) # Write to file

	def flush(self):
		# This flush method is essential for proper behavior, especially with interactive sessions
		self.terminal.flush()
		if self.log_file:
			self.log_file.flush()

	def close(self):
		if self.log_file:
			self.log_file.close()
			self.log_file = None


def MkCfgClone():
	"""Makes a clone of a configuration file, used for tests"""
	if os.path.exists(test_file):
		os.unlink(test_file)
	src_cfg = os.path.normpath(os.path.join(current_dir, 'test-reference.cfg'))
	shutil.copyfile(src_cfg, test_file)

err_count = 0
total_err_count = 0
def _validate_(cmd : Commands, method : str, args, cmp) -> str:
	global err_count
	# Prints command line
	cmdline = f"cmd.{method}{repr(args)}"
	print(f"Q: {cmdline}")
	# Run "method" with given arguments
	res = getattr(cmd, method)(*args)
	# Validation function?
	if isinstance(cmp, types.FunctionType):
		st : bool = cmp(res)
	elif isinstance(cmp, str):
		st : bool = (str(res).strip() == cmp)
	else:
		st = (res == cmp)
	# Print result
	if st:
		print(f"PASSED: {res}")
	else:
		print(f"FAILED: {res}")
		err_count += 1
	return res

def Validate(cmd : Commands, method : str, args, cmp) -> None:
	res = _validate_(cmd, method, tuple(args), cmp)
	lines = None
	if isinstance(res, LinesB64):
		lines = res.Extract()
	if isinstance(res, SectionInfoB64):
		lines = res.Extract()
	if isinstance(res, KeyInfoB64):
		lines = res.Extract()
	if isinstance(res, MultiLineData):
		lines = res.b64.Extract()
	if lines is not None:
		print("  Expands to:")
		if len(lines) > 0:
			for l in lines:
				print(f"    {l}")
		else:
			print("    <empty list>")
	print("-------------------------")

def Test_Begin_(name : str):
	global err_count
	print(" ____________________________________________________________________ ")
	print("|                                                                    |")
	print(f"=== {name} ===".center(70))
	print()
	err_count = 0

def Test_Checkpoint(cmd : Commands, idx : int):
	global err_count
	cmd.Save()
	print()
	ref = os.path.join(results_dir, f"test_edit_cfg-{idx:03}.cfg")
	if files_equal(cmd.fname, ref):
		print("PASSED: ", end='')
	else:
		print("FAILED: ", end='')
		err_count += 1
	print(f"Comparing '{cmd.fname}'\n        with '{ref}'",)

def Test_Close_():
	global total_err_count
	print()
	if err_count:
		print(f"######## TOTAL ERROR COUNT: {err_count} ########".center(70))
		total_err_count += err_count
	else:
		print("NO ERRORS".center(70))
	print("|____________________________________________________________________|")
	print()
	print()


res_empty_list = lambda res : str(res).endswith("KxdyRThQkB+mXYgA==")	# spellchecker: disable-line


def Test_ListSec(cmd : Commands):
	Test_Begin_("ListSectionsB64 Test")

	Validate(cmd, 'ListSectionsB64', ['no_no_no'], res_empty_list)
	Validate(cmd, 'ListSectionsB64', ['include *'], res_empty_list)

	Validate(cmd, 'ListSectionsB64', ['printer'], lambda res : str(res).endswith("xdyRThQkIRkQBs"))
	Validate(cmd, 'ListSectionsB64', ['stepper_?'], lambda res : str(res).endswith("X4u5IpwoSEsm4ee"))	# spellchecker: disable-line
	Validate(cmd, 'ListSectionsB64', ['*home*'], lambda res : str(res).endswith("u5IpwoSAevd+OA=="))	# spellchecker: disable-line

	Test_Close_()

def Test_ListKeys(cmd : Commands):
	Test_Begin_("ListKeys Test")

	Validate(cmd, 'ListKeysB64', ['no_no_no'], res_empty_list)
	Validate(cmd, 'ListKeysB64', ['pause_resume'], res_empty_list)

	Validate(cmd, 'ListKeysB64', ['idle_timeout'], lambda res : str(res).endswith("PxdyRThQkO6W9Ew="))		# spellchecker: disable-line
	Validate(cmd, 'ListKeysB64', ['gcode_macro nozzle_wipe'], lambda res : str(res).endswith("P8XckU4UJAIWKOg"))	# spellchecker: disable-line
	Validate(cmd, 'ListKeysB64', ['printer'], lambda res : str(res).endswith("Qu5IpwoSC9tKcCA"))			# spellchecker: disable-line

	Test_Close_()

def Test_ListKey(cmd : Commands):
	Test_Begin_("ListKey Test")
	Validate(cmd, 'ListKey', ['no_no_no', 'no_no_no'], None)

	Validate(cmd, 'ListKey', ['printer', 'kinematics'], KeyInfo('printer', 'kinematics', 266, True, False, CrcKey(0x032E315C)))
	Validate(cmd, 'ListKey', ['gcode_macro G29', 'gcode'], KeyInfo('gcode_macro G29', 'gcode', 294, True, False, CrcKey(0xF8CEE4BF)))

	Test_Close_()

def Test_GetKey(cmd : Commands):
	Test_Begin_("GetKey Test")

	Validate(cmd, 'GetKey', ['no_no_no', 'no_no_no'], None)
	Validate(cmd, 'GetKey', ['stepper_?', 'step_pin'], None)
	Validate(cmd, 'GetKey', ['stepper_x', 'no_no_no'], None)

	Validate(cmd, 'GetKey', ['stepper_x', 'step_pin'], "PC14")
	Validate(cmd, 'GetKey', ['stepper_x', 'enable_pin'], "!PC15")
	Validate(cmd, 'GetKey', ['stepper_x', 'step_pulse_duration'], "0.000002")
	Validate(cmd, 'GetKey', ['stepper_y', 'full_steps_per_rotation'], "200")
	Validate(cmd, 'GetKey', ['stepper_y', 'endstop_pin'], "tmc2209_stepper_y:virtual_endstop")
	Validate(cmd, 'GetKey', ['stepper_y', 'step_pulse_duration'], "0.000002")
	Validate(cmd, 'GetKey', ['extruder', 'sensor_type'], "EPCOS 100K B57560G104F")
	Validate(cmd, 'GetKey', ['homing_override', 'gcode'], lambda res : str(res).endswith("qif+LuSKcKEgfPVerg=="))	# spellchecker: disable-line
	Validate(cmd, 'GetKey', ['gcode_macro G29', 'gcode'], lambda res : str(res).endswith("Q0dMBdyRThQkAw3lao"))		# spellchecker: disable-line
	Validate(cmd, 'GetKey', ['gcode_macro M600', 'gcode'], lambda res : str(res).endswith("lV/4u5IpwoSAzd/lIA"))	# spellchecker: disable-line

	Test_Close_()

def Test_EditKey(cmd : Commands):
	Test_Begin_("EditKey Test")

	Validate(cmd, 'EditKey', ['no_no_no', 'no_no_no', '999'], None)
	Validate(cmd, 'EditKey', ['stepper_?', 'new_key', '999'], None)

	Validate(cmd, 'EditKey', ['stepper_z', 'endstop_pin', 'PROBE:Z_VIRTUAL_ENDSTOP'], True)
	Validate(cmd, 'GetKey', ['stepper_z', 'endstop_pin'], 'PROBE:Z_VIRTUAL_ENDSTOP')

	Validate(cmd, 'EditKey', ['stepper_x', 'full_steps_per_rotation', '201'], True)
	Validate(cmd, 'GetKey', ['stepper_x', 'full_steps_per_rotation'], '201')

	Validate(cmd, 'EditKey', ['homing_override', 'gcode', encoded_data.HOME_OVR_PRO], False)

	Validate(cmd, 'GetKey', ['stepper_z', 'new_key'], None)
	Validate(cmd, 'EditKey', ['stepper_z', 'new_key', '999'], True)
	Validate(cmd, 'GetKey', ['stepper_z', 'new_key'], '999')

	Test_Checkpoint(cmd, 1)
	Test_Close_()

def Test_EditKeyML(cmd : Commands):
	Test_Begin_("EditKeyML Test")

	Validate(cmd, 'EditKeyML', ['no_no_no', 'no_no_no', encoded_data.G29_PLUS], None)
	Validate(cmd, 'EditKeyML', ['gcode_macro *', 'new_key', encoded_data.G29_PRO], None)

	Validate(cmd, 'ListKey', ['gcode_macro G29', 'gcode'], KeyInfo('gcode_macro G29', 'gcode', 295, True, False, encoded_data.G29_PRO_CRC))
	Validate(cmd, 'EditKeyML', ['gcode_macro G29', 'gcode', encoded_data.G29_PLUS], True)
	Validate(cmd, 'ListKey', ['gcode_macro G29', 'gcode'], KeyInfo('gcode_macro G29', 'gcode', 295, True, False, encoded_data.G29_PLUS_CRC))

	Validate(cmd, 'ListKey', ['gcode_macro G29', 'new_key'], None)
	Validate(cmd, 'EditKeyML', ['gcode_macro G29', 'new_key', encoded_data.G29_PRO], True)
	Validate(cmd, 'ListKey', ['gcode_macro G29', 'new_key'], KeyInfo('gcode_macro G29', 'new_key', 301, True, False, CrcKey(0x9DF557ED)))

	Test_Checkpoint(cmd, 2)
	Test_Close_()

def Test_DelKey(cmd : Commands):
	Test_Begin_("DelKey Test")

	Validate(cmd, 'DelKey', ['no_no_no', 'no_no_no'], None)
	Validate(cmd, 'DelKey', ['stepper_?', 'position_max'], None)

	Validate(cmd, 'DelKey', ['stepper_z', 'new_key'], True)
	Validate(cmd, 'GetKey', ['stepper_z', 'new_key'], None)

	Validate(cmd, 'DelKey', ['gcode_macro G29', 'new_key'], True)
	Validate(cmd, 'GetKey', ['gcode_macro G29', 'new_key'], None)

	Test_Checkpoint(cmd, 3)
	Test_Close_()

def Test_RenSec(cmd : Commands):
	Test_Begin_("RenSec Test")

	Validate(cmd, 'RenSec', ['no_no_no', 'abcdefg'], None)
	Validate(cmd, 'RenSec', ['stepper_?', 'abcdefg'], None)

	Validate(cmd, 'ListSection', ['controller_fan mainboard_fan'], SectionInfo('controller_fan mainboard_fan', 243, True, True, CrcKey(0x0DABA107)))
	Validate(cmd, 'RenSec', ['controller_fan mainboard_fan', 'controller_fan motherboard_fan'], True)
	Validate(cmd, 'ListSection', ['controller_fan mainboard_fan'], None)
	Validate(cmd, 'ListSection', ['controller_fan motherboard_fan'], SectionInfo('controller_fan motherboard_fan', 243, True, True, CrcKey(0x4C733D2B)))

	Test_Checkpoint(cmd, 4)
	Test_Close_()

def Test_DelSec(cmd : Commands):
	Test_Begin_("DelSec Test")

	Validate(cmd, 'DelSec', ['no_no_no'], None)
	Validate(cmd, 'DelSec', ['stepper_?'], None)

	Validate(cmd, 'ListSection', ['neopixel my_neopixel'], SectionInfo('neopixel my_neopixel', 676, True, True, CrcKey(0x1804619F)))
	Validate(cmd, 'DelSec', ['neopixel my_neopixel'], 674)
	Validate(cmd, 'ListSection', ['neopixel my_neopixel'], None)

	Validate(cmd, 'ListSection', ['probe'], SectionInfo('probe', 167, True, True, CrcKey(0x6C3A1993)))
	Validate(cmd, 'DelSec', ['probe'], 165)
	Validate(cmd, 'ListSection', ['probe'], None)

	Test_Checkpoint(cmd, 5)
	Test_Close_()

def Test_ReadSec(cmd : Commands):
	Test_Begin_("ReadSec Test")

	Validate(cmd, 'ReadSec', ['no_no_no'], None)

	Validate(cmd, 'ReadSec', ['pause_resume'], lambda res : str(res).endswith("Jgq0EBHwu5IpwoSAecMju"))	# spellchecker: disable-line
	Validate(cmd, 'ReadSec', ['input_shaper'], lambda res : str(res).endswith("UjajsfxdyRThQkEpxYmUA="))	# spellchecker: disable-line
	Validate(cmd, 'ReadSec', ['extruder'], lambda res : str(res).endswith("TcnXHBKfYxf+LuSKcKEglExVSA"))

	Test_Close_()

def Test_AddSec(cmd : Commands):
	top_section = LinesB64(Contents(['\n', '[top]\n', 'success:1\n']).sections[0].lines)
	bottom_section = LinesB64(Contents(['\n', '[bottom]\n', 'success:1\n']).sections[0].lines)
	mid_section = LinesB64(Contents(['\n', '[after homing_override]\n', 'success:1\n']).sections[0].lines)
	split_section = LinesB64(Contents(['\n', '[extruder]\n', 'control :pid\n', 'pid_kp : 26.213\n', 'pid_ki : 1.304\n', 'pid_kd : 131.721\n', 'intruder : 1\n']).sections[0].lines)

	Test_Begin_("AddSec Test")

	Validate(cmd, 'ListSection', ['extruder'], SectionInfo('extruder', 56, True, True, CrcKey(0x12529D87)))

	Validate(cmd, 'AddSec', [0, top_section], None)
	Validate(cmd, 'AddSec', [-1, bottom_section], None)
	Validate(cmd, 'AddSec', [100, mid_section], None)
	Validate(cmd, 'AddSec', ['heater_bed', split_section], None)

	Validate(cmd, 'ListSection', ['top'], SectionInfo('top', 6, True, True, CrcKey(0x96FBD474)))
	Validate(cmd, 'ListSection', ['after homing_override'], SectionInfo('after homing_override', 164, True, True, CrcKey(0x488DF9FB)))
	Validate(cmd, 'ListSection', ['bottom'], SectionInfo('bottom', 781, True, True, CrcKey(0x11427BAD)))
	Validate(cmd, 'ListSection', ['extruder'], SectionInfo('extruder', 59, True, True, CrcKey(0xC48D84C3)))
	Validate(cmd, 'GetKey', ['extruder', 'intruder'], "1")

	Test_Checkpoint(cmd, 6)
	Test_Close_()

def Test_OvrSec(cmd : Commands):
	section1 = LinesB64(Contents(['\n', '[new-top]\n', 'success:2\n']).sections[0].lines)
	section2 = LinesB64(Contents(['\n', '[extruder2]\n', 'bye_bye:1\n']).sections[0].lines)
	Test_Begin_("OvrSec Test")

	Validate(cmd, 'OvrSec', ['no_no_no', section1], False)

	Validate(cmd, 'OvrSec', ['top', section1], True)
	Validate(cmd, 'ListSection', ['top'], None)
	Validate(cmd, 'ListSection', ['new-top'], SectionInfo('new-top', 6, True, True, CrcKey(0x89002721)))
	Validate(cmd, 'GetKey', ['new-top', 'success'], "2")

	Validate(cmd, 'OvrSec', ['extruder', section2], True)
	Validate(cmd, 'ListSection', ['extruder'], None)
	Validate(cmd, 'ListSection', ['extruder2'], SectionInfo('extruder2', 59, True, True, CrcKey(0x36F82B6E)))
	Validate(cmd, 'GetKey', ['extruder2', 'bye_bye'], "1")

	Test_Checkpoint(cmd, 7)
	Test_Close_()

def Test_Persistence(cmd : Commands):
	Test_Begin_("Persistence Test")

	Validate(cmd, 'GetPersistenceB64', [], lambda res : str(res).endswith("CPAf8XckU4UJAuPxkB"))
	Validate(cmd, 'SavePersistenceB64', [encoded_data.RESET_CFG_PLUS], None)
	Validate(cmd, 'GetPersistenceB64', [], lambda res : str(res).endswith("Ng2osw1f2LuSKcKEgK1Qy8A="))

	Test_Checkpoint(cmd, 8)
	Test_Close_()


def main():
	global total_err_count
	MkCfgClone()
	original_stdout = sys.stdout
	sys.stdout = Tee(os.path.join(current_dir, 'test_edit_cfg.log'))
	cmd = Commands(test_file)
	Test_ListSec(cmd)
	Test_ListKeys(cmd)
	Test_ListKey(cmd)
	Test_GetKey(cmd)
	Test_EditKey(cmd)
	Test_EditKeyML(cmd)
	Test_DelKey(cmd)
	Test_RenSec(cmd)
	Test_DelSec(cmd)
	Test_ReadSec(cmd)
	Test_AddSec(cmd)
	Test_OvrSec(cmd)
	Test_Persistence(cmd)

	print(f"TOTAL ERROR COUNT: {total_err_count}")

	sys.stdout = original_stdout

if __name__ == "__main__":
	main()
