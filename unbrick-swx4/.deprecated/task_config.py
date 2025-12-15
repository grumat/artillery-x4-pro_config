#
# -*- coding: UTF-8 -*-
#
# Spellchecker: words USWX klipper gcode endstop grumat


import os
import shutil
import re
import shlex
from datetime import datetime
from typing import TYPE_CHECKING, Callable, Any

TEST_MODE = os.getenv("USWX4_TEST")

STORE = {}
def _get_var_(key : str):
	if key not in STORE:
		raise RuntimeError("variable not present")
	return STORE[key]
def _set_var_(key : str, value):
	STORE[key] = value
def _persistence_updated_():
	STORE["PERSISTENCE"] = True

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
			# In test mode, upper word contains the initial printer configuration file
			start = workflow.opts.printer >>  16
			# Get rid of this information, since plugins don't expect these masked values
			workflow.opts.printer = workflow.opts.printer & 0xFFFF
			# Apply selection
			if start == 0:
				src = os.path.join(GetAssetsFolder(), "artillery_X4_pro.def.cfg")
			elif start == 1:
				src = os.path.join(GetAssetsFolder(), "artillery_X4_pro.upg.cfg")
			elif start == 2:
				src = os.path.join(GetAssetsFolder(), "artillery_X4_pro.grumat.cfg")
			elif start == 3:
				src = os.path.join(GetAssetsFolder(), "artillery_X4_plus.def.cfg")
			elif start == 4:
				src = os.path.join(GetAssetsFolder(), "artillery_X4_plus.upg.cfg")
			elif start == 5:
				src = os.path.join(GetAssetsFolder(), "artillery_X4_plus.grumat.cfg")
			else:
				raise ValueError("Invalid start printer file")
			# Clear old test
			if os.path.isfile(self.target):
				os.unlink(self.target)
			# Not copy the start configuration file
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
			res = EditConfig(["cmd.GetPersistenceB64", self.target])
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
	def __str__(self):
		return f"[{self.section}]/{self.key}"
	def __repr__(self):
		return f'K("[{self.section}]" / "{self.key}")'


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
_hold_current_z_ = K("tmc2209 stepper_z", "hold_current")
_extruder_accel_ = K("extruder", "max_extrude_only_accel")
_extruder_current_ = K("tmc2209 extruder", "run_current")
_probe_x_offset_ = K("probe", "x_offset")
_probe_y_offset_ = K("probe", "y_offset")
_probe_speed_ = K("probe", "speed")
_probe_lift_ = K("probe", "lift_speed")
_probe_samples_ = K("probe", "samples")
_probe_result_ = K("probe", "samples_result")
_probe_tolerance_ = K("probe", "samples_tolerance")
_probe_retries_ = K("probe", "samples_tolerance_retries")
_tilt_adjust_ = K("screws_tilt_adjust", "")

def _always_():
	return True
def _is_upg_():
	return _get_var_("UPG") != False
def _is_def_():
	return _get_var_("UPG") == False
def _modified_inc_():
	if "MODIFIED" not in STORE:
		STORE["MODIFIED"] = 1
	else:
		STORE["MODIFIED"] += 1
def _get_modified_():
	if "MODIFIED" not in STORE:
		STORE["MODIFIED"] = 0
	return STORE["MODIFIED"]
def _is_modified_():
	return ("MODIFIED" not in STORE) or (STORE["MODIFIED"] != 0)

def _set_combobox_opt_(value : int) -> None:
	STORE["COMBOBOX"] = value
def _is_combo_0_() -> bool:
	return STORE["COMBOBOX"] == 0
def _is_combo_1_() -> bool:
	return STORE["COMBOBOX"] == 1
def _is_combo_2_() -> bool:
	return STORE["COMBOBOX"] == 2
def _is_combo_3_() -> bool:
	return STORE["COMBOBOX"] == 3

def _has_sec_(location : K|str, fname : str) -> bool:
	if isinstance(location, K):
		location = location.section
	cmd_line = ["ListSec", location, fname]
	Debug(" ".join([shlex.quote(t) for t in cmd_line]))
	res = EditConfig(cmd_line)
	return not res.IsError()

def _no_sec_(location : K|str, fname : str) -> bool:
	if isinstance(location, K):
		location = location.section
	cmd_line = ["ListSec", location, fname]
	Debug(" ".join([shlex.quote(t) for t in cmd_line]))
	res = EditConfig(cmd_line)
	return res.IsError()

