#
# -*- coding: UTF-8 -*-
#
# Spellchecker: words USWX klipper gcode endstop grumat toks heatbreak mainboard


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
	from .encoded_data import *
	from .my_workflow import Task, TaskState, Workflow # type: ignore
	from .edit_cfg import *
else:
	from my_env import GetBackupFolder, GetAssetsFolder, Debug
	from i18n import _, N_
	from encoded_data import *
	from my_workflow import Task, TaskState, Workflow # type: ignore
	from edit_cfg import *


class Pair_(object):
	def __init__(self, name : str|None = None) -> None:
		self.type = ""
		self.name = ""
		if name:
			toks = name.split()
			if len(toks) == 2:
				self.type = toks[0]
				self.name = toks[1]
	def IsEmpty(self) -> bool:
		return (len(self.type) == 0) or (len(self.name) == 0)
	def GetSectionName(self) -> str:
		assert len(self.type) and len(self.name), "Empty Object"
		return self.type + ' ' + self.name


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
			raise Exception(_("Cannot find the copy of the configuration file!"))
		if self.workflow.editor is None:
			raise Exception(_("Configuration file editor is missing!"))
	def IdentifyFans(self) -> tuple[Pair_, Pair_]:
		" Return heat-break and main-board fan sections respectively"
		editor = self.workflow.editor
		assert isinstance(editor, Commands), "Invalid object state"
		heat_break = Pair_()
		main_board = Pair_()
		for s in editor.ListSections("heater_fan *"):
			v = editor.GetKey(s.label, "pin")
			if isinstance(v, str):
				if v == "PC7":
					heat_break = Pair_(s.label)
				elif v == "PC9":
					main_board = Pair_(s.label)
		if main_board.IsEmpty():
			for s in editor.ListSections("controller_fan *"):
				v = editor.GetKey(s.label, "pin")
				if v == "PC9":
					main_board = Pair_(s.label)
		return (heat_break, main_board)


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
		self.workflow.editor = Commands(self.target)


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
		assert workflow.editor is not None, "Invalid object state"
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
			cal = workflow.editor.GetPersistenceB64()
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
			workflow.editor.SavePersistenceB64(cal)


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
_gcode_M300_ = K("gcode_macro M300", "gcode")
_gcode_M600_ = K("gcode_macro M600", "gcode")
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
		self.modified_cnt = self.workflow.modify_cfg
		self.combo_val = 0
	def HasStepModified(self):
		return self.modified_cnt != self.workflow.modify_cfg
	def _decode_call(self, op : list[Any], vars : list[Any]):
		if len(op) == 0:
			raise RuntimeError("Function call need at least a function value")
		call : Callable = getattr(self, op[0])
		del op[0]
		args : list[Any] = []
		for p in op:
			if type(p) is str:
				m = FixModelSettings.IDX_ARG_PAT.match(p)
				if m:
					v = vars[int(m[1])]
					if isinstance(v, (K, str, CrcKey, LinesB64)):
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
		self.modified_cnt = self.workflow.modify_cfg
	def RunPlan(self, plan):
		# Run the correction plan
		for op in plan:
			if isinstance(op[0], tuple):
				# Build variable list <var-array>
				vars : list[Any] = [None]
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
	def _set_upgraded_cfg_(self, status : bool) -> None:
		self.workflow.upgraded_cfg = status
	def _modified_inc_(self) -> None:
		self.workflow.modify_cfg += 1
	def _always_(self) -> bool:
		return True
	def _is_def_(self) -> bool:
		" Is default factory config? (not an upgraded version) "
		return self.workflow.upgraded_cfg == False
	def _is_upg_(self) -> bool:
		" Is upgraded config? (not a default version) "
		return self.workflow.upgraded_cfg != False
	def _is_modified_(self) -> bool:
		return self.workflow.modify_cfg != 0
	def _set_combobox_opt_(self, v : int) -> None:
		self.combo_val = v
	def _is_combo_0_(self) -> bool:
		return self.combo_val == 0
	def _is_combo_1_(self) -> bool:
		return self.combo_val == 1
	def _is_combo_2_(self) -> bool:
		return self.combo_val == 2
	def _is_combo_3_(self) -> bool:
		return self.combo_val == 3
	##### SECTION ######
	def _has_sec_(self, k : K|str) -> bool:
		assert self.workflow.editor is not None, "Invalid object state"
		if isinstance(k, K):
			k = k.section
		return self.workflow.editor.ListSection(k) is not None
	def _no_sec_(self, k : K|str) -> bool:
		assert self.workflow.editor is not None, "Invalid object state"
		if isinstance(k, K):
			k = k.section
		return self.workflow.editor.ListSection(k) is None
	def _has_sec_crc_ne_(self, k : K|str, value : CrcKey) -> bool:
		assert self.workflow.editor is not None, "Invalid object state"
		if isinstance(k, K):
			k = k.section
		res = self.workflow.editor.ListSection(k)
		if isinstance(res, SectionInfo):
			return res.crc != value
		return False
	def _del_sec_(self, k : K|str) -> bool:
		assert self.workflow.editor is not None, "Invalid object state"
		if isinstance(k, K):
			k = k.section
		res = self.workflow.editor.DelSec(k)
		if res:
			self._modified_inc_()
			return True
		return False
	def _set_sec_ml_(self, k : K|str, b64 : LinesB64) -> None:
		assert self.workflow.editor is not None, "Invalid object state"
		if isinstance(k, K):
			k = k.section
		self.workflow.editor.AddSec(k, b64)
		self._modified_inc_()
	def _ovr_sec_ml_(self, k : K|str, b64 : LinesB64) -> None:
		assert self.workflow.editor is not None, "Invalid object state"
		if isinstance(k, K):
			k = k.section
		self.workflow.editor.OvrSec(k, b64)
		self._modified_inc_()
	##### SECTION/KEY/VALUE ######
	def _has_key_(self, k : K) -> bool:
		assert self.workflow.editor is not None, "Invalid object state"
		return self.workflow.editor.GetKey(k.section, k.key) is not None
	def _get_crc_eq_(self, k : K, value : CrcKey) -> bool:
		assert self.workflow.editor is not None, "Invalid object state"
		res = self.workflow.editor.ListKey(k.section, k.key)
		if isinstance(res, KeyInfo):
			return res.crc == value
		return False
	def _get_crc_ne_(self, k : K, value : CrcKey) -> bool:
		assert self.workflow.editor is not None, "Invalid object state"
		res = self.workflow.editor.ListKey(k.section, k.key)
		if isinstance(res, KeyInfo):
			return res.crc != value
		return True
	def _get_key_ne_(self, k : K, value : str) -> bool:
		assert self.workflow.editor is not None, "Invalid object state"
		res = self.workflow.editor.GetKey(k.section, k.key)
		if isinstance(res, str):
			return str != value
		return True
	def _set_key_(self, k : K, value : str) -> bool:
		assert self.workflow.editor is not None, "Invalid object state"
		if self.workflow.editor.EditKey(k.section, k.key, value):
			self._modified_inc_()
			return True
		return False
	def _set_key_ml_(self, k : K, value : LinesB64) -> bool:
		assert self.workflow.editor is not None, "Invalid object state"
		if self.workflow.editor.EditKeyML(k.section, k.key, value):
			self._modified_inc_()
			return True
		return False
	def _del_key_(self, k : K, value : LinesB64) -> bool:
		assert self.workflow.editor is not None, "Invalid object state"
		return self.workflow.editor.DelKey(k.section, k.key) == True
	##### PERSISTENCE BLOCK ######
	def _save_persistence_(self, data : LinesB64) -> None:
		assert self.workflow.editor is not None, "Invalid object state"
		self.workflow.editor.SavePersistenceB64(data)
		self._modified_inc_()
		self.workflow.persistence_upd = True


