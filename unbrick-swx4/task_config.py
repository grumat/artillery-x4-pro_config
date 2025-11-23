#
# -*- coding: UTF-8 -*-
#
# Spellchecker: words USWX klipper


import os
import shutil
from datetime import datetime
from typing import TYPE_CHECKING

TEST_MODE = os.getenv("USWX4_TEST")

from my_env import GetBackupFolder, GetAssetsFolder, Debug
from i18n import _, N_
from edit_cfg import EditConfig

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
		res = EditConfig(cmd_line)
		if res.IsString() and isinstance(res.value, str):
			return res.value
		raise Exception(f"{res}")

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
		# Optionally recover configuration
		cal = None
		if workflow.opts.reset == 1:
			res = EditConfig(["GetSave", self.target])
			if res.code != '*':
				raise Exception(f"{res}")
			if not isinstance(res.value, str):
				raise ValueError("Data type value is unexpected")
			cal = res.value
		# Use the latest Artillery upgrade file, according to printer model
		if workflow.opts.IsArtillerySWX4Pro():
			source = os.path.join(GetAssetsFolder(), 'artillery_X4_pro.upg.cfg')
		else:
			source = os.path.join(GetAssetsFolder(), 'artillery_X4_plus.upg.cfg')
		# Replace current configuration file
		os.unlink(self.target)
		shutil.copyfile(source, self.target)
		# Optionally restore printer settings
		if cal is not None:
			res = EditConfig(["Save", cal, self.target])


class FixModelSettings(EditConfig_):
	def __init__(self, workflow: Workflow) -> None:
		super().__init__(workflow, N_("Fix Printer Model Settings"), workflow.opts.model_attr and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		workflow = self.workflow
		# Validate state
		if workflow.opts.model_attr == False:
			raise Exception("This item is disabled, why got called?")
		super().Do()
		super().Validate()
		# Changes for Artillery Sizewinder X4 Pro
		x_max = self.GetLine(["GetKey", "stepper_x", "position_max", self.target ])
		y_dir = self.GetLine(["GetKey", "stepper_y", "dir_pin", self.target ])
		y_min = self.GetLine(["GetKey", "stepper_y", "position_min", self.target ])
		y_stop = self.GetLine(["GetKey", "stepper_y", "position_endstop", self.target ])
		y_max = self.GetLine(["GetKey", "stepper_y", "position_max", self.target ])
		z_max = self.GetLine(["GetKey", "stepper_z", "position_max", self.target ])
		if workflow.opts.IsArtillerySWX4Pro():
			pass