def _has_sec_crc_ne_(location : K|str, crc : str, fname : str) -> bool:
	if isinstance(location, K):
		location = location.section
	cmd_line = ["ListSec", location, fname]
	Debug(" ".join([shlex.quote(t) for t in cmd_line]))
	res = EditConfig(cmd_line)
	if not res.IsError():
		kl = res.GetKeyList()
		if len(kl) != 1:
			raise RuntimeError("More than one section was found")
		return kl[0].crc != crc
	return False

def _set_key_(location : K, value : str, fname : str) -> None:
	cmd_line = ["EditKey", location.section, location.key, value, fname]
	Debug(" ".join([shlex.quote(t) for t in cmd_line]))
	res = EditConfig(cmd_line)
	Debug('  ' + str(res))
	if not res.IsError():
		_modified_inc_()

def _set_key_ml_(location : K, value : str, fname : str) -> None:
	cmd_line = ["EditKeyML", location.section, location.key, value, fname]
	Debug(" ".join([shlex.quote(t) for t in cmd_line]))
	res = EditConfig(cmd_line)
	Debug('  ' + str(res))
	if not res.IsError():
		_modified_inc_()

def _set_sec_ml_(after : K|str, value : str, fname : str) -> None:
	if isinstance(after, K):
		after = after.section
	cmd_line = ["AddSec", after, value, fname]
	Debug(" ".join([shlex.quote(t) for t in cmd_line]))
	res = EditConfig(cmd_line)
	Debug('  ' + str(res))
	if not res.IsError():
		_modified_inc_()

def _ovr_sec_ml_(section : K|str, value : str, fname : str) -> None:
	if isinstance(section, K):
		section = section.section
	cmd_line = ["OvrSec", section, value, fname]
	Debug(" ".join([shlex.quote(t) for t in cmd_line]))
	res = EditConfig(cmd_line)
	Debug('  ' + str(res))
	if not res.IsError():
		_modified_inc_()

def _has_key_(location : K, fname : str) -> bool:
	cmd_line = ["GetKey", location.section, location.key, fname]
	Debug(" ".join([shlex.quote(t) for t in cmd_line]))
	res = EditConfig(cmd_line)
	Debug('  ' + str(res))
	return res.IsError()

def _get_key_ne_(location : K, value : str, fname : str) -> bool:
	cmd_line = ["GetKey", location.section, location.key, fname]
	Debug(" ".join([shlex.quote(t) for t in cmd_line]))
	res = EditConfig(cmd_line)
	Debug('  ' + str(res))
	if res.IsString() and isinstance(res.value, str):
		return res.value != value
	return True

def _get_crc_ne_(location : K, value : str, fname : str) -> bool:
	cmd_line = ["ListKey", location.section, location.key, fname]
	res = EditConfig(cmd_line)
	Debug('  ' + str(res))
	if res.IsString():
		return res.GetSingleKeyList().crc != value
	return True

def _get_crc_eq_(location : K, value : str, fname : str) -> bool:
	cmd_line = ["ListKey", location.section, location.key, fname]
	res = EditConfig(cmd_line)
	Debug('  ' + str(res))
	if res.IsString():
		return res.GetSingleKeyList().crc == value
	return False

def _del_sec_(location : K|str, fname : str) -> None:
	if isinstance(location, K):
		location = location.section
	cmd_line = ["DelSec", location, fname]
	Debug(" ".join([shlex.quote(t) for t in cmd_line]))
	res = EditConfig(cmd_line)
	if not res.IsError():
		_modified_inc_()

def _del_key_(location : K, fname : str) -> None:
	cmd_line = ["DelKey", location.section, location.key, fname]
	Debug(" ".join([shlex.quote(t) for t in cmd_line]))
	res = EditConfig(cmd_line)
	Debug('  ' + str(res))
	if not res.IsError():
		_modified_inc_()

def _save_persistence(data: str, fname : str) -> None:
	cmd_line = ["Save", data, fname]
	Debug(" ".join([shlex.quote(t) for t in cmd_line]))
	res = EditConfig(cmd_line)
	if not res.IsError():
		_modified_inc_()
		_persistence_updated_()


