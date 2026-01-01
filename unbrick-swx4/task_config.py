#
# -*- coding: UTF-8 -*-
#
# Spellchecker: words USWX klipper gcode endstop grumat toks heatbreak mainboard modlelight adxl sdcard neopixel


import os
import shutil
import re
import shlex
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Any
import random

TEST_MODE = os.getenv("USWX4_TEST")

if TYPE_CHECKING:
	from .my_env import GetBackupFolder, GetAssetsFolder, Debug, Info
	from .i18n import _, N_
	from .encoded_data import *
	from .my_workflow import Task, TaskState, Workflow  # type: ignore
	from .edit_cfg import *
else:
	from my_env import GetBackupFolder, GetAssetsFolder, Debug, Info
	from i18n import _, N_
	from encoded_data import *
	from my_workflow import Task, TaskState, Workflow # type: ignore
	from edit_cfg import *

SECTIONS = [
	("stepper_x", 									True ),
	("stepper_y", 									True ),
	("stepper_z", 									True ),
	("extruder", 									True ),
	("homing_override", 							True ),
	("safe_z_home",									False ),
	("probe", 										True ),
	("bed_mesh", 									False ),
	("verify_heater extruder", 						False ),
	("heater_bed", 									True ),
	("verify_heater heater_bed",					False ),
	("temperature_sensor mcu_temp", 				False ),
	("temperature_sensor rpi_cpu", 					False ),
	("fan", 										False ),
	("heater_fan fan0",								False ),
	("heater_fan heatbreak_cooling_fan",			False ),
	("heater_fan fan2", 							False ),
	("controller_fan mainboard_fan", 				False ),
	("printer", 									True ),
	("input_shaper", 								False ),
	("idle_timeout", 								False ),
	("gcode_macro G29", 							False ),
	("gcode_macro FLASHLIGHT_ON", 					False ),
	("gcode_macro FLASHLIGHT_OFF",					False ),
	("gcode_macro MODLELIGHT_ON",					False ),
	("gcode_macro MODLELIGHT_OFF",					False ),
	("filament_switch_sensor fila",					False ),
	("tmc2209 stepper_x",							True ),
	("tmc2209 stepper_y",							True ),
	("tmc2209 stepper_z",							True ),
	("tmc2209 extruder",							True ),
	("mcu rpi",										True ),
	("adxl345",										False ),
	("resonance_tester",							False ),
	("exclude_object",								False ),
	("force_move",									False ),
	("virtual_sdcard",								False ),
	("gcode_macro nozzle_wipe",						False ),
	("gcode_macro nozzle_clean",					False ),
	("gcode_macro draw_line_only",					False ),
	("gcode_macro draw_line",						False ),
	("gcode_macro PRINT_START",						False ),
	("gcode_macro PRINT_END",						False ),
	("pause_resume",								True ),
	("gcode_macro CANCEL_PRINT",					False ),
	("output_pin BEEPER_pin",						False ),
	("gcode_macro M300",							False ),
	("gcode_macro M600",							False ),
	("gcode_macro T600",							False ),
	("gcode_macro PAUSE",							False ),
	("gcode_macro RESUME",							False ),
	("display_status",								False ),
	("gcode_arcs",									False ),
	("output_pin LAMP",								False ),
	("neopixel my_neopixel",						False ),
	("gcode_macro NEOPIXEL_DISPLAY",				False ),
	("display_template led_extruder_temp_glow",		False ),
	("display_template led_bed_temp_glow",			False ),
	("display_template led_print_percent_progress",	False ),
	("gcode_macro M109",							False ),
	("gcode_macro M190",							False ),
	("gcode_macro move_to_point_0",					True ),
	("gcode_macro move_to_point_1",					True ),
	("gcode_macro move_to_point_2",					True ),
	("gcode_macro move_to_point_3",					True ),
	("gcode_macro move_to_point_4",					False ),
	("gcode_macro move_to_point_5",					False ),
	("screws_tilt_adjust",							False ),
]

