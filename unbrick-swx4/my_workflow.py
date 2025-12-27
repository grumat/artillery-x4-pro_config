#
# -*- coding: UTF-8 -*-
#
# spellchecker:words erasefiles USWX klipper gcode


import os
import tkinter as tk
import queue
import threading
import time
from enum import Enum
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

TEST_MODE = os.getenv("USWX4_TEST")

if TYPE_CHECKING:
	from .user_options import UserOptions
	from .i18n import _, N_
	from .my_env import Info, Error, GetBackupFolder, GetMainScriptPath, YELLOW, NORMAL, BOLD, RED, GREEN
	from .my_shell import ArtillerySideWinder, DiskUsage
	from .edit_cfg import Commands
else:
	from user_options import UserOptions
	from i18n import _, N_
	from my_env import Info, Error, GetBackupFolder, GetMainScriptPath, YELLOW, NORMAL, BOLD, RED, GREEN
	from my_shell import ArtillerySideWinder, DiskUsage
	from edit_cfg import Commands



class MessageType(Enum):
	NORMAL = "normal"
	SUCCESS = "success"
	ACTION = "action"
	BOLD = "bold"
	WARNING = "warning"
	ERROR = "error"


class Message:
	def __init__(self, t : MessageType, msg : str) -> None:
		self.type = t
		self.msg = msg


class TaskState(Enum):
	DISABLED = 0	# Disabled by user interface
	READY = 1		# task is waiting for its time
	ALWAYS = 2		# run always, regardless of connection/error state
	CONNECTED = 3	# run always if a connection was established, regardless of error state
	RUNNING = 4		# Task being run (one at a time)
	DONE = 5		#  task 
	CANCELLED = 6
	FAIL = 7

class Task(ABC):
	def __init__(self, workflow : "Workflow", label : str, state : TaskState) -> None:
		self.workflow = workflow
		self.label = label
		self.state = state
	@abstractmethod
	def Do(self):
		if self.state == TaskState.DISABLED:
			raise Exception("This item is disabled, why got called?")
		time.sleep(0.2)
	def CanRun(self) -> bool:
		return self.state in (TaskState.RUNNING, TaskState.READY, TaskState.ALWAYS, TaskState.CONNECTED)
	def CanFail(self) -> bool:
		return self.state in (TaskState.RUNNING, TaskState.READY)
	def SetState(self, state : TaskState) -> None:
		if self.state != state:
			self.state = state
			self.workflow.UpdateUI(self)
	def UpdateState(self) -> None:
		workflow = self.workflow
		if self.CanFail():
			if workflow.exception or workflow.failed_connection:
				self.SetState(TaskState.FAIL)
			elif workflow.cancel_flag:
				self.SetState(TaskState.CANCELLED)
		elif (self.state == TaskState.CONNECTED) and workflow.failed_connection:
				self.SetState(TaskState.FAIL)
	def Bold(self, msg : str) -> None:
		self.workflow.UpdateUI(Message(MessageType.BOLD, msg))
	def Info(self, msg : str) -> None:
		self.workflow.UpdateUI(Message(MessageType.NORMAL, msg))
	def Warning(self, msg : str) -> None:
		self.workflow.UpdateUI(Message(MessageType.WARNING, msg))
	def Success(self, msg : str) -> None:
		self.workflow.UpdateUI(Message(MessageType.SUCCESS, msg))


#class MinTemplate(Task):
#	def __init__(self, workflow : "Workflow") -> None:
#		super().__init__(workflow, N_("..."), TaskState.READY)
#	def Do(self):
#		super().Do()


