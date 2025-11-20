#
# -*- coding: UTF-8 -*-


import os
import shutil
from datetime import datetime

from my_env import GetBackupFolder, Debug
from i18n import _, N_
from my_workflow import Task, TaskState, Workflow


class BackupConfig(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Backup Current Configuration"), TaskState.READY)
	def Do(self):
		workflow = self.workflow
		if workflow.sftp is None:
			raise Exception(N_("Connection is invalid to complete the command!"))
		super().Do()
		target = GetBackupFolder()
		if not os.path.isdir(target):
			os.makedirs(target)
		backup = os.path.join(target, datetime.now().strftime('printer_%Y%m%d-%H%M%S.cfg'))
		target = os.path.join(target, 'printer.cfg')
		Debug(f"SFTP /home/mks/klipper_config/printer.cfg '{target}'")
		workflow.sftp.get('/home/mks/klipper_config/printer.cfg', target)
		self.Info(_("\n\tSuccessfully copy file '{}'").format('/home/mks/klipper_config/printer.cfg'))
		if os.path.isfile(backup):
			os.unlink(backup)
		Debug(f"copy '{target}' '{backup}'")
		shutil.copyfile(target, backup)
		self.Info(_("\n\tCreated a backup in '{}'\n").format(backup))