def InsertAfterSection(section : str, cur_set : list[SectionInfo]) -> str|int:
	current = set([n.label for n in cur_set])
	pos = 0
	for s, _ in SECTIONS:
		if s == section:
			return pos
		if s in current:
			pos = s
	return -1


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
_bed_mesh_max_ = K("bed_mesh", "mesh_max")
_gcode_G29_ = K("gcode_macro G29", "gcode")
_gcode_M300_ = K("gcode_macro M300", "gcode")
_gcode_M600_ = K("gcode_macro M600", "gcode")
_gcode_T600_ = K("gcode_macro T600", "gcode")
_gcode_wipe = K("gcode_macro nozzle_wipe", "gcode")
_gcode_line = K("gcode_macro draw_line", "gcode")
_gcode_line_only = K("gcode_macro draw_line_only", "gcode")
_gcode_point_0_ = K("gcode_macro move_to_point_0", "gcode")
_gcode_point_1_ = K("gcode_macro move_to_point_1", "gcode")
_gcode_point_2_ = K("gcode_macro move_to_point_2", "gcode")
_gcode_point_3_ = K("gcode_macro move_to_point_3", "gcode")
_gcode_point_4_ = K("gcode_macro move_to_point_4", "gcode")
_gcode_point_5_ = K("gcode_macro move_to_point_5", "gcode")
_gcode_point_6_ = K("gcode_macro move_to_point_6", "gcode")
_gcode_pause_ = K("gcode_macro PAUSE", "gcode")
_hold_current_z_ = K("tmc2209 stepper_z", "hold_current")
_extruder_accel_ = K("extruder", "max_extrude_only_accel")
_extruder_current_ = K("tmc2209 extruder", "run_current")
_probe_pin_ = K("probe", "pin")
_probe_x_offset_ = K("probe", "x_offset")
_probe_y_offset_ = K("probe", "y_offset")
_probe_speed_ = K("probe", "speed")
_probe_lift_ = K("probe", "lift_speed")
_probe_samples_ = K("probe", "samples")
_probe_result_ = K("probe", "samples_result")
_probe_tolerance_ = K("probe", "samples_tolerance")
_probe_retries_ = K("probe", "samples_tolerance_retries")
_tilt_adjust_ = K("screws_tilt_adjust", "")
_beeper_pin_ = K("output_pin BEEPER_pin", "")
_exclude_obj_ = K("exclude_object", "")



