#
# -*- coding: UTF-8 -*-

import time

from my_lib import FmtByteSize
from i18n import _, N_
from my_workflow import Workflow, Task, TaskState


class GetInitialDiskSpace(Task):
	def __init__(self, workflow : Workflow) -> None:
		super().__init__(workflow, N_("Reading initial disk space"), TaskState.READY)
	def Do(self):
		workflow = self.workflow
		workflow.start_space = workflow.GetFreeScape()
		self.Info(_("\n\tBoot partition total size: {0}").format(FmtByteSize(workflow.start_space.boot_size)))
		self.Info(_("\n\tBoot partition free size: {0}").format(FmtByteSize(workflow.start_space.boot_free)))
		self.Info(_("\n\tRoot partition total size: {0}").format(FmtByteSize(workflow.start_space.root_size)))
		self.Info(_("\n\tRoot partition free size: {0}").format(FmtByteSize(workflow.start_space.root_free)) + '\n')


class GetFinalDiskSpace(Task):
	def __init__(self, workflow : Workflow) -> None:
		super().__init__(workflow, N_("Reading final disk space"), TaskState.READY)
	def Do(self):
		workflow = self.workflow
		workflow.end_space = workflow.GetFreeScape()
		self.Info(_("\n\tBoot partition total size: {0}").format(FmtByteSize(workflow.end_space.boot_size)))
		self.Info(_("\n\tBoot partition free size: {0}").format(FmtByteSize(workflow.end_space.boot_free)))
		self.Info(_("\n\tRoot partition total size: {0}").format(FmtByteSize(workflow.end_space.root_size)))
		self.Info(_("\n\tRoot partition free size: {0}").format(FmtByteSize(workflow.end_space.root_free)) + '\n')


class TrimDisk(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Trimming eMMC disk"), workflow.opts.trim and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()
		self.Info(_('\n\tFlushing file data...\n'))
		self.workflow.ExecCommand("sync", 20)
		time.sleep(1)
		self.Info(_('\n\tTrimming eMMC...\n'))
		self.workflow.ExecCommand("fstrim /", 60)
		# Lets give a resting time for file-system
		time.sleep(4)
