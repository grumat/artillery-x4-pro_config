#
# -*- coding: UTF-8 -*-


import time

from i18n import _, N_
from my_workflow import Workflow, Task, TaskState


class StopUserInterface(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Stopping User Interface Service"), TaskState.READY)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl stop makerbase-client", 60)
		self.Info(_("\n\tPrinter display is now unresponsive.\n"))

class StopWebCam(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Stopping WebCam Service"), TaskState.READY)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl stop makerbase-webcam", 60)

class StopMoonraker(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Stopping Moonraker Service"), TaskState.READY)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl stop moonraker-obico", 60)
		self.workflow.ExecCommand("systemctl stop moonraker", 60)
		self.Info(_("\n\tWeb access is down.\n"))

class StopKlipper(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Stopping Klipper Service"), TaskState.READY)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl stop klipper", 60)
		self.Info(_("\n\tKlipper is down.\n"))

class EnableUserInterface(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Enabling User Interface Service"), TaskState.CONNECTED)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl enable makerbase-client", 60)

class EnableWebCam(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Enabling WebCam Service"), TaskState.CONNECTED)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl enable makerbase-webcam", 60)

class EnableMoonraker(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Enabling Moonraker Service"), TaskState.CONNECTED)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl enable moonraker-obico", 60)
		self.workflow.ExecCommand("systemctl enable moonraker", 60)

class EnableKlipper(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Enabling Klipper Service"), TaskState.CONNECTED)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl enable klipper", 60)

class StartKlipper(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Starting Klipper Service"), TaskState.CONNECTED)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl start klipper", 120)
		self.Info(_("\n\tWaiting for Klipper to start..."))
		time.sleep(5)

class StartMoonraker(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Starting Moonraker Service"), TaskState.CONNECTED)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl start moonraker", 120)
		self.workflow.ExecCommand("systemctl start moonraker-obico", 120)
		self.Info(_("\n\tWaiting for Moonraker to start..."))
		time.sleep(3)

class StartWebCam(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Starting WebCam Service"), TaskState.CONNECTED)
	def Do(self):
		super().Do()
		self.Info(_("\n\tBe patient...\n"))
		self.workflow.ExecCommand("systemctl start makerbase-webcam", 150)

class StartUserInterface(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Starting User Interface Service"), TaskState.CONNECTED)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl start makerbase-client", 120)
		self.Info(_("\n\tWaiting for User Interface to start..."))
		time.sleep(10)

class FixCardResizeBug(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Fix for card resize bug"), workflow.opts.resize_bug and TaskState.READY or TaskState.DISABLED)
	def UpdateState(self):
		super().UpdateState()
		if self.CanFail() and self.workflow.resizing_issue == False:
			self.SetState(TaskState.DISABLED)
	def Do(self):
		super().Do()
		# spellchecker:disable-next-line
		self.workflow.ExecCommand("systemctl disable armbian-resize-filesystem", 60)