class EditConfig_(Task):
	def __init__(self, workflow : Workflow, label : str, state : TaskState) -> None:
		super().__init__(workflow, label, state)
		self.work_folder = GetBackupFolder()
		self.target = os.path.join(self.work_folder, 'printer.cfg')
		# Modified flag
		self.modified_cnt = self.workflow.modify_cfg
		self.combo_val = 0
		self.has_log = False
	def Do(self):
		super().Do()
		if not os.path.isdir(self.work_folder):
			os.makedirs(self.work_folder)
		self.modified_cnt = self.workflow.modify_cfg
	def Validate(self):
		# File that is edited is here
		if not os.path.isfile(self.target):
			raise Exception(_("Cannot find the copy of the configuration file!"))
		if self.workflow.editor is None:
			raise Exception(_("Configuration file editor is missing!"))
	def HasStepModified(self):
		return self.modified_cnt != self.workflow.modify_cfg
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
	def _start_log_(self):
		if self.has_log == False:
			self.has_log = True
			self.Info('\n')
	def _set_upgraded_cfg_(self, status : bool) -> None:
		self.workflow.upgraded_cfg = status
		if status:
			msg = N_("An updated config file was found.")
		else:
			msg = N_("A legacy config file was found.")
		Info(msg)
		self._start_log_()
		self.Info('\t' + _(msg) + '\n')
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
			msg = N_("The section {0} was removed.")
			Warning(msg.format(f"[{k}]"))
			self._start_log_()
			self.Warning('\t' + _(msg).format(f"[{k}]") + '\n')
			return True
		return False
	def _add_sec_(self, b64 : LinesB64) -> None:
		assert self.workflow.editor is not None, "Invalid object state"
		ns = None
		ml = b64.Extract()
		for l in ml:
			if not ns and isinstance(l, SectionLine):
				ns = l.section_name
		assert ns is not None, "Invalid input argument"
		sections = self.workflow.editor.ListSections()
		w = InsertAfterSection(ns, sections)
		self.workflow.editor.AddSec(w, ml)
		self._modified_inc_()
		msg = N_("The section {0} was added.")
		Info(msg.format(f"[{ns}]"))
		for l in ml:
			Info('\t' + repr(l))
		self._start_log_()
		self.Bold('\t' + _(msg).format(f"[{ns}]") + '\n')
	def _ovr_sec_ml_(self, k : K|str, b64 : LinesB64) -> None:
		assert self.workflow.editor is not None, "Invalid object state"
		if isinstance(k, K):
			k = k.section
		self.workflow.editor.OvrSec(k, b64)
		self._modified_inc_()
		msg = N_("The section {0} was replaced.")
		Info(msg.format(f"[{k}]"))
		for l in b64.Extract():
			Info('\t' + repr(l))
		self._start_log_()
		self.Bold('\t' + _(msg).format(f"[{k}]") + '\n')
	def _upd_sec_(self, k : K, crc_pro : CrcKey|None, b64_pro : LinesB64|None, crc_plus : CrcKey|None, b64_plus : LinesB64|None) -> None:
		" Update section for pro/plus. A `None` value indicates section delete "
		assert self.workflow.editor is not None, "Invalid object state"
		if self.workflow.opts.IsArtillerySWX4Pro():
			crc = crc_pro
			b64 = b64_pro
		else:
			crc = crc_plus
			b64 = b64_plus

		info = self.workflow.editor.ListSection(k.section)
		if crc is None:
			assert b64 is None, "Invalid function argument"
			if info is not None:
				self._del_sec_(k)
		else:
			assert isinstance(b64, LinesB64), "Invalid function argument"
			if info is not None:
				if info.crc != crc:
					self._ovr_sec_ml_(k, b64)
			else:
				self._add_sec_(b64)

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
			msg : str = N_("The value {0}/{1} was added/updated to {2}.")
			Info(msg.format(f"[{k.section}]", k.key, repr(value)))
			self._start_log_()
			self.Bold('\t' + _(msg).format(f"[{k.section}]", k.key, repr(value)) + '\n')
			return True
		return False
	def _set_key_ml_(self, k : K, value : LinesB64) -> bool:
		assert self.workflow.editor is not None, "Invalid object state"
		if self.workflow.editor.EditKeyML(k.section, k.key, value):
			self._modified_inc_()
			msg : str = N_("The value {0}/{1} was added/updated.")
			Info(msg.format(f"[{k.section}]", k.key))
			for l in value.Extract():
				Info('\t' + repr(l))
			self._start_log_()
			self.Bold('\t' + _(msg).format(f"[{k.section}]", k.key) + '\n')
			return True
		return False
	def _del_key_(self, k : K) -> bool:
		assert self.workflow.editor is not None, "Invalid object state"
		if self.workflow.editor.DelKey(k.section, k.key) == True:
			msg : str = N_("The value {0}/{1} was removed.")
			Warning(msg.format(f"[{k.section}]", k.key))
			self._start_log_()
			self.Warning('\t' + _(msg).format(f"[{k.section}]", k.key) + '\n')
			return True
		return False
	def _upd_val_(self, k : K, val_pro : str|None, val_plus : str|None) -> None:
		" Update value for pro/plus. A `None` value indicates key delete "
		assert val_pro is None or isinstance(val_pro, str), "Invalid function argument"
		assert val_plus is None or isinstance(val_plus, str), "Invalid function argument"
		if self.workflow.opts.IsArtillerySWX4Pro():
			v = val_pro
		else:
			v = val_plus
		if v is None:
			self._del_key_(k)
		else:
			self._set_key_(k, v)
	def _upd_ml_(self, k : K, crc_pro : CrcKey|None, b64_pro : LinesB64|None, crc_plus : CrcKey|None, b64_plus : LinesB64|None) -> None:
		" Update multiline value for pro/plus.  A `None` value indicates key delete "
		assert crc_pro is None or isinstance(crc_pro, CrcKey), "Invalid function argument"
		assert crc_plus is None or isinstance(crc_plus, CrcKey), "Invalid function argument"
		if self.workflow.opts.IsArtillerySWX4Pro():
			crc = crc_pro
			b64 = b64_pro
		else:
			crc = crc_plus
			b64 = b64_plus
		if crc is None:
			assert b64 is None, "Invalid function argument"
			self._del_key_(k)
		else:
			assert isinstance(b64, LinesB64), "Invalid function argument"
			if self._get_crc_ne_(k, crc):
				self._set_key_ml_(k, b64)

	##### PERSISTENCE BLOCK ######
	def _save_persistence_(self, data : LinesB64) -> None:
		assert self.workflow.editor is not None, "Invalid object state"
		self.workflow.editor.SavePersistenceB64(data)
		self._modified_inc_()
		self.workflow.persistence_upd = True
		msg : str = N_("The persistence block was reset.")
		Warning(msg)
		self._start_log_()
		self.Warning('\t' + _(msg) + '\n')
	def _persist_(self, b64_pro : LinesB64, b64_plus : LinesB64) -> None:
		" Saves persistence for pro/plus configuration"
		assert isinstance(b64_pro, LinesB64), "Invalid function argument"
		assert isinstance(b64_plus, LinesB64), "Invalid function argument"
		if self.workflow.opts.IsArtillerySWX4Pro():
			self._save_persistence_(b64_pro)
		else:
			self._save_persistence_(b64_plus)


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
			workflow.backup_file = datetime.now().strftime('printer-%Y%m%d_%H%M%S.cfg')
			backup = os.path.join(self.work_folder, workflow.backup_file)
			workflow.SftpGet(CONFIG_FILE, self.target)
			self.Info(_("\n\tSuccessfully copy file '{}'").format(CONFIG_FILE))
			if os.path.isfile(backup):
				os.unlink(backup)
			Debug(f"copy '{self.target}' '{backup}'")
			if os.path.exists(backup):
				Debug(f"Remove preexisting '{backup}' file.")
				os.unlink(backup)
			shutil.copyfile(self.target, backup)
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
			tmp = Commands(self.target)
			cal = tmp.GetPersistenceB64()
			tmp = None
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
			workflow.editor = Commands(self.target)
			workflow.editor.SavePersistenceB64(cal)


