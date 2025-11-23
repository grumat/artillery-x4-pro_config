#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# spellchecker: words gcode endstop EPCOS mainboard neopixel

import sys
import os
import shutil
import shlex
import types

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
import edit_cfg		# type: ignore
import encoded_data

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
def Run(args : list[str], cmp, fname : str | None = None) -> None:
	global err_count
	# Prints command line
	cmdline = ' '.join(shlex.quote(a) for a in args)
	print(f"Q: {cmdline}")
	# Use a local test file
	args.append(fname or test_file)
	# Run "editor" with arguments
	res = edit_cfg.main(args)
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
	# Expand base64 block
	if res.IsBase64():
		lines = edit_cfg.DecodeMultiLine(res.value)
		print("Expands to:")
		for l in lines:
			print(l, end='')
	
	print("-------------------------")

def Test_Begin_(name : str):
	global err_count
	print(" ____________________________________________________________________ ")
	print("|                                                                    |")
	print(f"=== {name} ===".center(70))
	print()
	err_count = 0

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

def Test_ListSec():
	Test_Begin_("ListSec Test")
	Run(['ListSec'], "!ARG")
	Run(['ListSec', 'abcdefg'], "!SEC")
	Run(['ListSec', 'abcdefg', 'extra-arg'], "!ARG+")

	Run(['ListSec', 'printer'], "=printer @264 :2098A795")
	Run(['ListSec', 'include *'], lambda res : str(res).endswith("fi7kinChIfuiecA=")) # spellchecker: disable-line
	Run(['ListSec', 'stepper_?'], lambda res : str(res).endswith("fi7kinChIS/zd5A="))

	Test_Close_()

def Test_ListKeys():
	Test_Begin_("ListKeys Test")
	Run(['ListKeys'], "!ARG")
	Run(['ListKeys', 'abcdefg'], "!SEC")
	Run(['ListKeys', 'abcdefg', 'extra-arg'], "!ARG+")

	Run(['ListKeys', 'pause_resume'], "!KEY")
	Run(['ListKeys', 'idle_timeout'], "=timeout @284 :58D59594")
	Run(['ListKeys', 'gcode_macro nozzle_wipe'], "=gcode @408 :B77EDF4D")
	Run(['ListKeys', 'printer'], lambda res : str(res).endswith("IpwoSAtX0ksA==")) # spellchecker: disable-line

	Test_Close_()

def Test_GetKey():
	Test_Begin_("GetKey Test")
	Run(['GetKey'], "!ARG")
	Run(['GetKey', 'stepper_x'], "!ARG")
	Run(['GetKey', 'stepper_x', 'no_key'], "!KEY")
	Run(['GetKey', 'no_no_no', 'no_key'], "!SEC")
	Run(['GetKey', 'no_no_no', 'no_key', 'extra-arg'], "!ARG+")

	Run(['GetKey', 'stepper_x', 'step_pin'], "=PC14")
	Run(['GetKey', 'stepper_x', 'enable_pin'], "=!PC15")
	Run(['GetKey', 'stepper_x', 'step_pulse_duration'], "=0.000002")
	Run(['GetKey', 'stepper_y', 'full_steps_per_rotation'], "=200")
	Run(['GetKey', 'stepper_y', 'endstop_pin'], "=tmc2209_stepper_y:virtual_endstop")
	Run(['GetKey', 'stepper_y', 'step_pulse_duration'], "=0.000002")
	Run(['GetKey', 'extruder', 'sensor_type'], "=EPCOS 100K B57560G104F")
	Run(['GetKey', 'homing_override', 'gcode'], lambda res : str(res).endswith("i7kinChITWZTlAA="))	# spellchecker: disable-line
	Run(['GetKey', 'gcode_macro G29', 'gcode'], lambda res : str(res).endswith("x+LuSKcKEg5WYIZg"))	# spellchecker: disable-line
	Run(['GetKey', 'gcode_macro M600', 'gcode'], lambda res : str(res).endswith("uSKcKEgn29ApA=="))	# spellchecker: disable-line

	Run(['GetKey', 'stepper_?', 'step_pin'], "!SEC+")

	Test_Close_()

