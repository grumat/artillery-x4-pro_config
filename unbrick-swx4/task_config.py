#
# -*- coding: UTF-8 -*-
#
# Spellchecker: words USWX klipper gcode endstop filt


import os
import shutil
import re
import shlex
from datetime import datetime
from typing import TYPE_CHECKING, Callable, Any

TEST_MODE = os.getenv("USWX4_TEST")

if TYPE_CHECKING:
	from .my_env import GetBackupFolder, GetAssetsFolder, Debug
	from .i18n import _, N_
	from .edit_cfg import EditConfig
	from .encoded_data import *
	from .my_workflow import Task, TaskState, Workflow # type: ignore
else:
	from my_env import GetBackupFolder, GetAssetsFolder, Debug
	from i18n import _, N_
	from edit_cfg import EditConfig
	from encoded_data import *
	from my_workflow import Task, TaskState, Workflow # type: ignore


class EditConfig_(Task):
	def __init__(self, workflow : Workflow, label : str, state : TaskState) -> None:
		super().__init__(workflow, label, state)
		self.work_folder = GetBackupFolder()
		self.target = os.path.join(self.work_folder, 'printer.cfg')
	def Do(self):
		super().Do()
		if not os.path.isdir(self.work_folder):
			os.makedirs(self.work_folder)
	def Validate(self):
		# File that is edited is here
		if not os.path.isfile(self.target):
			raise Exception(_("Cannot find the copy of te configuration file!"))
	def GetLine(self, cmd_line : list[str]) -> str:
		cmd_line.append(self.target)
		res = EditConfig(cmd_line)
		if res.IsString() and isinstance(res.value, str):
			return res.value
		raise Exception(f"{res}")
	def GetKey(self, section : str, key : str) -> str | None:
		res = EditConfig(["GetKey", section, key, self.target])
		if res.IsString() and isinstance(res.value, str):
			return res.value
		return None
	def EditKey(self, section : str, key : str, value : str) -> None:
		EditConfig(["EditKey", section, key, value, self.target])
	def EditKeyML(self, section : str, key : str, value : str) -> None:
		EditConfig(["EditKeyML", section, key, value, self.target])
	def GetCRC(self, section : str, key : str) -> str | None:
		res = EditConfig(["ListKey", section, key, self.target])
		if res.IsString():
			return res.GetSingleKeyList().crc
		return None

class BackupConfig(EditConfig_):
	def __init__(self, workflow : Workflow) -> None:
		super().__init__(workflow, N_("Backup Current Configuration"), TaskState.READY)
	def Do(self):
		workflow = self.workflow
		if TEST_MODE is None:
			if workflow.sftp is None:
				raise Exception(N_("Connection is invalid to complete the command!"))
		super().Do()
		if TEST_MODE is None:
			backup = os.path.join(self.work_folder, datetime.now().strftime('printer_%Y%m%d-%H%M%S.cfg'))
			Debug(f"SFTP /home/mks/klipper_config/printer.cfg '{self.work_folder}'")
			workflow.SftpGet('/home/mks/klipper_config/printer.cfg', self.work_folder)
			self.Info(_("\n\tSuccessfully copy file '{}'").format('/home/mks/klipper_config/printer.cfg'))
			if os.path.isfile(backup):
				os.unlink(backup)
			Debug(f"copy '{self.work_folder}' '{backup}'")
			shutil.copyfile(self.work_folder, backup)
			self.Info(_("\n\tCreated a backup in '{}'\n").format(backup))
		else:
			if os.path.isfile(self.target):
				os.unlink(self.target)
			src = os.path.join(GetAssetsFolder(), "artillery_X4_pro.upg.cfg")
			shutil.copyfile(src, self.target)


