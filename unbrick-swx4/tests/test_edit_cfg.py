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
	if isinstance(res, MultiLineData):
		print("  Expands to:")
		lines = res.GetLines()
		if len(lines) > 0:
			for l in lines:
				print(f"    {l}")
		else:
			print("    <empty list>")
	print("-------------------------")

def ValidateB64(cmd : Commands, method : str, args, cmp) -> None:
	res = _validate_(cmd, method, tuple(args), cmp)
	if res:
		# Expand base64 block
		lines = eval(DecodeB64(res))
		print("  Expands to:")
		if lines:
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

	ValidateB64(cmd, 'ListSectionsB64', ['no_no_no'], res_empty_list)
	ValidateB64(cmd, 'ListSectionsB64', ['include *'], res_empty_list)

	ValidateB64(cmd, 'ListSectionsB64', ['printer'], lambda res : str(res).endswith("fi7kinChINWnJ9A"))
	ValidateB64(cmd, 'ListSectionsB64', ['stepper_?'], lambda res : str(res).endswith("Kfi7kinChIXwJgQA="))
	ValidateB64(cmd, 'ListSectionsB64', ['*home*'], lambda res : str(res).endswith("PxdyRThQkMeZWQcA=="))	# spellchecker: disable-line

	Test_Close_()

def Test_ListKeys(cmd : Commands):
	Test_Begin_("ListKeys Test")

	ValidateB64(cmd, 'ListKeysB64', ['no_no_no'], res_empty_list)
	ValidateB64(cmd, 'ListKeysB64', ['pause_resume'], res_empty_list)

	ValidateB64(cmd, 'ListKeysB64', ['idle_timeout'], lambda res : str(res).endswith("Ckw78XckU4UJBy5xmeA=="))
	ValidateB64(cmd, 'ListKeysB64', ['gcode_macro nozzle_wipe'], lambda res : str(res).endswith("MLwVzkNRdyRThQkHCY3Xg="))
	ValidateB64(cmd, 'ListKeysB64', ['printer'], lambda res : str(res).endswith("KGRfxdyRThQkFz1CAAA="))	# spellchecker: disable-line

	Test_Close_()

def Test_ListKey(cmd : Commands):
	Test_Begin_("ListKey Test")
	Validate(cmd, 'ListKey', ['no_no_no', 'no_no_no'], None)

	Validate(cmd, 'ListKey', ['printer', 'kinematics'], KeyInfo('printer', 'kinematics', 266, True, False, '032E315C'))
	Validate(cmd, 'ListKey', ['gcode_macro G29', 'gcode'], KeyInfo('gcode_macro G29', 'gcode', 294, True, False, 'F8CEE4BF'))

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
	Validate(cmd, 'GetKey', ['homing_override', 'gcode'], lambda res : str(res).endswith("URVE/8XckU4UJClGFkcA"))	# spellchecker: disable-line
	Validate(cmd, 'GetKey', ['gcode_macro G29', 'gcode'], lambda res : str(res).endswith("Q0dMBdyRThQkAw3lao"))		# spellchecker: disable-line
	Validate(cmd, 'GetKey', ['gcode_macro M600', 'gcode'], lambda res : str(res).endswith("Kkqv/F3JFOFCQUtiz/QA=="))	# spellchecker: disable-line

	Test_Close_()

def Test_EditKey(cmd : Commands):
	Test_Begin_("EditKey Test")

	Validate(cmd, 'EditKey', ['no_no_no', 'no_no_no', '999'], None)
	Validate(cmd, 'EditKey', ['stepper_?', 'new_key', '999'], None)

	Validate(cmd, 'EditKey', ['stepper_z', 'endstop_pin', 'PROBE:Z_VIRTUAL_ENDSTOP'], True)
	Validate(cmd, 'GetKey', ['stepper_z', 'endstop_pin'], 'PROBE:Z_VIRTUAL_ENDSTOP')

	Validate(cmd, 'EditKey', ['stepper_x', 'full_steps_per_rotation', '201'], True)
	Validate(cmd, 'GetKey', ['stepper_x', 'full_steps_per_rotation'], '201')

	Validate(cmd, 'EditKey', ['gcode_macro M600', 'gcode', encoded_data.HOME_OVR_PRO], False)

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
	Validate(cmd, 'ListKey', ['gcode_macro G29', 'new_key'], KeyInfo('gcode_macro G29', 'new_key', 301, True, False, '9DF557ED'))

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

	Validate(cmd, 'ListSection', ['controller_fan mainboard_fan'], SectionInfo('controller_fan mainboard_fan', 243, True, True, '0DABA107'))
	Validate(cmd, 'RenSec', ['controller_fan mainboard_fan', 'controller_fan motherboard_fan'], True)
	Validate(cmd, 'ListSection', ['controller_fan mainboard_fan'], None)
	Validate(cmd, 'ListSection', ['controller_fan motherboard_fan'], SectionInfo('controller_fan motherboard_fan', 243, True, True, '4C733D2B'))

	Test_Checkpoint(cmd, 4)
	Test_Close_()