def Test_EditKey():
	Test_Begin_("EditKey Test")
	Run(['EditKey'], "!ARG")
	Run(['EditKey', 'stepper_z'], "!ARG")
	Run(['EditKey', 'stepper_z', 'endstop_pin'], "!ARG")
	Run(['EditKey', 'no_no_no', 'no_key', '999'], "!SEC")
	Run(['EditKey', 'no_no_no', 'no_key', '999', 'extra-arg'], "!ARG+")

	Run(['EditKey', 'stepper_z', 'endstop_pin', 'PROBE:Z_VIRTUAL_ENDSTOP'], ".OK")
	Run(['GetKey', 'stepper_z', 'endstop_pin'], "=PROBE:Z_VIRTUAL_ENDSTOP")
	Run(['EditKey', 'stepper_x', 'full_steps_per_rotation', '201'], ".OK")
	Run(['GetKey', 'stepper_x', 'full_steps_per_rotation'], "=201")
	Run(['EditKey', 'gcode_macro M600', 'gcode', encoded_data.M600], "!ML")

	Run(['GetKey', 'stepper_z', 'new_key'], "!KEY")
	Run(['EditKey', 'stepper_z', 'new_key', '999'], ".OK")
	Run(['GetKey', 'stepper_z', 'new_key'], "=999")

	Run(['EditKey', 'stepper_?', 'new_key', '999'], "!SEC+")

	Test_Close_()

def Test_EditKeyML():
	Test_Begin_("EditKeyML Test")
	Run(['EditKeyML'], "!ARG")
	Run(['EditKeyML', 'stepper_z'], "!ARG")
	Run(['EditKeyML', 'stepper_z', 'endstop_pin'], "!ARG")
	Run(['EditKeyML', 'no_no_no', 'no_key', '999'], "!ENC")
	Run(['EditKeyML', 'no_no_no', 'no_key', encoded_data.M600], "!SEC")
	Run(['EditKeyML', 'no_no_no', 'no_key', encoded_data.M600, 'extra-arg'], "!ARG+")

	Run(['EditKeyML', 'gcode_macro M600', 'gcode', encoded_data.M600], ".OK")
	Run(['GetKey', 'gcode_macro M600', 'gcode'], lambda res : str(res).endswith("/F3JFOFCQ39ObeQ"))	# spellchecker: disable-line

	Run(['GetKey', 'gcode_macro M600', 'new_key'], "!KEY")
	Run(['EditKeyML', 'gcode_macro M600', 'new_key', encoded_data.M600], ".OK")
	Run(['GetKey', 'gcode_macro M600', 'new_key'], lambda res : str(res).endswith("/F3JFOFCQ39ObeQ"))	# spellchecker: disable-line

	Run(['EditKeyML', 'gcode_macro *', 'new_key', encoded_data.M600], "!SEC+")

	Test_Close_()

def Test_DelKey():
	Test_Begin_("DelKey Test")
	Run(['DelKey'], "!ARG")
	Run(['DelKey', 'gcode_macro move_to_point_3'], "!ARG")
	Run(['DelKey', 'gcode_macro move_to_point_3', 'abcd'], "!KEY")
	Run(['DelKey', 'abcdefg', 'abcd'], "!SEC")
	Run(['DelKey', 'abcdefg', 'abcd', 'extra-arg'], "!ARG+")

	Run(['GetKey', 'stepper_z', 'homing_speed'], "=20")
	Run(['DelKey', 'stepper_z', 'new_key'], ".OK")
	Run(['GetKey', 'stepper_z', 'new_key'], "!KEY")
	Run(['GetKey', 'stepper_z', 'homing_speed'], "=20")

	Run(['DelKey', 'gcode_macro M600', 'new_key'], ".OK")
	Run(['GetKey', 'gcode_macro M600', 'new_key'], "!KEY")

	Run(['GetKey', 'stepper_?', 'position_max'], "!SEC+")

	Test_Close_()

def Test_RenSec():
	Test_Begin_("RenSec Test")
	Run(['RenSec'], "!ARG")
	Run(['RenSec', 'abcdefg'], "!ARG")
	Run(['RenSec', 'abcdefg', 'defgh'], "!SEC")					# spellchecker: disable-line
	Run(['RenSec', 'abcdefg', 'defgh', 'extra-arg'], "!ARG+") 	# spellchecker: disable-line

	Run(['ListSec', 'controller_fan mainboard_fan'], "=controller_fan mainboard_fan @242 :9971A484")
	Run(['RenSec', 'controller_fan mainboard_fan', 'controller_fan motherboard_fan'], ".OK")
	Run(['ListSec', 'controller_fan mainboard_fan'], "!SEC")
	Run(['ListSec', 'controller_fan motherboard_fan'], "=controller_fan motherboard_fan @242 :97664E5B")

	Run(['RenSec', 'stepper_?', 'abcdefgh'], "!SEC+")

	Test_Close_()

def Test_DelSec():
	Test_Begin_("DelSec Test")
	Run(['DelSec'], "!ARG")
	Run(['DelSec', 'abcdefg'], "!SEC")
	Run(['DelSec', 'abcdefg', 'extra-arg'], "!ARG+")
	Run(['DelSec', '@9999'], "!RANGE")

	Run(['ListSec', 'neopixel my_neopixel'], "=neopixel my_neopixel @648 :60C51F9E")
	Run(['DelSec', 'neopixel my_neopixel'], ".OK")
	Run(['ListSec', 'neopixel my_neopixel'], "!SEC")

	Run(['DelSec', 'stepper_?'], "!SEC+")

	Run(['ListSec', 'probe'], "=probe @166 :014F644B")
	Run(['DelSec', '@166'], ".OK")
	Run(['ListSec', 'probe'], "!SEC")

	Test_Close_()