class ConfigReset(EditConfig_):
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Reset Printer Configuration"), workflow.opts.reset and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		# Validate state
		if workflow.opts.reset == 0:
			raise Exception("This item is disabled, why got called?")
		super().Do()
		super().Validate()
		# Calibration
		cal = None
		# Reset calibration only
		if workflow.opts.reset == 1:
			if workflow.opts.IsArtillerySWX4Pro():
				cal = RESET_CFG_PRO
			else:
				cal = RESET_CFG_PLUS
		# Reset settings, but preserve calibration
		if workflow.opts.reset == 2:
			res = EditConfig(["GetSave", self.target])
			if res.code != '*':
				raise Exception(f"{res}")
			if not isinstance(res.value, str):
				raise ValueError("Data type value is unexpected")
			cal = res.value
		# Reset settings to factory default
		if workflow.opts.reset in (2, 3):
			# Use the latest Artillery upgrade file, according to printer model
			if workflow.opts.IsArtillerySWX4Pro():
				source = os.path.join(GetAssetsFolder(), 'artillery_X4_pro.upg.cfg')
			else:
				source = os.path.join(GetAssetsFolder(), 'artillery_X4_plus.upg.cfg')
			# Replace current settings file
			os.unlink(self.target)
			shutil.copyfile(source, self.target)
		# Apply calibration
		if cal is not None:
			res = EditConfig(["Save", cal, self.target])


class K(object):
	def __init__(self, section : str, key : str) -> None:
		self.section = section
		self.key = key

_stepper_x_max = K("stepper_x", "position_max")
_stepper_y_max = K("stepper_y", "position_max")
_stepper_y_dir = K("stepper_y", "dir_pin")
_stepper_y_min = K("stepper_y", "position_min")
_stepper_y_stop = K("stepper_y", "position_endstop")
_stepper_z_max = K("stepper_z", "position_max")
_gcode_homing_ = K("homing_override", "gcode")
_gcode_line_ = K("gcode_macro draw_line", "gcode")
_bed_mesh_max_ = K("bed_mesh", "mesh_max")
_gcode_G29_ = K("gcode_macro G29", "gcode")
_gcode_wipe = K("gcode_macro nozzle_wipe", "gcode")
_gcode_line_only = K("gcode_macro draw_line_only", "gcode")
_gcode_point_0_ = K("gcode_macro move_to_point_0", "gcode")
_gcode_point_1_ = K("gcode_macro move_to_point_1", "gcode")
_gcode_point_2_ = K("gcode_macro move_to_point_2", "gcode")
_gcode_point_3_ = K("gcode_macro move_to_point_3", "gcode")
_gcode_point_4_ = K("gcode_macro move_to_point_4", "gcode")
_gcode_point_5_ = K("gcode_macro move_to_point_5", "gcode")
_gcode_point_6_ = K("gcode_macro move_to_point_6", "gcode")

STORE = {}

def _get_var_(key : str):
	if key not in STORE:
		raise RuntimeError("variable not present")
		return STORE[key]
def _set_var_(key : str, value):
	STORE[key] = value
def _always_():
	return True
def _is_upg_():
	return _get_var_("UPG") != False
def _is_def_():
	return _get_var_("UPG") == False

def _set_key_(location : K, value : str, fname : str) -> None:
	cmd_line = ["EditKey", location.section, location.key, value, fname]
	Debug(" ".join([shlex.quote(t) for t in cmd_line]))
	EditConfig(cmd_line)

def _set_key_ml_(location : K, value : str, fname : str):
	cmd_line = ["EditKeyML", location.section, location.key, value, fname]
	Debug(" ".join([shlex.quote(t) for t in cmd_line]))
	res = EditConfig(cmd_line)
	Debug('  ' + str(res))

def _get_key_ne_(location : K, value : str, fname : str):
	cmd_line = ["GetKey", location.section, location.key, fname]
	Debug(" ".join([shlex.quote(t) for t in cmd_line]))
	res = EditConfig(cmd_line)
	Debug('  ' + str(res))
	if res.IsString() and isinstance(res.value, str):
		return res.value != value
	return True

def _get_crc_ne_(location : K, value : str, fname : str):
	cmd_line = ["ListKey", location.section, location.key, fname]
	res = EditConfig(cmd_line)
	Debug('  ' + str(res))
	if res.IsString():
		return res.GetSingleKeyList().crc != value
	return True