class StmtList_(EditConfig_):
	"""
	Semi automated configuration fix.

	About each outer tuple:
		This is a statement in the form:
			if <filter-1>:
				if <filter-2>:
					<then-2>
				else:
					<else-2>
			else:
				<else-1>
	Info about <var-array>:
		Give a list with constants that will be used in that statement. The command lines can be build using shortcuts like:
			- '@0#' system provided option containing the path to the target script
			- '@1#' Your first variable (optional)
			- '@2#' Your second variable (optional)
			- ...
	About each callable:
		The <filter-1>, <filter-2>, <then-2>, <else-2> and <else-1> are callables stored each in an own tuple. A `None` is accepted except for the 
		<filter-1> and <filter-2>. Each callable tuple has the following structure: (<callable, <arg-1>, <arg-2>, ...)
		Callable return `bool` for filters and `None` for the others.
	"""
	IDX_ARG_PAT = re.compile(r'@(\d+)#')

	def __init__(self, workflow: Workflow, label: str, state: TaskState) -> None:
		super().__init__(workflow, label, state)
		# Modified flag
		self.modified_cnt = _get_modified_()
	def HasStepModified(self):
		return self.modified_cnt != _get_modified_()
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
		super().Do()
		super().Validate()
		self.modified_cnt = _get_modified_()
	def RunPlan(self, plan):
		# Run the correction plan
		for op in plan:
			if isinstance(op[0], tuple):
				# Build variable list <var-array>
				vars : list[Any] = [self.target]
				vars += list(op[0])
				# Validate <filter-1>
				if not isinstance(op[1], tuple):
					raise RuntimeError("Filter 1 is not optional")
				# Execute <filter-1>
				if self._decode_call(list(op[1]), vars):
					# Validate <filter-2>
					if not isinstance(op[2], tuple):
						raise RuntimeError("Filter 2 is not optional")
					# Execute <filter-2>
					if self._decode_call(list(op[2]), vars):
						# <then> condition
						if isinstance(op[3], tuple):
							self._decode_call(list(op[3]), vars)
						elif op[3] is not None:
							raise RuntimeError("The `then` clause has an unexpected data-type")
					elif len(op) > 4:
						if isinstance(op[4], tuple):
							# <else> condition
							self._decode_call(list(op[4]), vars)
						elif op[4] is not None:
							raise RuntimeError("The `else` clause has an unexpected data-type")
				elif len(op) > 5:
					if isinstance(op[5], tuple):
						# <else> condition
						self._decode_call(list(op[5]), vars)
					elif op[5] is not None:
						raise RuntimeError("The `else` clause has an unexpected data-type")
			else:
				raise ValueError("Invalid `var-array` element")