class ConfigValidate(EditConfig_):
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Validate Printer Configuration"), TaskState.READY)
	def Do(self):
		workflow = self.workflow
		if not workflow.editor:
			workflow.editor = Commands(self.target)
		upg = 0
		# Build a list with required sections
		watch = [s for s, f in SECTIONS if f]
		for info in workflow.editor.ListSections():
			if info.label in watch:
				watch.remove(info.label)
			# These sections indicates a firmware upgrade
			if info.label == _gcode_M300_.section or \
				info.label == _gcode_M600_.section:
				upg += 1
		# Required section is missing
		if len(watch):
			raise Exception(N_("Configuration file is incomplete. Please reset printer configuration to factory default!"))
		# Indicates an upgraded firmware was found
		self._set_upgraded_cfg_(upg >= 2)


_always_ = "_always_"					# Always true
_is_def_ = "_is_def_"					# Is default factory config?
_is_upg_ = "_is_upg_"					# Is upgraded config?
_set_upgraded_cfg_ = "_set_upgraded_cfg_"
_is_modified_ = "_is_modified_"			# Config file was changed?
_is_combo_0_ = "_is_combo_0_"			# Item 0 of associated combobox is selected
_is_combo_1_ = "_is_combo_1_"			# Item 1 of associated combobox is selected
_is_combo_2_ = "_is_combo_2_"			# Item 2 of associated combobox is selected
_is_combo_3_ = "_is_combo_3_"			# Item 2 of associated combobox is selected

_upd_val_ = "_upd_val_"					# (_upd_val_, K, val_pro, val_plus)	 					## Use None values to delete key
_upd_ml_ = "_upd_ml_"					# (_upd_ml_, K, crc_pro, b64_pro, crc_plus, b64_plus)	## Use None values to delete key
_upd_sec_ = "_upd_sec_"					# (_upd_sec_, K, crc_pro, b64_pro, crc_plus, b64_plus)	## Use None values to delete section
_persist_ = "_persist_"					# (_persist_, b64_pro, b64_plus)


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
	def Do(self):
		super().Do()
		super().Validate()
	def RunPlan(self, plan, opt_idx : int):
		self._set_combobox_opt_(opt_idx)
		# Run the correction plan
		for op in plan:
			assert isinstance(op, tuple), "Invalid table"
			cond : Callable = getattr(self, op[0])
			if cond():
				call : Callable = getattr(self, op[1])
				args = op[2:]
				call(*args)