_always_ = "_always_"					# Always true
_is_def_ = "_is_def_"					# Is default factory config?
_is_upg_ = "_is_upg_"					# Is upgraded config?
_set_upgraded_cfg_ = "_set_upgraded_cfg_"
_is_modified_ = "_is_modified_"			# Config file was changed?
_is_combo_0_ = "_is_combo_0_"			# Item 0 of associated combobox is selected
_is_combo_1_ = "_is_combo_1_"			# Item 1 of associated combobox is selected
_is_combo_2_ = "_is_combo_2_"			# Item 2 of associated combobox is selected
_is_combo_3_ = "_is_combo_3_"			# Item 2 of associated combobox is selected
_has_sec_ = "_has_sec_"					# Has Section?
_has_sec_crc_ne_ = "_has_sec_crc_ne_"	# Section exists but differs CRC
_no_sec_ = "_no_sec_"					# Does not have section?
_del_sec_ = "_del_sec_"					# Delete a section
_set_sec_ml_ = "_set_sec_ml_"			# Adds entire section contents after a section
_ovr_sec_ml_ = "_ovr_sec_ml_"			# Overwrite entire section contents
_has_key_ = "_has_key_"					# Does the section has the specified key?
_get_crc_eq_ = "_get_crc_eq_"			# Exists and is CRC equal?
_get_crc_ne_ = "_get_crc_ne_"			# Does not exists or CRC is not equal?
_get_key_ne_ = "_get_key_ne_"			# Does not exists or key value differs?
_set_key_ = "_set_key_"					# Sets simple key value
_set_key_ml_ = "_set_key_ml_"			# Sets MultiLine key
_del_key_ = "_del_key_"					# Delete a key
_save_persistence_ = "_save_persistence_"
_1_ = '@1#'
_2_ = '@2#'
_3_ = '@3#'