class FixModelSettings(StmtList_):
	X4_PRO = (
		# <var-array>								<filter-1>					<then-1: filter-2> 						<then-2> / <else-2> / <else-1>
		((_gcode_line_, LINE_PRO_CRC_UPG),			(_always_, ),				(_get_crc_eq_, '@1#', '@2#', '@0#'), 	(_set_var_, "UPG", True),
				 																										(_set_var_, "UPG", False)),
		((_stepper_x_max, X_MAX_PRO),				(_always_, ),				(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_stepper_y_dir, Y_DIR_PRO),				(_always_, ),				(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_stepper_y_min, Y_MIN_PRO),				(_always_, ),				(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_stepper_y_stop, Y_STOP_PRO),				(_always_, ),				(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_stepper_y_max, Y_MAX_PRO),				(_always_, ),				(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_stepper_z_max, Z_MAX_PRO),				(_always_, ),				(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_gcode_homing_, HOME_OVR_PRO_CRC),		(_always_, ),				(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", HOME_OVR_PRO, '@0#')),
		((_bed_mesh_max_, MESH_MAX_PRO),			(_always_, ),				(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_gcode_G29_, G29_PRO_CRC),				(_always_, ),				(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", G29_PRO, '@0#')),
		((_gcode_wipe, WIPE_PLUS_CRC_DEF),			(_is_def_, ),				(_get_crc_eq_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", WIPE_PRO_DEF, '@0#')),
		((_gcode_wipe, WIPE_PLUS_CRC_UPG),			(_is_upg_, ),				(_get_crc_eq_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", WIPE_PRO_UPG, '@0#')),
		((_gcode_line_only, LINE_ONLY_PLUS_CRC),	(_is_upg_, ),				(_get_crc_eq_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", LINE_ONLY_PRO, '@0#')),
		((_gcode_point_0_, POINT0_PRO_CRC),			(_always_, ),				(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", POINT0_PRO, '@0#')),
		((_gcode_point_1_, POINT1_PRO_CRC),			(_always_, ),				(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", POINT1_PRO, '@0#')),
		((_gcode_point_2_, POINT2_PRO_CRC),			(_always_, ),				(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", POINT2_PRO, '@0#')),
		((_gcode_point_3_, POINT3_PRO_CRC),			(_always_, ),				(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", POINT3_PRO, '@0#')),
		((_gcode_point_4_, ),						(_always_, ),				(_has_sec_, '@1#', '@0#'),				(_del_sec_, "@1#", '@0#')),
		((_gcode_point_5_, ),						(_always_, ),				(_has_sec_, '@1#', '@0#'),				(_del_sec_, "@1#", '@0#')),
		((_gcode_point_6_, ),						(_always_, ),				(_has_sec_, '@1#', '@0#'),				(_del_sec_, "@1#", '@0#')),
		((RESET_CFG_PRO, ),							(_always_, ),				(_is_modified_, ),						(_save_persistence, "@1#", '@0#')),
	)
	X4_PLUS = (
		# <var-array>								<filter-1>					<filter-2> 								<then-2> / <else-2> / <else-1>
		((_gcode_line_, LINE_PLUS_CRC_UPG),			(_always_, ), 				(_get_crc_eq_, '@1#', '@2#', '@0#'), 	(_set_var_, "UPG", True),
   																								 						(_set_var_, "UPG", False)),
		((_stepper_x_max, X_MAX_PLUS),				(_always_, ),				(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_stepper_y_dir, Y_DIR_PLUS),				(_always_, ),				(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_stepper_y_min, Y_MIN_PLUS),				(_always_, ),				(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_stepper_y_stop, Y_STOP_PLUS),			(_always_, ),				(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_stepper_y_max, Y_MAX_PLUS),				(_always_, ),				(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_stepper_z_max, Z_MAX_PLUS),				(_always_, ),				(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_gcode_homing_, HOME_OVR_PLUS_CRC),		(_always_, ),				(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", HOME_OVR_PLUS, '@0#')),
		((_bed_mesh_max_, MESH_MAX_PLUS),			(_always_, ),				(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_gcode_G29_, G29_PLUS_CRC),				(_always_, ),				(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", G29_PLUS, '@0#')),
		((_gcode_wipe, WIPE_PRO_CRC_DEF),			(_is_def_, ),				(_get_crc_eq_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", WIPE_PLUS_DEF, '@0#')),
		((_gcode_wipe, WIPE_PRO_CRC_UPG),			(_is_upg_, ),				(_get_crc_eq_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", WIPE_PLUS_UPG, '@0#')),
		((_gcode_line_only, LINE_ONLY_PRO_CRC),		(_is_upg_, ),				(_get_crc_eq_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", LINE_ONLY_PLUS, '@0#')),
		((_gcode_point_0_, POINT0_PLUS_CRC),		(_always_, ),				(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", POINT0_PLUS, '@0#')),
		((_gcode_point_1_, POINT1_PLUS_CRC),		(_always_, ),				(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", POINT1_PLUS, '@0#')),
		((_gcode_point_2_, POINT2_PLUS_CRC),		(_always_, ),				(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", POINT2_PLUS, '@0#')),
		((_gcode_point_3_, POINT3_PLUS_CRC),		(_always_, ),				(_get_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_ml_, "@1#", POINT3_PLUS, '@0#')),
		((_gcode_point_4_, POINT4_PLUS_CRC),		(_has_sec_, '@1#', '@0#'),	(_get_crc_eq_, '@1#', '@2#', '@0#'),	None,
   																														(_set_key_ml_, "@1#", POINT4_PLUS, '@0#'),
																														(_set_sec_ml_, _gcode_point_3_, POINT4_SEC_PLUS, '@0#')),
		((_gcode_point_5_, POINT5_PLUS_CRC),		(_has_sec_, '@1#', '@0#'),	(_get_crc_eq_, '@1#', '@2#', '@0#'),	None,
   																														(_set_key_ml_, "@1#", POINT5_PLUS, '@0#'),
																														(_set_sec_ml_, _gcode_point_4_, POINT5_SEC_PLUS, '@0#')),
		((_gcode_point_6_, POINT6_PLUS_CRC),		(_has_sec_, '@1#', '@0#'),	(_get_crc_eq_, '@1#', '@2#', '@0#'),	None,
   																														(_set_key_ml_, "@1#", POINT6_PLUS, '@0#'),
																														(_set_sec_ml_, _gcode_point_5_, POINT6_SEC_PLUS, '@0#')),
		((RESET_CFG_PLUS, ),						(_always_, ),				(_is_modified_, ),						(_save_persistence, "@1#", '@0#')),
	)

	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Fix Printer Model Settings"), workflow.opts.model_attr and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		# Validate state
		if workflow.opts.model_attr == False:
			raise Exception("This item is disabled, why got called?")
		super().Do()
		# Select by printer
		if workflow.opts.IsArtillerySWX4Pro():
			# Changes for Artillery Sidewinder X4 Pro
			plan = self.X4_PRO
		else:
			# Changes for Artillery Sidewinder X4 Plus
			plan = self.X4_PLUS
		self.RunPlan(plan)


class StepperZCurrent(StmtList_):
	PLAN =(
		# <var-array>									<filter-1>			<then-1: filter-2> 						<then-2> / <else-2> / <else-1>
		((_hold_current_z_, HOLD_CURRENT_Z_LOW),		(_is_combo_1_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_hold_current_z_, HOLD_CURRENT_Z_HI),			(_is_combo_2_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
	)

	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Stepper Z Hold Current"), workflow.opts.stepper_z_current and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		# Validate state
		super().Do()
		_set_combobox_opt_(workflow.opts.stepper_z_current)
		self.RunPlan(self.PLAN)


class ExtruderAccel(StmtList_):
	PLAN =(
		# <var-array>									<filter-1>			<then-1: filter-2> 						<then-2> / <else-2> / <else-1>
		((_extruder_accel_, EXTRUDER_ACCEL_LOW),		(_is_combo_1_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_extruder_accel_, EXTRUDER_ACCEL_MID),		(_is_combo_2_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_extruder_accel_, EXTRUDER_ACCEL_HI),			(_is_combo_3_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
	)

	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Extruder Acceleration Limit"), workflow.opts.extruder_accel and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		# Validate state
		super().Do()
		_set_combobox_opt_(workflow.opts.extruder_accel)
		self.RunPlan(self.PLAN)


class ExtruderCurrent(StmtList_):
	PLAN =(
		# <var-array>									<filter-1>			<then-1: filter-2> 						<then-2> / <else-2> / <else-1>
		((_extruder_current_, EXTRUDER_CURRENT_LOW),	(_is_combo_1_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_extruder_current_, EXTRUDER_CURRENT_MID),	(_is_combo_2_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_extruder_current_, EXTRUDER_CURRENT_HI),		(_is_combo_3_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
	)

	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Extruder Run Current"), workflow.opts.extruder_current and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		# Validate state
		super().Do()
		_set_combobox_opt_(workflow.opts.extruder_current)
		self.RunPlan(self.PLAN)


class ProbeOffset(StmtList_):
	PLAN =(
		# <var-array>							<filter-1>			<then-1: filter-2> 						<then-2> / <else-2> / <else-1>
		((_probe_x_offset_, PROBE_X_OFFSET),	(_is_combo_1_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_probe_y_offset_, PROBE_Y_OFFSET),	(_is_combo_1_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_probe_x_offset_, PROBE180_X_OFFSET),	(_is_combo_2_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_probe_y_offset_, PROBE180_Y_OFFSET),	(_is_combo_2_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
	)

	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Probe Offset"), workflow.opts.probe_offset and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		# Validate state
		super().Do()
		_set_combobox_opt_(workflow.opts.probe_offset)
		self.RunPlan(self.PLAN)


class ProbeSampling(StmtList_):
	PLAN =(
		# <var-array>								<filter-1>			<then-1: filter-2> 						<then-2> / <else-2> / <else-1>
		((_probe_speed_, PROBE_SPEED),				(_is_combo_1_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_probe_lift_, ),							(_is_combo_1_, ),	(_has_key_, '@1#', '@0#'),				(_del_key_, "@1#", '@0#')),
		((_probe_samples_, PROBE_SAMPLE),			(_is_combo_1_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_probe_result_, PROBE_RESULT),			(_is_combo_1_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		# <var-array>								<filter-1>			<then-1: filter-2> 						<then-2> / <else-2> / <else-1>
		((_probe_speed_, PROBE180_SPEED),			(_is_combo_2_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_probe_lift_, PROBE180_LIFT),				(_is_combo_2_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_probe_samples_, PROBE180_SAMPLE),		(_is_combo_2_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_probe_result_, PROBE180_RESULT),			(_is_combo_2_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
	)

	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Z-Offset Sampling"), workflow.opts.probe_sampling and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		# Validate state
		super().Do()
		_set_combobox_opt_(workflow.opts.probe_sampling)
		self.RunPlan(self.PLAN)


class ProbeValidation(StmtList_):
	PLAN =(
		# <var-array>								<filter-1>			<then-1: filter-2> 						<then-2> / <else-2> / <else-1>
		((_probe_tolerance_, PROBE_TOLERANCE),		(_is_combo_1_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_probe_retries_, PROBE_RETRIES),			(_is_combo_1_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		# <var-array>								<filter-1>			<then-1: filter-2> 						<then-2> / <else-2> / <else-1>
		((_probe_tolerance_, PROBE180_TOLERANCE),	(_is_combo_2_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
		((_probe_retries_, PROBE180_RETRIES),		(_is_combo_2_, ),	(_get_key_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", '@2#', '@0#')),
	)

	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Z-Offset Error Margin"), workflow.opts.probe_validation and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		# Validate state
		super().Do()
		_set_combobox_opt_(workflow.opts.probe_validation)
		self.RunPlan(self.PLAN)


class ScrewsTiltAdjust(StmtList_):
	X4_PRO = (
		# <var-array>							<filter-1>			<then-1: filter-2> 							<then-2> / <else-2> / <else-1>
		((_tilt_adjust_, SCREWS_PRO_CRC),		(_is_combo_1_, ),	(_has_sec_crc_ne_, '@1#', '@2#', '@0#'),	(_ovr_sec_ml_, "@1#", SCREWS_PRO, '@0#')),
		((_tilt_adjust_, ),						(_is_combo_1_, ),	(_no_sec_, '@1#', '@0#'),					(_set_sec_ml_, "@1#", SCREWS_PRO, '@0#')),
		# <var-array>							<filter-1>			<then-1: filter-2> 							<then-2> / <else-2> / <else-1>
		((_tilt_adjust_, SCREWS180_PRO_CRC),	(_is_combo_2_, ),	(_has_sec_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", SCREWS180_PRO, '@0#')),
		((_tilt_adjust_, ),						(_is_combo_2_, ),	(_no_sec_, '@1#', '@0#'),					(_set_sec_ml_, "@1#", SCREWS180_PRO, '@0#')),
	)
	X4_PLUS = (
		# <var-array>							<filter-1>			<then-1: filter-2> 							<then-2> / <else-2> / <else-1>
		((_tilt_adjust_, SCREWS_PLUS_CRC),		(_is_combo_1_, ),	(_has_sec_crc_ne_, '@1#', '@2#', '@0#'),	(_ovr_sec_ml_, "@1#", SCREWS_PLUS, '@0#')),
		((_tilt_adjust_, ),						(_is_combo_1_, ),	(_no_sec_, '@1#', '@0#'),					(_set_sec_ml_, "@1#", SCREWS_PLUS, '@0#')),
		# <var-array>							<filter-1>			<then-1: filter-2> 							<then-2> / <else-2> / <else-1>
		((_tilt_adjust_, SCREWS180_PLUS_CRC),	(_is_combo_2_, ),	(_has_sec_crc_ne_, '@1#', '@2#', '@0#'),	(_set_key_, "@1#", SCREWS180_PLUS, '@0#')),
		((_tilt_adjust_, ),						(_is_combo_2_, ),	(_no_sec_, '@1#', '@0#'),					(_set_sec_ml_, "@1#", SCREWS180_PLUS, '@0#')),
	)

	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Manual Leveling Feature"), workflow.opts.screws_tilt_adjust and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		# Validate state
		super().Do()
		_set_combobox_opt_(workflow.opts.screws_tilt_adjust)
		# Select by printer
		if workflow.opts.IsArtillerySWX4Pro():
			# Changes for Artillery Sidewinder X4 Pro
			plan = self.X4_PRO
		else:
			# Changes for Artillery Sidewinder X4 Plus
			plan = self.X4_PLUS
		self.RunPlan(plan)



def HasUpdatedPersistence() -> bool:
	return ("PERSISTENCE" in STORE) and STORE["PERSISTENCE"]