class FixModelSettings(StmtList_):
	PLAN = (
		# <cond>			<command>		<section/key>		<value pro>		<value plus>
		( _always_,			_upd_val_,		_stepper_x_max,		X_MAX_PRO,		X_MAX_PLUS ),
		( _always_,			_upd_val_,		_stepper_y_dir,		Y_DIR_PRO,		Y_DIR_PLUS ),
		( _always_,			_upd_val_,		_stepper_y_min,		Y_MIN_PRO,		Y_MIN_PLUS ),
		( _always_,			_upd_val_,		_stepper_y_stop,	Y_STOP_PRO,		Y_STOP_PLUS ),
		( _always_,			_upd_val_,		_stepper_y_max,		Y_MAX_PRO,		Y_MAX_PLUS ),
		( _always_,			_upd_val_,		_stepper_z_max,		Z_MAX_PRO,		Z_MAX_PLUS ),
		# <cond>			<command>		<section/key>		<crc pro>			<b64 pro>		<crc plus>			<b64 plus>
		( _always_,			_upd_ml_,		_gcode_homing_,		HOME_OVR_PRO_CRC,	HOME_OVR_PRO,	HOME_OVR_PLUS_CRC,	HOME_OVR_PLUS ),
		# <cond>			<command>		<section/key>		<value pro>		<value plus>
		( _always_,			_upd_val_,		_bed_mesh_max_,		MESH_MAX_PRO,	MESH_MAX_PLUS ),
		# <cond>			<command>		<section/key>		<crc pro>			<b64 pro>		<crc plus>			<b64 plus>
		( _always_,			_upd_ml_,		_gcode_G29_,		G29_PRO_CRC,		G29_PRO,		G29_PLUS_CRC,		G29_PLUS),
		( _is_def_,			_upd_ml_,		_gcode_wipe,		WIPE_PRO_CRC_DEF,	WIPE_PRO_DEF,	WIPE_PLUS_CRC_DEF,	WIPE_PLUS_DEF ),
		( _is_upg_,			_upd_ml_,		_gcode_wipe,		WIPE_PRO_CRC_UPG,	WIPE_PRO_UPG,	WIPE_PLUS_CRC_UPG,	WIPE_PLUS_UPG ),
		( _is_def_,			_upd_ml_,		_gcode_line,		LINE_PRO_CRC_DEF,	LINE_PRO_DEF,	LINE_PLUS_CRC_DEF,	LINE_PLUS_DEF ),
		( _is_upg_,			_upd_ml_,		_gcode_line,		LINE_PRO_CRC_UPG,	LINE_PRO_UPG,	LINE_PLUS_CRC_UPG,	LINE_PLUS_UPG ),
		# <cond>			<command>		<section/key>		<crc pro>				<b64 pro>			<crc plus>				<b64 plus>
		( _is_upg_,			_upd_sec_,		_gcode_line_only,	LINE_ONLY_PRO_CRC_UPG,	LINE_ONLY_PRO_UPG,	LINE_ONLY_PLUS_CRC_UPG,	LINE_ONLY_PLUS_UPG ),	
		# <cond>			<command>		<section/key>		<crc pro>			<b64 pro>		<crc plus>			<b64 plus>
		( _always_,			_upd_ml_,		_gcode_point_0_,	POINT0_PRO_CRC,		POINT0_PRO,		POINT0_PLUS_CRC,	POINT0_PLUS ),
		( _always_,			_upd_ml_,		_gcode_point_1_,	POINT1_PRO_CRC,		POINT1_PRO,		POINT1_PLUS_CRC,	POINT1_PLUS ),
		( _always_,			_upd_ml_,		_gcode_point_2_,	POINT2_PRO_CRC,		POINT2_PRO,		POINT2_PLUS_CRC,	POINT2_PLUS ),
		( _always_,			_upd_ml_,		_gcode_point_3_,	POINT3_PRO_CRC,		POINT3_PRO,		POINT3_PLUS_CRC,	POINT3_PLUS ),
		( _always_,			_upd_sec_,		_gcode_point_4_,	None,				None,			POINT4_PLUS_CRC,	POINT4_SEC_PLUS ),
		( _always_,			_upd_sec_,		_gcode_point_5_,	None,				None,			POINT5_PLUS_CRC,	POINT5_SEC_PLUS ),
		( _always_,			_upd_sec_,		_gcode_point_6_,	None,				None,			POINT6_PLUS_CRC,	POINT6_SEC_PLUS ),
		# <cond>			<command>		<b64 pro>			<b64 plus>
		( _is_modified_,	_persist_,		RESET_CFG_PRO,		RESET_CFG_PLUS),
	)
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Fix Printer Model Settings"), workflow.opts.model_attr and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		# Validate state
		assert workflow.opts.model_attr == True, "This item is disabled, why got called?"
		super().Do()
		# Select by printer
		self.RunPlan(self.PLAN, 0)


class ExcludeObject(StmtList_):
	PLAN =(
		# <cond>			<command>	<section/key>		<crc pro>			<b64 pro>			<crc plus>			<b64 plus>
		( _always_,			_upd_sec_,	_exclude_obj_,		EXCLUDE_OBJECT_CRC,	EXCLUDE_OBJECT,		EXCLUDE_OBJECT_CRC,	EXCLUDE_OBJECT ),
	)
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Enable Exclude Object"), workflow.opts.exclude_object and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		assert workflow.opts.exclude_object != 0, "This item is disabled, why got called?"
		# Validate state
		super().Do()
		self.RunPlan(self.PLAN, 0)


class StepperZCurrent(StmtList_):
	PLAN =(
		# <cond>			<command>		<section/key>		<value pro>				<value plus>
		( _is_combo_1_,		_upd_val_,		_hold_current_z_,	HOLD_CURRENT_Z_LOW,		HOLD_CURRENT_Z_LOW ),
		( _is_combo_2_,		_upd_val_,		_hold_current_z_,	HOLD_CURRENT_Z_HI,		HOLD_CURRENT_Z_HI ),
	)
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Z-Axis Stepper Motor Hold Current"), workflow.opts.stepper_z_current and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		assert workflow.opts.stepper_z_current != 0, "This item is disabled, why got called?"
		# Validate state
		super().Do()
		self.RunPlan(self.PLAN, workflow.opts.stepper_z_current)