def _get_crc_eq_(location : K, value : str, fname : str):
	cmd_line = ["ListKey", location.section, location.key, fname]
	res = EditConfig(cmd_line)
	Debug('  ' + str(res))
	if res.IsString():
		return res.GetSingleKeyList().crc == value
	return False

class FixModelSettings(EditConfig_):
	"""
	Semi automated configuration fix.

	Info about <var-array>:
		<filt-1>: is a callable filter method to perform very basic filtering
		<var-array>: A tuple converted to a list and used to build parameter passage using *args. But note that the first parameter of the 
			tuple is the path to the configuration script.
		<filt-2>: is a tuple where the first argument is a callable. The other arguments are converted to a list and passed to the callable 
			using *args. But note that if the string
	"""
	X4_PRO = (
		# <filt-1>	<var-array>								<filt-2> 								<then> 											<else>
		(_always_, (_gcode_line_, LINE_PRO_CRC_UPG),		(_get_crc_eq_, '@1#', '@2#', '@0#'), 	(_set_var_, ("UPG", True)), 					(_set_var_, ("UPG", False))),
		(_always_,	(_stepper_x_max, X_MAX_PRO),			(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#'),				None),
		(_always_,	(_stepper_y_dir, Y_DIR_PRO),			(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#'),				None),
		(_always_,	(_stepper_y_min, Y_MIN_PRO),			(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#'),				None),
		(_always_,	(_stepper_y_stop, Y_STOP_PRO),			(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#'),				None),
		(_always_,	(_stepper_y_max, Y_MAX_PRO),			(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#'),				None),
		(_always_,	(_stepper_z_max, Z_MAX_PRO),			(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#'),				None),
		(_always_,	(_gcode_homing_, HOME_OVR_PRO_CRC),		(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", HOME_OVR_PRO, '@0#'),		None),
		(_always_,	(_bed_mesh_max_, MESH_MAX_PRO),			(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#'),				None),
		(_always_,	(_gcode_G29_, G29_PRO_CRC),				(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", G29_PRO, '@0#'),			None),
		(_is_def_,	(_gcode_wipe, WIPE_PLUS_CRC_DEF),		(_get_crc_eq_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", WIPE_PRO_DEF, '@0#'),		None),
		(_is_upg_,	(_gcode_wipe, WIPE_PLUS_CRC_UPG),		(_get_crc_eq_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", WIPE_PRO_UPG, '@0#'),		None),
		(_is_upg_,	(_gcode_line_only, LINE_ONLY_PLUS_CRC),	(_get_crc_eq_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", LINE_ONLY_PRO, '@0#'),	None),
		(_always_,	(_gcode_point_0_, POINT0_PRO_CRC),		(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", POINT0_PRO, '@0#'),		None),
		(_always_,	(_gcode_point_1_, POINT1_PRO_CRC),		(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", POINT1_PRO, '@0#'),		None),
		(_always_,	(_gcode_point_2_, POINT2_PRO_CRC),		(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", POINT2_PRO, '@0#'),		None),
		(_always_,	(_gcode_point_3_, POINT3_PRO_CRC),		(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", POINT3_PRO, '@0#'),		None),
	)
	X4_PLUS = (
		# <filt-1>	<var-array>								<filt-2> 								<then> 											<else>
		(_always_, 	(_gcode_line_, LINE_PLUS_CRC_UPG),		(_get_crc_eq_, '@1#', '@2#', '@0#'), 	(_set_var_, "UPG", True), 						(_set_var_, "UPG", False)),
		(_always_,	(_stepper_x_max, X_MAX_PLUS),			(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#'),				None),
		(_always_,	(_stepper_y_dir, Y_DIR_PLUS),			(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#'),				None),
		(_always_,	(_stepper_y_min, Y_MIN_PLUS),			(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#'),				None),
		(_always_,	(_stepper_y_stop, Y_STOP_PLUS),			(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#'),				None),
		(_always_,	(_stepper_y_max, Y_MAX_PLUS),			(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#'),				None),
		(_always_,	(_stepper_z_max, Z_MAX_PLUS),			(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#'),				None),
		(_always_,	(_gcode_homing_, HOME_OVR_PLUS_CRC),	(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", HOME_OVR_PLUS, '@0#'),	None),
		(_always_,	(_bed_mesh_max_, MESH_MAX_PLUS),		(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#'),				None),
		(_always_,	(_gcode_G29_, G29_PLUS_CRC),			(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", G29_PLUS, '@0#'),			None),
		(_is_def_,	(_gcode_wipe, WIPE_PRO_CRC_DEF),		(_get_crc_eq_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", WIPE_PLUS_DEF, '@0#'),	None),
		(_is_upg_,	(_gcode_wipe, WIPE_PRO_CRC_UPG),		(_get_crc_eq_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", WIPE_PLUS_UPG, '@0#'),	None),
		(_is_upg_,	(_gcode_line_only, LINE_ONLY_PRO_CRC),	(_get_crc_eq_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", LINE_ONLY_PLUS, '@0#'),	None),
		(_always_,	(_gcode_point_0_, POINT0_PLUS_CRC),		(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", POINT0_PLUS, '@0#'),		None),
		(_always_,	(_gcode_point_1_, POINT1_PLUS_CRC),		(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", POINT1_PLUS, '@0#'),		None),
		(_always_,	(_gcode_point_2_, POINT2_PLUS_CRC),		(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", POINT2_PLUS, '@0#'),		None),
		(_always_,	(_gcode_point_3_, POINT3_PLUS_CRC),		(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", POINT3_PLUS, '@0#'),		None),
		(_always_,	(_gcode_point_4_, POINT4_PLUS_CRC),		(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", POINT4_PLUS, '@0#'),		None),
		(_always_,	(_gcode_point_5_, POINT5_PLUS_CRC),		(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", POINT5_PLUS, '@0#'),		None),
		(_always_,	(_gcode_point_6_, POINT6_PLUS_CRC),		(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", POINT6_PLUS, '@0#'),		None),
	)
	IDX_ARG_PAT = re.compile(r'@(\d+)#')

	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Fix Printer Model Settings"), workflow.opts.model_attr and TaskState.READY or TaskState.DISABLED)
	@staticmethod
	def _decode_call(op : list[Any], vars : list[Any]):
		if len(op) == 0:
			raise RuntimeError("Function call need at least a function value")
		call : Callable = op[0]	# type:ignore
		del op[0]
		args : list[Any] = []
		for p in op:
			if isinstance(p, str):
				m = FixModelSettings.IDX_ARG_PAT.match(p)
				if m:
					v = vars[int(m[1])]
					if isinstance(v, K) or isinstance(v, str):
						args.append(v)
					else:
						raise ValueError("Unsupported data-type")
				else:
					args.append(p)
			else:
				args.append(p)
		return call(*args)
	def Do(self):
		workflow = self.workflow
		# Validate state
		if workflow.opts.model_attr == False:
			raise Exception("This item is disabled, why got called?")
		super().Do()
		super().Validate()
		# Select by printer
		if workflow.opts.IsArtillerySWX4Pro():
			# Changes for Artillery Sidewinder X4 Pro
			plan = FixModelSettings.X4_PRO
		else:
			# Changes for Artillery Sidewinder X4 Plus
			plan = FixModelSettings.X4_PLUS
		# Run the correction plan
		for op in plan:
			if op[0]():
				vars : list[Any] = [self.target]
				if op[1]:
					vars += list(op[1])
				if not isinstance(op[2], tuple):
					raise RuntimeError("Filter 2 is not optional")
				if self._decode_call(list(op[2]), vars):
					if isinstance(op[3], tuple):
						self._decode_call(list(op[3]), vars)
					elif op[3] is not None:
						raise RuntimeError("The `then` clause has an unexpected data-type")
				elif isinstance(op[4], tuple):
					self._decode_call(list(op[4]), vars)
				elif op[4] is not None:
					raise RuntimeError("The `else` clause has an unexpected data-type")

				













