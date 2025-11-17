#
# -*- coding: UTF-8 -*-

N_ = lambda t : t

from enum import Enum
import tkinter as tk
import queue
import threading
import time
import paramiko

import UserOptions
from i18n import _
from myenv import *


USERNAME = 'mks'
PASSWORD = 'makerbase'


class MessageType(Enum):
	NORMAL = "normal"
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
	RUNNING = 3		# Task being run (one at a time)
	DONE = 4		#  task 
	FAIL = 5

class Task:
	def __init__(self, workflow : "Workflow", label : str, state : TaskState) -> None:
		self.workflow = workflow
		self.label = label
		self.state = state
	def Do(self):
		time.sleep(0.2)
	def CanRun(self) -> bool:
		return self.state in (TaskState.RUNNING, TaskState.READY, TaskState.ALWAYS)
	def CanFail(self) -> bool:
		return self.state in (TaskState.RUNNING, TaskState.READY)
	def UpdateState(self):
		if self.CanFail():
			workflow = self.workflow
			if workflow.exception or workflow.failed_connection or workflow.cancel_flag:
				self.state = TaskState.FAIL
				workflow.UpdateUI(self)

class Connect(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Connecting to printer using SSH"), TaskState.ALWAYS)
	def Do(self):
		self.workflow.client.connect(hostname=self.workflow.opts.ip_addr, username=USERNAME, password=PASSWORD)
		Info("SSH connection established.")
		self.workflow.sftp = self.workflow.client.open_sftp()

class Disconnect(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Disconnecting SSH Client"), TaskState.ALWAYS)
	def Do(self):
		workflow = self.workflow
		if hasattr(workflow, 'sftp') and workflow.sftp:
			workflow.sftp.close()

class CheckConnect(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Check if Artillery Sidewinder X4 Printer Connected"), TaskState.READY)
	def Do(self):
		super().Do()

class StopUserInterface(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Stopping User Interface Service"), TaskState.READY)
	def Do(self):
		super().Do()

class StopWebCam(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Stopping WebCam Service"), TaskState.READY)
	def Do(self):
		super().Do()

class StopMoonraker(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Stopping Moonraker Service"), TaskState.READY)
	def Do(self):
		super().Do()

class StopKlipper(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Stopping Klipper Service"), TaskState.READY)
	def Do(self):
		super().Do()

class EraseGcodeFiles(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Erase .gcode files"), workflow.opts.optimize_disk_space and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()

class EraseMiniatures(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Erase miniature files"), workflow.opts.optimize_disk_space and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()

class EraseOldConfig(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Erase old configuration files"), workflow.opts.optimize_disk_space and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()

class EraseLogFiles(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Erase log files"), workflow.opts.optimize_disk_space and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()

class EraseClutterFiles(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Erase Artillery clutter files"), workflow.opts.optimize_disk_space and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()

class FixFilePermission(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Fix file permission"), workflow.opts.file_permissions and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()

class FixCardResizeBug(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Fix for card resize bug"), workflow.opts.resize_bug and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()

class TrimDisk(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Trimming eMMC disk"), workflow.opts.trim and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()

class EnableUserInterface(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Enabling User Interface Service"), TaskState.READY)
	def Do(self):
		super().Do()

class EnableWebCam(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Enabling WebCam Service"), TaskState.READY)
	def Do(self):
		super().Do()

class EnableMoonraker(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Enabling Moonraker Service"), TaskState.READY)
	def Do(self):
		super().Do()

class EnableKlipper(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Enabling Klipper Service"), TaskState.READY)
	def Do(self):
		super().Do()

class StartKlipper(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Enabling Klipper Service"), TaskState.READY)
	def Do(self):
		super().Do()

class StartMoonraker(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Enabling Moonraker Service"), TaskState.READY)
	def Do(self):
		super().Do()

class StartWebCam(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Enabling WebCam Service"), TaskState.READY)
	def Do(self):
		super().Do()

class StartUserInterface(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Enabling User Interface Service"), TaskState.READY)
	def Do(self):
		super().Do()



class Workflow(object):
	" Class to run all operations "
	def __init__(self, opts : UserOptions.UserOptions) -> None:
		self.opts = opts
		self.connected = False
		self.exception = False
		self.failed_connection = False
		self.cancel_flag = False
		self.dlg : tk.Misc
		self.queue : queue.Queue
		self.thread : threading.Thread
		self.client = paramiko.SSHClient()
		self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.sftp : paramiko.SFTPClient
		self.tasks : list[Task] = []
		self.tasks.append(Connect(self))
		self.tasks.append(CheckConnect(self))
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
		self.tasks.append(FixCardResizeBug(self))
		self.tasks.append(TrimDisk(self))
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
		self.queue.put(task)
		self.dlg.event_generate("<<UpdateUI>>", when="tail")

	def _update_states(self):
		for task in self.tasks:
			try:
				task.UpdateState()
			except Exception as e:
				self.exception = True

	def _update_progress(self, cnt : int):
		for task in self.tasks:
			cnt += task.CanRun()
		return cnt

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
					Info(f'Running {task.label}...')
					self.UpdateUI(Message(MessageType.NORMAL, _(task.label) + ': ' + _('Running...') + '  '))
					task.state = TaskState.RUNNING
					self.UpdateUI(task)
					task.Do()
					self.UpdateUI(Message(MessageType.BOLD, _('OK!') + '\n'))
					Info('  OK!')
					task.state = TaskState.DONE
					self.UpdateUI(task)
				except Exception as e:
					error_message = str(e)
					self.exception = True
					task.state = TaskState.FAIL
					Error(f'{error_message}\n')
					self.UpdateUI(Message(MessageType.ERROR, _('ERROR!') + '\n\t' + _(error_message) + '\n'))
		self.UpdateUI(100)
		self._update_states()
		time.sleep(0.5)			# give time for user knowledge
		self.UpdateUI(None)

	def Do(self, dlg : tk.Misc, queue : queue.Queue):
		self.dlg = dlg
		self.queue = queue
		self.thread = threading.Thread(target=self._worker_thread)
		self.thread.start()