class ExtruderAccel(StmtList_):
	PLAN =(
		# <cond>			<command>		<section/key>		<value pro>				<value plus>
		( _is_combo_1_,		_upd_val_,		_extruder_accel_,	EXTRUDER_ACCEL_LOW,		EXTRUDER_ACCEL_LOW ),
		( _is_combo_2_,		_upd_val_,		_extruder_accel_,	EXTRUDER_ACCEL_MID,		EXTRUDER_ACCEL_MID ),
		( _is_combo_3_,		_upd_val_,		_extruder_accel_,	EXTRUDER_ACCEL_HI,		EXTRUDER_ACCEL_HI ),
	)
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Extruder Acceleration Limit"), workflow.opts.extruder_accel and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		assert workflow.opts.extruder_accel != 0, "This item is disabled, why got called?"
		# Validate state
		super().Do()
		self.RunPlan(self.PLAN, workflow.opts.extruder_accel)


class ExtruderCurrent(StmtList_):
	PLAN =(
		# <cond>			<command>		<section/key>		<value pro>				<value plus>
		( _is_combo_1_,		_upd_val_,		_extruder_current_,	EXTRUDER_CURRENT_LOW,	EXTRUDER_CURRENT_LOW ),
		( _is_combo_2_,		_upd_val_,		_extruder_current_,	EXTRUDER_CURRENT_MID,	EXTRUDER_CURRENT_MID ),
		( _is_combo_3_,		_upd_val_,		_extruder_current_,	EXTRUDER_CURRENT_HI,	EXTRUDER_CURRENT_HI ),
	)
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Extruder Motor Current Settings"), workflow.opts.extruder_current and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		assert workflow.opts.extruder_current != 0, "This item is disabled, why got called?"
		# Validate state
		super().Do()
		self.RunPlan(self.PLAN, workflow.opts.extruder_current)


class InputPinPolarity(StmtList_):
	PLAN =(
		# <cond>			<command>		<section/key>	<value pro>		<value plus>
		( _is_combo_1_,		_upd_val_,		_probe_pin_,	PROBE_NC,		PROBE_NC ),
		( _is_combo_2_,		_upd_val_,		_probe_pin_,	PROBE_NO,		PROBE_NO ),
	)
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Distance Sensor Offset"), workflow.opts.probe_logic and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		assert workflow.opts.probe_logic != 0, "This item is disabled, why got called?"
		# Validate state
		super().Do()
		self.RunPlan(self.PLAN, workflow.opts.probe_logic)


class ProbeOffset(StmtList_):
	PLAN =(
		# <cond>			<command>		<section/key>		<value pro>			<value plus>
		( _is_combo_1_,		_upd_val_,		_probe_x_offset_,	PROBE_X_OFFSET,		PROBE_X_OFFSET ),
		( _is_combo_1_,		_upd_val_,		_probe_y_offset_,	PROBE_Y_OFFSET,		PROBE_Y_OFFSET ),
		( _is_combo_2_,		_upd_val_,		_probe_x_offset_,	PROBE180_X_OFFSET,	PROBE180_X_OFFSET ),
		( _is_combo_2_,		_upd_val_,		_probe_y_offset_,	PROBE180_Y_OFFSET,	PROBE180_Y_OFFSET ),
	)
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Distance Sensor Offset"), workflow.opts.probe_offset and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		assert workflow.opts.probe_offset != 0, "This item is disabled, why got called?"
		# Validate state
		super().Do()
		self.RunPlan(self.PLAN, workflow.opts.probe_offset)


class ProbeSampling(StmtList_):
	PLAN =(
		# <cond>			<command>		<section/key>		<value pro>			<value plus>
		( _is_combo_1_,		_upd_val_,		_probe_speed_,		PROBE_SPEED,		PROBE_SPEED ),
		( _is_combo_2_,		_upd_val_,		_probe_speed_,		PROBE180_SPEED,		PROBE180_SPEED ),
		( _is_combo_1_,		_upd_val_,		_probe_lift_,		None,				None ),
		( _is_combo_2_,		_upd_val_,		_probe_lift_,		PROBE180_LIFT,		PROBE180_LIFT ),
		( _is_combo_1_,		_upd_val_,		_probe_samples_,	PROBE_SAMPLE,		PROBE_SAMPLE ),
		( _is_combo_2_,		_upd_val_,		_probe_samples_,	PROBE180_SAMPLE,	PROBE180_SAMPLE ),
		( _is_combo_1_,		_upd_val_,		_probe_result_,		PROBE_RESULT,		PROBE_RESULT ),
		( _is_combo_2_,		_upd_val_,		_probe_result_,		PROBE180_RESULT,	PROBE180_RESULT ),
	)
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Z-Offset Sampling"), workflow.opts.probe_sampling and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		assert workflow.opts.probe_sampling != 0, "This item is disabled, why got called?"
		# Validate state
		super().Do()
		self.RunPlan(self.PLAN, workflow.opts.probe_sampling)


