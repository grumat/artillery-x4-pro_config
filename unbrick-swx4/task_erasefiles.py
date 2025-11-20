#
# -*- coding: UTF-8 -*-


from i18n import _, N_
from my_workflow import Workflow, Task, TaskState


# spellchecker: disable
# Where to find .gcode files
DELETE_GCODE = [
	'/home/mks/gcode_files',
]

# Where to find miniatures
DELETE_MINIATURE = [
	"/home/mks/simage_space/",
	"/home/mks/Videos/",
]

# Where to find config files
DELETE_CONFIGS = [
	"/home/mks/klipper_config/.moonraker.conf.bkp",
	"/home/mks/klipper_config/printer-2*.cfg",
]

# Where to find log files
DELETE_LOGS = [
	"/home/mks/klipper_logs/timelapse/",
	"/home/mks/klipper_logs/",
	"/home/mks/Desktop/myfile/ws/debug_log.txt",
]

# Useless files that are found on the printer
DELETE_CLUTTER_FILES = [
	"/home/mks/.bash_history", 
	"/home/mks/.gitconfig", 
	"/home/mks/.viminfo", 
	"/home/mks/auto-webcam-id.sh", 
	"/home/mks/moonraker-obico-master.zip", 
	"/home/mks/moonraker-timelapse-main.zip", 
	"/home/mks/plrtmpA.1606", 
	"/home/mks/update_3b3bdc8.deb", 
	"/home/mks/update_50701cc.deb", 
	"/home/mks/update_f263f3d.deb", 
	"/home/mks/webcam.txt", 
	"/home/mks/Desktop/myfile/database.db", 
	"/home/mks/Desktop/myfile/ws/build/src/database.db", 
	"/home/mks/Desktop/myfile/ws.bak/build/mksclient", 
]

DELETE_CLUTTER_FOLDERS = [
	"/home/mks/moonraker-timelapse-main"
]

class _EraseFileList(Task):
	def __init__(self, workflow : "Workflow", title : str, state : TaskState) -> None:
		super().__init__(workflow, title, state)
	def _info(self, fname : str, qry : bool):
		if qry:
			self.Info(_('\n\tSearching {}...').format(fname))
		else:
			self.Info(_('\n\t\tDeleting {}...').format(fname))

class EraseGcodeFiles(_EraseFileList):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Erase .gcode files"), workflow.opts.optimize_disk_space and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()
		cnt = self.workflow.DelFileMatch(DELETE_GCODE, self._info)
		self.Bold(_("\n\tRemoved {} .gcode files.\n").format(cnt))

class EraseMiniatures(_EraseFileList):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Erase miniature files"), workflow.opts.optimize_disk_space and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		cnt = self.workflow.DelFileMatch(DELETE_MINIATURE, self._info)
		self.Bold(_("\n\tRemoved {} miniature files.\n").format(cnt))

class EraseOldConfig(_EraseFileList):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Erase old configuration files"), workflow.opts.optimize_disk_space and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()
		cnt = self.workflow.DelFileMatch(DELETE_CONFIGS, self._info)
		self.Bold(_("\n\tRemoved {} old configuration files.\n").format(cnt))

class EraseLogFiles(_EraseFileList):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Erase log files"), workflow.opts.optimize_disk_space and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()
		cnt = self.workflow.DelFileMatch(DELETE_LOGS, self._info)
		self.Bold(_("\n\tRemoved {} log files.\n").format(cnt))

class EraseClutterFiles(_EraseFileList):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Erase Artillery clutter files"), workflow.opts.optimize_disk_space and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()
		cnt = self.workflow.DelFileMatch(DELETE_CLUTTER_FILES, self._info)
		# Entire Folders
		cnt += self.workflow.DelTreeMatch(DELETE_CLUTTER_FOLDERS, self._info)
		self.Info(_("\n\tRemoved {} unneeded files.\n").format(cnt))