class Workflow(ArtillerySideWinder):
	" Class to run all operations "
	def __init__(self, opts : UserOptions) -> None:
		super().__init__()
		self.opts = opts
		self.exception = False
		self.cancel_flag = False
		self.resizing_issue = False
		if (TEST_MODE is None):
			self.queue : queue.Queue
			self.thread : threading.Thread
			self.dlg : tk.Misc
		self.start_space = DiskUsage()
		self.end_space = DiskUsage()
		self.editor : Commands|None = None

		self.tasks : list[Task] = []
		# Variables used during Gcode edit
		self.backup_file = "" 
		self.upgraded_cfg = False		# The cfg file has already upgraded Artillery gcode
		self.modify_cfg = 0				# A counter having the number of edits on the configuration file
		self.persistence_upd = False	# Indicates that persistence area has been updated

		if (TEST_MODE is None):
			if TYPE_CHECKING:
				from .task_permissions import FixFilePermission, FixHomePermission
				from .task_connect import Connect, CheckConnect, Disconnect
				from .task_disk import GetInitialDiskSpace, GetFinalDiskSpace, TrimDisk
				from .task_services import StopKlipper, StartKlipper, EnableKlipper, StopMoonraker, StartMoonraker, EnableMoonraker, \
						StopUserInterface, StartUserInterface, EnableUserInterface, StopWebCam, StartWebCam, EnableWebCam, FixCardResizeBug
				from .task_erasefiles import EraseGcodeFiles, EraseMiniatures, EraseLogFiles, EraseOldConfig, EraseClutterFiles
			else:
				from task_permissions import FixFilePermission, FixHomePermission
				from task_connect import Connect, CheckConnect, Disconnect
				from task_disk import GetInitialDiskSpace, GetFinalDiskSpace, TrimDisk
				from task_services import StopKlipper, StartKlipper, EnableKlipper, StopMoonraker, StartMoonraker, EnableMoonraker, \
						StopUserInterface, StartUserInterface, EnableUserInterface, StopWebCam, StartWebCam, EnableWebCam, FixCardResizeBug
				from task_erasefiles import EraseGcodeFiles, EraseMiniatures, EraseLogFiles, EraseOldConfig, EraseClutterFiles
		if TYPE_CHECKING:
			from .task_config import BackupConfig, ConfigReset, ConfigValidate, FixModelSettings, StepperZCurrent, ExtruderAccel, ExtruderCurrent, \
						ProbeOffset, ProbeSampling, ProbeValidation, ScrewsTiltAdjust, FanRename, MbFanFix, MbFanSpeed, HbFanSpeed, TempMCU, \
						NozzleWipe, PurgeLine, M600Support, PauseMacro, ExcludeObject, SaveConfig
		else:
			from task_config import BackupConfig, ConfigReset, ConfigValidate, FixModelSettings, StepperZCurrent, ExtruderAccel, ExtruderCurrent, \
						ProbeOffset, ProbeSampling, ProbeValidation, ScrewsTiltAdjust, FanRename, MbFanFix, MbFanSpeed, HbFanSpeed, TempMCU, \
						NozzleWipe, PurgeLine, M600Support, PauseMacro, ExcludeObject, SaveConfig

		if (TEST_MODE is None):
			self.tasks.append(Connect(self))
			self.tasks.append(CheckConnect(self))
			self.tasks.append(GetInitialDiskSpace(self))
			self.tasks.append(StopUserInterface(self))
			self.tasks.append(StopWebCam(self))
			self.tasks.append(StopMoonraker(self))
			self.tasks.append(StopKlipper(self))
			self.tasks.append(EraseGcodeFiles(self))
			self.tasks.append(EraseMiniatures(self))
			self.tasks.append(EraseOldConfig(self))
			self.tasks.append(EraseLogFiles(self))
			self.tasks.append(EraseClutterFiles(self))
			self.tasks.append(FixFilePermission(self))
			self.tasks.append(FixHomePermission(self))
			self.tasks.append(FixCardResizeBug(self))

		self.tasks.append(BackupConfig(self))
		self.tasks.append(ConfigReset(self))
		self.tasks.append(ConfigValidate(self))
		self.tasks.append(FixModelSettings(self))
		self.tasks.append(ExcludeObject(self))
		self.tasks.append(StepperZCurrent(self))
		self.tasks.append(ExtruderAccel(self))
		self.tasks.append(ExtruderCurrent(self))
		self.tasks.append(ProbeOffset(self))
		self.tasks.append(ProbeSampling(self))
		self.tasks.append(ProbeValidation(self))
		self.tasks.append(ScrewsTiltAdjust(self))
		self.tasks.append(FanRename(self))
		self.tasks.append(MbFanFix(self))
		self.tasks.append(MbFanSpeed(self))
		self.tasks.append(HbFanSpeed(self))
		self.tasks.append(TempMCU(self))
		self.tasks.append(NozzleWipe(self))
		self.tasks.append(PurgeLine(self))
		self.tasks.append(M600Support(self))
		self.tasks.append(PauseMacro(self))
		# Always the last of this block
		self.tasks.append(SaveConfig(self))

		if (TEST_MODE is None):
			self.tasks.append(TrimDisk(self))
			self.tasks.append(GetFinalDiskSpace(self))
			self.tasks.append(EnableUserInterface(self))
			self.tasks.append(EnableWebCam(self))
			self.tasks.append(EnableMoonraker(self))
			self.tasks.append(EnableKlipper(self))
			self.tasks.append(StartKlipper(self))
			self.tasks.append(StartMoonraker(self))
			self.tasks.append(StartWebCam(self))
			self.tasks.append(StartUserInterface(self))
			# Always the Last
			self.tasks.append(Disconnect(self))

	def UpdateUI(self, task: Task|Message|int|None):
		if (TEST_MODE is None):
			self.queue.put(task)
			self.dlg.event_generate("<<UpdateUI>>", when="tail")
		elif isinstance(task, Message):
			if task.type == MessageType.BOLD:
				print(BOLD, end='')
			elif task.type == MessageType.ERROR:
				print(RED, end='')
			elif task.type == MessageType.SUCCESS:
				print(GREEN, end='')
			elif task.type == MessageType.WARNING:
				print(YELLOW, end='')
			print(task.msg, end='')
			if task.type != MessageType.NORMAL:
				print(NORMAL, end='')

	def _update_states(self):
		for task in self.tasks:
			try:
				task.UpdateState()
			except Exception as e:
				error_message = str(e)
				self.exception = True
				self._set_task_state(task, TaskState.FAIL)
				Error(f'{error_message}\n')
				self.UpdateUI(Message(MessageType.ERROR, _('ERROR!') + '\n\t' + _(error_message) + '\n'))

	def _update_progress(self, cnt : int):
		for task in self.tasks:
			cnt += task.CanRun()
		return cnt

	def _set_task_state(self, task : Task, state : TaskState) -> None:
		task.state = state
		self.UpdateUI(task)

	if (TEST_MODE is None):
		def _worker_thread(self):
			cnt = 0
			for i, task in enumerate(self.tasks):
				self._update_states()
				if task.CanRun():
					total = self._update_progress(cnt)
					cnt += 1
					if total == 0:
						self.UpdateUI(100)
					else:
						self.UpdateUI((cnt * 100 + total//2) // total)
					try:
						Info(f'Begin Step: {task.label}...')
						self.UpdateUI(Message(MessageType.ACTION, _('Begin Step: ') + _(task.label) + '...  '))
						self._set_task_state(task, TaskState.RUNNING)
						task.Do()
						self.UpdateUI(Message(MessageType.ACTION, _('OK!') + '\n'))
						Info('  OK!')
						self._set_task_state(task, TaskState.DONE)
					except Exception as e:
						error_message = str(e)
						self.exception = True
						self._set_task_state(task, TaskState.FAIL)
						Error(f'{error_message}\n')
						self.UpdateUI(Message(MessageType.ERROR, _('ERROR!') + '\n\t' + _(error_message) + '\n'))
			self.UpdateUI(100)
			if self.persistence_upd:
				msg = N_("Printer configuration has been reset, printer needs recalibration.")
				Warning(msg)
				self.UpdateUI(Message(MessageType.BOLD, _(msg)))
			self._update_states()
			time.sleep(0.5)			# give time for user knowledge
			self.UpdateUI(None)

	def Do(self, dlg : tk.Misc, queue : queue.Queue):
		self.dlg = dlg
		self.queue = queue
		if (TEST_MODE is None):
			self.thread = threading.Thread(target=self._worker_thread)
			self.thread.start()

	def Test(self, test_name : str):
		import fnmatch
		temp_dir = os.path.join(GetMainScriptPath(), "temp")
		pat = f"{test_name}-??-*.cfg"
		for f in os.listdir(temp_dir):
			if fnmatch.fnmatch(f, pat):
				fp = os.path.join(temp_dir, f)
				os.unlink(fp)
		i = 0
		for task in self.tasks:
			cnt_ref = self.modify_cfg
			self._update_states()
			if task.CanRun():
				try:
					self.UpdateUI(Message(MessageType.ACTION, _('Begin Step: ') + _(task.label) + '...  '))
					self._set_task_state(task, TaskState.RUNNING)
					task.Do()
					self.UpdateUI(Message(MessageType.ACTION, _('OK!') + '\n'))
					self._set_task_state(task, TaskState.DONE)
					if (i == 0) or (cnt_ref != self.modify_cfg):
						if not os.path.isdir(temp_dir):
							os.makedirs(temp_dir)
						fname = os.path.join(temp_dir, f"{test_name}-{i:02}-{type(task).__name__}.cfg")
						if self.editor:
							self.editor.contents.file_buffer.Save(fname)
						i += 1
				except Exception as e:
					error_message = str(e)
					self.exception = True
					self._set_task_state(task, TaskState.FAIL)
					Error(f'{error_message}\n')
					self.UpdateUI(Message(MessageType.ERROR, _('ERROR!') + '\n\t' + _(error_message) + '\n'))
		if self.editor:
			self.editor.Save()
		if self.persistence_upd:
			msg = N_("Printer configuration has been reset, printer needs recalibration.")
			Warning(msg)
			self.UpdateUI(Message(MessageType.BOLD, '\n' + _(msg) + '\n'))