class ProbeValidation(StmtList_):
	PLAN =(
		# <cond>			<command>		<section/key>		<value pro>			<value plus>
		( _is_combo_1_,		_upd_val_,		_probe_tolerance_,	PROBE_TOLERANCE,	PROBE_TOLERANCE ),
		( _is_combo_2_,		_upd_val_,		_probe_tolerance_,	PROBE180_TOLERANCE,	PROBE180_TOLERANCE ),
		( _is_combo_1_,		_upd_val_,		_probe_retries_,	PROBE_RETRIES,		PROBE_RETRIES ),
		( _is_combo_2_,		_upd_val_,		_probe_retries_,	PROBE180_RETRIES,	PROBE180_RETRIES ),
	)
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Z-Offset Error Margin"), workflow.opts.probe_validation and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		assert workflow.opts.probe_validation != 0, "This item is disabled, why got called?"
		# Validate state
		super().Do()
		self.RunPlan(self.PLAN, workflow.opts.probe_validation)


class ScrewsTiltAdjust(StmtList_):
	PLAN =(
		# <cond>			<command>	<section/key>		<crc pro>			<b64 pro>			<crc plus>			<b64 plus>
		( _is_combo_1_,		_upd_sec_,	_tilt_adjust_,		SCREWS_PRO_CRC,		SCREWS_PRO,			SCREWS_PLUS_CRC,	SCREWS_PLUS ),
		( _is_combo_2_,		_upd_sec_,	_tilt_adjust_,		SCREWS180_PRO_CRC,	SCREWS180_PRO,		SCREWS180_PLUS_CRC,	SCREWS180_PLUS),
	)

	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Enable Manual Bed Leveling"), workflow.opts.screws_tilt_adjust and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		assert workflow.opts.screws_tilt_adjust != 0, "This item is disabled, why got called?"
		# Validate state
		super().Do()
		self.RunPlan(self.PLAN, workflow.opts.screws_tilt_adjust)


class FanRename(EditConfig_):
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Rename Fans for Clarity"), workflow.opts.fan_rename and TaskState.READY or TaskState.DISABLED)
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
		super().__init__(workflow, N_("Enhanced Mainboard Fan Control"), workflow.opts.mb_fan_fix and TaskState.READY or TaskState.DISABLED)
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
		super().__init__(workflow, N_("Adjust Mainboard Fan Speed"), TaskState.READY)
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
		super().__init__(workflow, N_("Adjust Heat-Break Fan Speed"), TaskState.READY)
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
		super().__init__(workflow, N_("Enable Host & MCU Temperature Monitoring"), workflow.opts.temp_mcu and TaskState.READY or TaskState.DISABLED)
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


class NozzleWipe(StmtList_):
	PLAN =(
		# <cond>			<command>	<section/key>		<crc pro>			<b64 pro>			<crc plus>			<b64 plus>
		( _is_combo_1_,		_upd_ml_,	_gcode_wipe,		WIPE_PRO_CRC_DEF,	WIPE_PRO_DEF,		WIPE_PLUS_CRC_DEF,	WIPE_PLUS_DEF ),
		( _is_combo_2_,		_upd_ml_,	_gcode_wipe,		WIPE_PRO_CRC_UPG,	WIPE_PRO_UPG,		WIPE_PLUS_CRC_UPG,	WIPE_PLUS_UPG),
	)
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Nozzle Wipe Settings"), workflow.opts.nozzle_wipe and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		assert workflow.opts.nozzle_wipe != 0, "This item is disabled, why got called?"
		# Validate state
		super().Do()
		self.RunPlan(self.PLAN, workflow.opts.nozzle_wipe)