class FixModelSettings(StmtList_):
	X4_PRO = (
		# <var-array>								<filter-1>			<then-1: filter-2> 			<then-2> / <else-2> / <else-1>
		((_gcode_M300_, _gcode_M600_),				(_has_key_, _1_),	(_has_key_, _2_), 			(_set_upgraded_cfg_, True),
				 																						(_set_upgraded_cfg_, False),
				 																							(_set_upgraded_cfg_, False)),
		((_stepper_x_max, X_MAX_PRO),				(_always_, ),		(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_stepper_y_dir, Y_DIR_PRO),				(_always_, ),		(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_stepper_y_min, Y_MIN_PRO),				(_always_, ),		(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_stepper_y_stop, Y_STOP_PRO),				(_always_, ),		(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_stepper_y_max, Y_MAX_PRO),				(_always_, ),		(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_stepper_z_max, Z_MAX_PRO),				(_always_, ),		(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_gcode_homing_, HOME_OVR_PRO_CRC),		(_always_, ),		(_get_crc_ne_, _1_, _2_),	(_set_key_ml_, _1_, HOME_OVR_PRO)),
		((_bed_mesh_max_, MESH_MAX_PRO),			(_always_, ),		(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_gcode_G29_, G29_PRO_CRC),				(_always_, ),		(_get_crc_ne_, _1_, _2_),	(_set_key_ml_, _1_, G29_PRO)),
		((_gcode_wipe, WIPE_PLUS_CRC_DEF),			(_is_def_, ),		(_get_crc_eq_, _1_, _2_),	(_set_key_ml_, _1_, WIPE_PRO_DEF)),
		((_gcode_wipe, WIPE_PLUS_CRC_UPG),			(_is_upg_, ),		(_get_crc_eq_, _1_, _2_),	(_set_key_ml_, _1_, WIPE_PRO_UPG)),
		((_gcode_line_only, LINE_ONLY_PLUS_CRC),	(_is_upg_, ),		(_get_crc_eq_, _1_, _2_),	(_set_key_ml_, _1_, LINE_ONLY_PRO)),
		((_gcode_point_0_, POINT0_PRO_CRC),			(_always_, ),		(_get_crc_ne_, _1_, _2_),	(_set_key_ml_, _1_, POINT0_PRO)),
		((_gcode_point_1_, POINT1_PRO_CRC),			(_always_, ),		(_get_crc_ne_, _1_, _2_),	(_set_key_ml_, _1_, POINT1_PRO)),
		((_gcode_point_2_, POINT2_PRO_CRC),			(_always_, ),		(_get_crc_ne_, _1_, _2_),	(_set_key_ml_, _1_, POINT2_PRO)),
		((_gcode_point_3_, POINT3_PRO_CRC),			(_always_, ),		(_get_crc_ne_, _1_, _2_),	(_set_key_ml_, _1_, POINT3_PRO)),
		((_gcode_point_4_, ),						(_always_, ),		(_has_sec_, _1_),			(_del_sec_, _1_)),
		((_gcode_point_5_, ),						(_always_, ),		(_has_sec_, _1_),			(_del_sec_, _1_)),
		((_gcode_point_6_, ),						(_always_, ),		(_has_sec_, _1_),			(_del_sec_, _1_)),
		((RESET_CFG_PRO, ),							(_always_, ),		(_is_modified_, ),			(_save_persistence_, _1_)),
	)
	X4_PLUS = (
		# <var-array>								<filter-1>			<filter-2> 					<then-2> / <else-2> / <else-1>
		((_gcode_M300_, _gcode_M600_),				(_has_key_, _1_),	(_has_key_, _2_), 			(_set_upgraded_cfg_, True),
				 																						(_set_upgraded_cfg_, False),
				 																							(_set_upgraded_cfg_, False)),
		((_stepper_x_max, X_MAX_PLUS),				(_always_, ),		(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_stepper_y_dir, Y_DIR_PLUS),				(_always_, ),		(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_stepper_y_min, Y_MIN_PLUS),				(_always_, ),		(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_stepper_y_stop, Y_STOP_PLUS),			(_always_, ),		(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_stepper_y_max, Y_MAX_PLUS),				(_always_, ),		(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_stepper_z_max, Z_MAX_PLUS),				(_always_, ),		(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_gcode_homing_, HOME_OVR_PLUS_CRC),		(_always_, ),		(_get_crc_ne_, _1_, _2_),	(_set_key_ml_, _1_, HOME_OVR_PLUS)),
		((_bed_mesh_max_, MESH_MAX_PLUS),			(_always_, ),		(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_gcode_G29_, G29_PLUS_CRC),				(_always_, ),		(_get_crc_ne_, _1_, _2_),	(_set_key_ml_, _1_, G29_PLUS)),
		((_gcode_wipe, WIPE_PRO_CRC_DEF),			(_is_def_, ),		(_get_crc_eq_, _1_, _2_),	(_set_key_ml_, _1_, WIPE_PLUS_DEF)),
		((_gcode_wipe, WIPE_PRO_CRC_UPG),			(_is_upg_, ),		(_get_crc_eq_, _1_, _2_),	(_set_key_ml_, _1_, WIPE_PLUS_UPG)),
		((_gcode_line_only, LINE_ONLY_PRO_CRC),		(_is_upg_, ),		(_get_crc_eq_, _1_, _2_),	(_set_key_ml_, _1_, LINE_ONLY_PLUS)),
		((_gcode_point_0_, POINT0_PLUS_CRC),		(_always_, ),		(_get_crc_ne_, _1_, _2_),	(_set_key_ml_, _1_, POINT0_PLUS)),
		((_gcode_point_1_, POINT1_PLUS_CRC),		(_always_, ),		(_get_crc_ne_, _1_, _2_),	(_set_key_ml_, _1_, POINT1_PLUS)),
		((_gcode_point_2_, POINT2_PLUS_CRC),		(_always_, ),		(_get_crc_ne_, _1_, _2_),	(_set_key_ml_, _1_, POINT2_PLUS)),
		((_gcode_point_3_, POINT3_PLUS_CRC),		(_always_, ),		(_get_crc_ne_, _1_, _2_),	(_set_key_ml_, _1_, POINT3_PLUS)),
		((_gcode_point_4_, POINT4_PLUS_CRC),		(_has_sec_, _1_),	(_get_crc_eq_, _1_, _2_),	None,
   																										(_set_key_ml_, _1_, POINT4_PLUS),
																											(_set_sec_ml_, _gcode_point_3_, POINT4_SEC_PLUS)),
		((_gcode_point_5_, POINT5_PLUS_CRC),		(_has_sec_, _1_),	(_get_crc_eq_, _1_, _2_),	None,
   																										(_set_key_ml_, _1_, POINT5_PLUS),
																											(_set_sec_ml_, _gcode_point_4_, POINT5_SEC_PLUS)),
		((_gcode_point_6_, POINT6_PLUS_CRC),		(_has_sec_, _1_),	(_get_crc_eq_, _1_, _2_),	None,
   																										(_set_key_ml_, _1_, POINT6_PLUS),
																											(_set_sec_ml_, _gcode_point_5_, POINT6_SEC_PLUS)),
		((RESET_CFG_PLUS, ),						(_always_, ),		(_is_modified_, ),			(_save_persistence_, _1_)),
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
		# <var-array>									<filter-1>			<then-1: filter-2> 			<then-2> / <else-2> / <else-1>
		((_hold_current_z_, HOLD_CURRENT_Z_LOW),		(_is_combo_1_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_hold_current_z_, HOLD_CURRENT_Z_HI),			(_is_combo_2_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
	)

	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Stepper Z Hold Current"), workflow.opts.stepper_z_current and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		# Validate state
		super().Do()
		self._set_combobox_opt_(workflow.opts.stepper_z_current)
		self.RunPlan(self.PLAN)


class ExtruderAccel(StmtList_):
	PLAN =(
		# <var-array>									<filter-1>			<then-1: filter-2> 			<then-2> / <else-2> / <else-1>
		((_extruder_accel_, EXTRUDER_ACCEL_LOW),		(_is_combo_1_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_extruder_accel_, EXTRUDER_ACCEL_MID),		(_is_combo_2_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_extruder_accel_, EXTRUDER_ACCEL_HI),			(_is_combo_3_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
	)

	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Extruder Acceleration Limit"), workflow.opts.extruder_accel and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		# Validate state
		super().Do()
		self._set_combobox_opt_(workflow.opts.extruder_accel)
		self.RunPlan(self.PLAN)


class ExtruderCurrent(StmtList_):
	PLAN =(
		# <var-array>									<filter-1>			<then-1: filter-2> 			<then-2> / <else-2> / <else-1>
		((_extruder_current_, EXTRUDER_CURRENT_LOW),	(_is_combo_1_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_extruder_current_, EXTRUDER_CURRENT_MID),	(_is_combo_2_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_extruder_current_, EXTRUDER_CURRENT_HI),		(_is_combo_3_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
	)

	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Extruder Run Current"), workflow.opts.extruder_current and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		# Validate state
		super().Do()
		self._set_combobox_opt_(workflow.opts.extruder_current)
		self.RunPlan(self.PLAN)


class ProbeOffset(StmtList_):
	PLAN =(
		# <var-array>							<filter-1>			<then-1: filter-2> 			<then-2> / <else-2> / <else-1>
		((_probe_x_offset_, PROBE_X_OFFSET),	(_is_combo_1_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_probe_y_offset_, PROBE_Y_OFFSET),	(_is_combo_1_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_probe_x_offset_, PROBE180_X_OFFSET),	(_is_combo_2_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_probe_y_offset_, PROBE180_Y_OFFSET),	(_is_combo_2_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
	)

	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Probe Offset"), workflow.opts.probe_offset and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		# Validate state
		super().Do()
		self._set_combobox_opt_(workflow.opts.probe_offset)
		self.RunPlan(self.PLAN)


class ProbeSampling(StmtList_):
	PLAN =(
		# <var-array>							<filter-1>			<then-1: filter-2> 			<then-2> / <else-2> / <else-1>
		((_probe_speed_, PROBE_SPEED),			(_is_combo_1_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_probe_lift_, ),						(_is_combo_1_, ),	(_has_key_, _1_),			(_del_key_, _1_)),
		((_probe_samples_, PROBE_SAMPLE),		(_is_combo_1_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_probe_result_, PROBE_RESULT),		(_is_combo_1_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		# <var-array>							<filter-1>			<then-1: filter-2> 			<then-2> / <else-2> / <else-1>
		((_probe_speed_, PROBE180_SPEED),		(_is_combo_2_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_probe_lift_, PROBE180_LIFT),			(_is_combo_2_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_probe_samples_, PROBE180_SAMPLE),	(_is_combo_2_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_probe_result_, PROBE180_RESULT),		(_is_combo_2_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
	)

	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Z-Offset Sampling"), workflow.opts.probe_sampling and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		# Validate state
		super().Do()
		self._set_combobox_opt_(workflow.opts.probe_sampling)
		self.RunPlan(self.PLAN)


class ProbeValidation(StmtList_):
	PLAN =(
		# <var-array>								<filter-1>			<then-1: filter-2> 			<then-2> / <else-2> / <else-1>
		((_probe_tolerance_, PROBE_TOLERANCE),		(_is_combo_1_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_probe_retries_, PROBE_RETRIES),			(_is_combo_1_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		# <var-array>								<filter-1>			<then-1: filter-2> 			<then-2> / <else-2> / <else-1>
		((_probe_tolerance_, PROBE180_TOLERANCE),	(_is_combo_2_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
		((_probe_retries_, PROBE180_RETRIES),		(_is_combo_2_, ),	(_get_key_ne_, _1_, _2_),	(_set_key_, _1_, _2_)),
	)

	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Z-Offset Error Margin"), workflow.opts.probe_validation and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		# Validate state
		super().Do()
		self._set_combobox_opt_(workflow.opts.probe_validation)
		self.RunPlan(self.PLAN)


class ScrewsTiltAdjust(StmtList_):
	X4_PRO = (
		# <var-array>							<filter-1>			<then-1: filter-2> 				<then-2> / <else-2> / <else-1>
		((_tilt_adjust_, SCREWS_PRO_CRC),		(_is_combo_1_, ),	(_has_sec_crc_ne_, _1_, _2_),	(_ovr_sec_ml_, _1_, SCREWS_PRO)),
		((_tilt_adjust_, ),						(_is_combo_1_, ),	(_no_sec_, _1_),					(_set_sec_ml_, _1_, SCREWS_PRO)),
		# <var-array>							<filter-1>			<then-1: filter-2> 				<then-2> / <else-2> / <else-1>
		((_tilt_adjust_, SCREWS180_PRO_CRC),	(_is_combo_2_, ),	(_has_sec_crc_ne_, _1_, _2_),	(_set_key_, _1_, SCREWS180_PRO)),
		((_tilt_adjust_, ),						(_is_combo_2_, ),	(_no_sec_, _1_),					(_set_sec_ml_, _1_, SCREWS180_PRO)),
	)
	X4_PLUS = (
		# <var-array>							<filter-1>			<then-1: filter-2> 				<then-2> / <else-2> / <else-1>
		((_tilt_adjust_, SCREWS_PLUS_CRC),		(_is_combo_1_, ),	(_has_sec_crc_ne_, _1_, _2_),	(_ovr_sec_ml_, _1_, SCREWS_PLUS)),
		((_tilt_adjust_, ),						(_is_combo_1_, ),	(_no_sec_, _1_),					(_set_sec_ml_, _1_, SCREWS_PLUS)),
		# <var-array>							<filter-1>			<then-1: filter-2> 				<then-2> / <else-2> / <else-1>
		((_tilt_adjust_, SCREWS180_PLUS_CRC),	(_is_combo_2_, ),	(_has_sec_crc_ne_, _1_, _2_),	(_set_key_, _1_, SCREWS180_PLUS)),
		((_tilt_adjust_, ),						(_is_combo_2_, ),	(_no_sec_, _1_),					(_set_sec_ml_, _1_, SCREWS180_PLUS)),
	)

	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Manual Leveling Feature"), workflow.opts.screws_tilt_adjust and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		# Validate state
		super().Do()
		self._set_combobox_opt_(workflow.opts.screws_tilt_adjust)
		# Select by printer
		if workflow.opts.IsArtillerySWX4Pro():
			# Changes for Artillery Sidewinder X4 Pro
			plan = self.X4_PRO
		else:
			# Changes for Artillery Sidewinder X4 Plus
			plan = self.X4_PLUS
		self.RunPlan(plan)


class FanRename(EditConfig_):
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Rename Fans"), workflow.opts.fan_rename and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		editor = self.workflow.editor
		assert isinstance(editor, Commands), "Invalid object state"
		# Validate state
		super().Do()
		super().Validate()
		heat_break, main_board = self.IdentifyFans()
		if not heat_break.IsEmpty() and heat_break.name != "heatbreak_cooling_fan":
			nn = Pair_(heat_break.GetSectionName())
			nn.name = "heatbreak_cooling_fan"
			editor.RenSec(heat_break.GetSectionName(), nn.GetSectionName())
			self.workflow.modify_cfg += 1
		if not main_board.IsEmpty() and main_board.name != "mainboard_fan":
			nn = Pair_(main_board.GetSectionName())
			nn.name = "mainboard_fan"
			editor.RenSec(main_board.GetSectionName(), nn.GetSectionName())
			self.workflow.modify_cfg += 1


class MbFanFix(EditConfig_):
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Improved Main-board Fan control"), workflow.opts.mb_fan_fix and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		editor = self.workflow.editor
		assert isinstance(editor, Commands), "Invalid object state"
		# Validate state
		super().Do()
		super().Validate()
		_, main_board = self.IdentifyFans()
		if not main_board.IsEmpty():
			section = main_board.GetSectionName()
			if main_board.type != 'controller_fan':
				old = Pair_(section)
				main_board.type = 'controller_fan'
				editor.RenSec(old.GetSectionName(), main_board.GetSectionName())
				self.workflow.modify_cfg += 1
				section = main_board.GetSectionName()
			self.workflow.modify_cfg += (editor.EditKey(section, "idle_timeout", "180") == True)
			self.workflow.modify_cfg += (editor.EditKey(section, "heater", "extruder,heater_bed") == True)


class MbFanSpeed(EditConfig_):
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Main-board Fan Speed"), TaskState.READY)
	def Do(self):
		editor = self.workflow.editor
		assert isinstance(editor, Commands), "Invalid object state"
		# Validate state
		super().Do()
		super().Validate()
		_, main_board = self.IdentifyFans()
		if not main_board.IsEmpty():
			rate = 1.0 - self.workflow.opts.mb_fan_speed * 0.05
			value = f"{rate:.2f}"
			section = main_board.GetSectionName()
			self.workflow.modify_cfg += (editor.EditKey(section, "fan_speed", value) == True)
			if rate != 1.0:
				self.workflow.modify_cfg += (editor.EditKey(section, "cycle_time", "0.016") == True)


class HbFanSpeed(EditConfig_):
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Heat-break Fan Speed"), TaskState.READY)
	def Do(self):
		editor = self.workflow.editor
		assert isinstance(editor, Commands), "Invalid object state"
		# Validate state
		super().Do()
		super().Validate()
		heat_break, _ = self.IdentifyFans()
		if not heat_break.IsEmpty():
			rate = 1.0 - self.workflow.opts.hb_fan_speed * 0.05
			value = f"{rate:.2f}"
			section = heat_break.GetSectionName()
			self.workflow.modify_cfg += (editor.EditKey(section, "fan_speed", value) == True)
			if rate != 1.0:
				self.workflow.modify_cfg += (editor.EditKey(section, "cycle_time", "0.016") == True)


class TempMCU(EditConfig_):
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Temperature Reading for Host and MCU"), workflow.opts.temp_mcu and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		editor = self.workflow.editor
		assert isinstance(editor, Commands), "Invalid object state"
		# Validate state
		super().Do()
		super().Validate()
		host = Pair_()
		mcu = Pair_()
		for s in editor.ListSections("temperature_sensor *"):
			v = editor.GetKey(s.label, "sensor_type")
			v2 = editor.GetKey(s.label, "sensor_mcu")
			if isinstance(v, str):
				if v == "temperature_host":
					if host.IsEmpty():
						host = Pair_(v)
				elif v == "temperature_mcu" \
					and isinstance(v2, str) \
					and v2 == "mcu" \
					and mcu.IsEmpty():
					mcu = Pair_(v)
		if host.IsEmpty():
			editor.AddSec("verify_heater heater_bed", HOST_TEMP)
			self.workflow.modify_cfg += 1
		if mcu.IsEmpty():
			editor.AddSec("verify_heater heater_bed", MCU_TEMP)
			self.workflow.modify_cfg += 1