def Test_DelSec(cmd : Commands):
	Test_Begin_("DelSec Test")

	Validate(cmd, 'DelSec', ['no_no_no'], None)
	Validate(cmd, 'DelSec', ['stepper_?'], None)

	Validate(cmd, 'ListSection', ['neopixel my_neopixel'], SectionInfo('neopixel my_neopixel', 676, True, True, '1804619F'))
	Validate(cmd, 'DelSec', ['neopixel my_neopixel'], 674)
	Validate(cmd, 'ListSection', ['neopixel my_neopixel'], None)

	Validate(cmd, 'ListSection', ['probe'], SectionInfo('probe', 167, True, True, '6C3A1993'))
	Validate(cmd, 'DelSec', ['probe'], 165)
	Validate(cmd, 'ListSection', ['probe'], None)

	Test_Checkpoint(cmd, 5)
	Test_Close_()

def Test_ReadSec(cmd : Commands):
	Test_Begin_("ReadSec Test")

	ValidateB64(cmd, 'ReadSec', ['no_no_no'], None)

	ValidateB64(cmd, 'ReadSec', ['pause_resume'], lambda res : str(res).endswith("Jgq0EBHwu5IpwoSAecMju"))
	ValidateB64(cmd, 'ReadSec', ['input_shaper'], lambda res : str(res).endswith("UjajsfxdyRThQkEpxYmUA="))
	ValidateB64(cmd, 'ReadSec', ['extruder'], lambda res : str(res).endswith("TcnXHBKfYxf+LuSKcKEglExVSA"))

	Test_Close_()

def Test_AddSec(cmd : Commands):
#	top_section = edit_cfg.EncodeMultiLine(['[top]\n', 'success:1\n', '\n'])
#	bottom_section = edit_cfg.EncodeMultiLine(['[bottom]\n', 'success:1\n', '\n'])
#	mid_section = edit_cfg.EncodeMultiLine(['[after gcode_macro move_to_point_3]\n', 'success:1\n', '\n'])
#	Test_Begin_("AddSec Test")
#	Run(['AddSec'], "!ARG")
#	Run(['AddSec', 'abcdefg'], "!ARG")
#	Run(['AddSec', 'abcdefg', 'bad-data'], "!ENC")
#	Run(['AddSec', 'abcdefg', 'bad-data', 'extra-arg'], "!ARG+")
#	Run(['AddSec', 'abcdefg', top_section], "!SEC")
#
#	Run(['AddSec', '@top', top_section], ".OK")
#	Run(['AddSec', '@bottom', bottom_section], ".OK")
#	Run(['AddSec', 'gcode_macro move_to_point_3', mid_section], ".OK")

	Test_Close_()

def Test_OvrSec(cmd : Commands):
#	section1 = edit_cfg.EncodeMultiLine(['[new-top]\n', 'success:2\n', '\n'])
#	section2 = edit_cfg.EncodeMultiLine(['[tmc2209 extruder2]\n', 'bye_bye:1\n', '\n'])
	Test_Begin_("OvrSec Test")
#	Run(['OvrSec'], "!ARG")
#	Run(['OvrSec', 'abcdefg'], "!ARG")
#	Run(['OvrSec', 'abcdefg', 'bad-data'], "!ENC")
#	Run(['OvrSec', 'abcdefg', 'bad-data', 'extra-arg'], "!ARG+")
#	Run(['OvrSec', 'abcdefg', section1], "!SEC")
#
#	Run(['ListSec', 'gcode_arcs'], "=gcode_arcs @632 :7224E2B6")
#	Run(['OvrSec', 'gcode_arcs', section1], ".OK")
#	Run(['ListSec', 'gcode_arcs'], "!SEC")
#	Run(['ListSec', 'new-top'], "=new-top @633 :41A7D47C")
#
#	Run(['ListSec', 'tmc2209 extruder'], "=tmc2209 extruder @368 :77B0CB90")
#	Run(['OvrSec', 'tmc2209 extruder', section2], ".OK")
#	Run(['ListSec', 'tmc2209 extruder'], "!SEC")
#	Run(['ListSec', 'tmc2209 extruder2'], "=tmc2209 extruder2 @369 :A160D7EF")

	Test_Close_()

def Test_Persistence(cmd : Commands):
	Test_Begin_("Persistence Test")

#	Run(['cmd.GetPersistenceB64'], lambda res : str(res).endswith("POEsH+LuSKcKEh7KyHCgA=="))
#	Run(['Save', encoded_data.RESET_CFG_PLUS], ".OK")
#	Run(['cmd.GetPersistenceB64'], lambda res : str(res).endswith("Qk/+LuSKcKEhc2G8Eg="))

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
	#Test_AddSec(cmd)
	#Test_OvrSec(cmd)
	#Test_Persistence(cmd)

	print(f"TOTAL ERROR COUNT: {total_err_count}")

	sys.stdout = original_stdout

if __name__ == "__main__":
	main()