def Test_ReadSec():
	Test_Begin_("ReadSec Test")
	Run(['ReadSec'], "!ARG")
	Run(['ReadSec', 'abcdefg'], "!SEC")
	Run(['ReadSec', 'abcdefg', 'extra-arg'], "!ARG+")
	Run(['ReadSec', '@9999'], "!RANGE")

	Run(['ReadSec', 'pause_resume'], lambda res : str(res).endswith("7xdyRThQkEjA7v4A=="))
	Run(['ReadSec', 'input_shaper'], lambda res : str(res).endswith("RThQkBAC6zkA=="))
	Run(['ReadSec', 'extruder'], lambda res : str(res).endswith("4u5IpwoSD5i+UKA==")) # spellchecker: disable-line

	Run(['ReadSec', '@464'], lambda res : str(res).endswith("5IpwoSFd2ewqA=")) # spellchecker: disable-line

	Test_Close_()

def Test_AddSec():
	top_section = edit_cfg.EncodeMultiLine(['[top]\n', 'success:1\n', '\n'])
	bottom_section = edit_cfg.EncodeMultiLine(['[bottom]\n', 'success:1\n', '\n'])
	mid_section = edit_cfg.EncodeMultiLine(['[after gcode_macro move_to_point_3]\n', 'success:1\n', '\n'])
	Test_Begin_("AddSec Test")
	Run(['AddSec'], "!ARG")
	Run(['AddSec', 'abcdefg'], "!ARG")
	Run(['AddSec', 'abcdefg', 'bad-data'], "!ENC")
	Run(['AddSec', 'abcdefg', 'bad-data', 'extra-arg'], "!ARG+")
	Run(['AddSec', 'abcdefg', top_section], "!SEC")

	Run(['AddSec', '@top', top_section], ".OK")
	Run(['AddSec', '@bottom', bottom_section], ".OK")
	Run(['AddSec', 'gcode_macro move_to_point_3', mid_section], ".OK")

	Test_Close_()

def Test_OvrSec():
	section1 = edit_cfg.EncodeMultiLine(['[new-top]\n', 'success:2\n', '\n'])
	section2 = edit_cfg.EncodeMultiLine(['[tmc2209 extruder2]\n', 'bye_bye:1\n', '\n'])
	Test_Begin_("OvrSec Test")
	Run(['OvrSec'], "!ARG")
	Run(['OvrSec', 'abcdefg'], "!ARG")
	Run(['OvrSec', 'abcdefg', 'bad-data'], "!ENC")
	Run(['OvrSec', 'abcdefg', 'bad-data', 'extra-arg'], "!ARG+")
	Run(['OvrSec', 'abcdefg', section1], "!SEC")

	Run(['ListSec', 'gcode_arcs'], "=gcode_arcs @632 :7224E2B6")
	Run(['OvrSec', 'gcode_arcs', section1], ".OK")
	Run(['ListSec', 'gcode_arcs'], "!SEC")
	Run(['ListSec', 'new-top'], "=new-top @633 :41A7D47C")

	Run(['ListSec', 'tmc2209 extruder'], "=tmc2209 extruder @368 :77B0CB90")
	Run(['OvrSec', 'tmc2209 extruder', section2], ".OK")
	Run(['ListSec', 'tmc2209 extruder'], "!SEC")
	Run(['ListSec', 'tmc2209 extruder2'], "=tmc2209 extruder2 @369 :A160D7EF")

	Test_Close_()

def Test_Persistence():
	Test_Begin_("Persistence Test")

	Run(['GetSave'], lambda res : str(res).endswith("POEsH+LuSKcKEh7KyHCgA=="))
	Run(['Save', encoded_data.RESET_CFG_SWX4_PLUS], ".OK")
	Run(['GetSave'], lambda res : str(res).endswith("Qk/+LuSKcKEhc2G8Eg="))

	Test_Close_()


def main():
	global total_err_count
	MkCfgClone()
	original_stdout = sys.stdout
	sys.stdout = Tee(os.path.join(current_dir, 'test_edit_cfg.log'))
	Test_ListSec()
	Test_ListKeys()
	Test_GetKey()
	Test_EditKey()
	Test_EditKeyML()
	Test_DelKey()
	Test_RenSec()
	Test_DelSec()
	Test_ReadSec()
	Test_AddSec()
	Test_OvrSec()
	Test_Persistence()

	print(f"TOTAL ERROR COUNT: {total_err_count}")

	sys.stdout = original_stdout

if __name__ == "__main__":
	main()