class PurgeLine(StmtList_):
	PLAN =(
		# <cond>			<command>	<section/key>		<crc pro>				<b64 pro>			<crc plus>				<b64 plus>
		( _is_combo_1_,		_upd_ml_,	_gcode_line,		LINE_PRO_CRC_DEF,		LINE_PRO_DEF,		LINE_PLUS_CRC_DEF,		LINE_PLUS_DEF ),
		( _is_combo_2_,		_upd_ml_,	_gcode_line,		LINE_PRO_CRC_UPG,		LINE_PRO_UPG,		LINE_PLUS_CRC_UPG,		LINE_PLUS_UPG ),
		( _is_combo_3_,		_upd_ml_,	_gcode_line,		LINE_PRO_CRC_UPG,		LINE_PRO_UPG,		LINE_PLUS_CRC_UPG,		LINE_PLUS_UPG ),
		# <cond>			<command>	<section>			<crc pro>				<b64 pro>			<crc plus>				<b64 plus>
		( _is_combo_1_,		_upd_sec_,	_gcode_line_only,	None,					None,				None,					None ),
		( _is_combo_2_,		_upd_sec_,	_gcode_line_only,	LINE_ONLY_PRO_CRC_UPG,	LINE_ONLY_PRO_UPG,	LINE_ONLY_PLUS_CRC_UPG,	LINE_ONLY_PLUS_UPG ),
		( _is_combo_3_,		_upd_sec_,	_gcode_line_only,	LINE_ONLY_PRO_CRC_GRU,	LINE_ONLY_PRO_GRU,	LINE_ONLY_PLUS_CRC_GRU,	LINE_ONLY_PLUS_GRU ),
	)
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Purge Line Settings"), workflow.opts.purge_line and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		assert workflow.opts.purge_line != 0, "This item is disabled, why got called?"
		# Validate state
		super().Do()
		self.RunPlan(self.PLAN, workflow.opts.purge_line)


class M600Support(StmtList_):
	PLAN =(
		# <cond>			<command>	<section>			<crc pro>				<b64 pro>			<crc plus>				<b64 plus>
		( _always_,			_upd_sec_,	_beeper_pin_,		BEEPER_CRC_UPG,			BEEPER_UPG,			BEEPER_CRC_UPG,			BEEPER_UPG ),
		( _always_,			_upd_sec_,	_gcode_M300_,		M300_CRC_UPG,			M300_UPG,			M300_CRC_UPG,			M300_UPG ),
		( _is_combo_1_,		_upd_sec_,	_gcode_M600_,		M600_CRC_UPG,			M600_UPG,			M600_CRC_UPG,			M600_UPG ),
		( _is_combo_2_,		_upd_sec_,	_gcode_M600_,		M600_CRC_GRU,			M600_GRU,			M600_CRC_GRU,			M600_GRU ),
		( _always_,			_upd_sec_,	_gcode_T600_,		T600_CRC_UPG,			T600_UPG,			T600_CRC_UPG,			T600_UPG ),
	)
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Enable Filament Change (M600 Support)"), workflow.opts.enable_m600 and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		assert workflow.opts.enable_m600 != 0, "This item is disabled, why got called?"
		# Validate state
		super().Do()
		self.RunPlan(self.PLAN, workflow.opts.enable_m600)


class PauseMacro(StmtList_):
	PLAN =(
		# <cond>			<command>	<section>			<crc pro>				<b64 pro>			<crc plus>				<b64 plus>
		( _is_combo_1_,		_upd_ml_,	_gcode_pause_,		PAUSE_CRC_DEF,			PAUSE_DEF,			PAUSE_CRC_DEF,			PAUSE_DEF ),
		( _is_combo_2_,		_upd_ml_,	_gcode_pause_,		PAUSE_CRC_UPG,			PAUSE_UPG,			PAUSE_CRC_UPG,			PAUSE_UPG ),
		( _is_combo_3_,		_upd_ml_,	_gcode_pause_,		PAUSE_CRC_GRU,			PAUSE_GRU,			PAUSE_CRC_GRU,			PAUSE_GRU ),
	)
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Pause Macro Settings"), workflow.opts.pause and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		assert workflow.opts.pause != 0, "This item is disabled, why got called?"
		# Validate state
		super().Do()
		self.RunPlan(self.PLAN, workflow.opts.pause)


class SaveConfig(EditConfig_):
	def __init__(self, workflow : Workflow) -> None:
		super().__init__(workflow, N_("Save Configuration"), TaskState.READY)
	def Do(self):
		workflow = self.workflow
		if TEST_MODE is None:
			if workflow.sftp is None:
				raise Exception(N_("Connection is invalid to complete the command!"))
		super().Do()
		if (workflow.editor is not None) and (workflow.modify_cfg or workflow.persistence_upd):
			workflow.editor.Save()
			if TEST_MODE is None:
				dirname = Path(CONFIG_FILE).parent
				fname = dirname / workflow.backup_file
				workflow.ExecCommand(f"cp -f {CONFIG_FILE} {fname.as_posix()}")
				fname = dirname / f"printer.{str(random.randint(0, 9999999))}"
				workflow.SftpPut(self.target, fname.as_posix())
				workflow.ExecCommand(f"cp -f {fname.as_posix()} {CONFIG_FILE}")
				workflow.ExecCommand(f"chown mks:mks {CONFIG_FILE}")
				workflow.ExecCommand(f"rm {fname.as_posix()}")
				self.Info(_("\n\tSuccessfully saved file '{}'").format(CONFIG_FILE))

