#
# -*- coding: UTF-8 -*-
#
# Spellchecker: words mkspi, klipper, rockchip

import os
import time
import re

from my_env import Debug
from i18n import _, N_
from my_lib import FmtByteSize
from my_workflow import Task, TaskState, Workflow


class Connect(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Connecting to printer using SSH"), TaskState.ALWAYS)
	def Do(self):
		workflow = self.workflow
		workflow.Connect(workflow.opts.ip_addr)
		self.Info(_("\n\tSSH connection established."))

class CheckConnect(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Check if Artillery Sidewinder X4 Printer Connected"), TaskState.READY)
	def Do(self):
		found = 0
		# Find in motd the 'mkspi' login prompt
		for line in self.workflow.motd_output:
			if line.startswith('root@mkspi:'):
				found += 1
				break
			elif "a reboot is needed to finish resizing the filesystem" in line:
				self.workflow.resizing_issue = True

		if found != 1:
			Debug('\n'.join(self.workflow.motd_output))
		else:
			time.sleep(0.2)
			# Check `uname -a` results
			res = self.workflow.ExecCommand('uname -a')
			if len(res):
				m = re.match(r'Linux mkspi (\d+\.\d+\.\d+)-rockchip64 .*', res[0])
				if m:
					msg = _('\n\tDetected OS is Linux mkspi {0}\n').format(m[1])
					self.Info(msg)
					found += 1
		if found != 2:
			self.Warning(_("Failed to retrieve OS version information!\n"))
		else:
			time.sleep(0.2)
			# Check `./get_id` mkspi utility and verify MCU model
			res = self.workflow.ExecCommand('./get_id')
			for line in res:
				line = line.strip()
				m = re.match(r'/dev/serial/by-id/usb-Klipper_stm32f401xc_[A-Z0-9]{24}-if00', line)
				if m:
					msg = _('\tMCU STM32F401XC found on {0}\n').format(line)
					self.Info(msg)
					found += 1
					break
		if found != 3:
			self.Warning(_("Failed to retrieve MCU Klipper connection!\n"))
		else:
			time.sleep(0.2)
			# Check `ls -1 /home/mks/Desktop/myfile/others/artillery_X4_*.cfg` to find configuration restore files
			res = self.workflow.ExecCommand('ls -1 /home/mks/Desktop/myfile/others/artillery_X4_*.cfg')
			for line in res:
				line = line.strip()
				m = re.match(r'/home/mks/Desktop/myfile/others/artillery_X4_(.+)\.cfg', line)
				if m:
					found += int(m[1] in ('max', 'plus', 'pro'))
					msg = _("\tDefault printer configuration file '{0}' was found\n").format(os.path.basename(line))
					self.Info(msg)
				else:
					found = 100
			if found != 6:
				self.Warning(_('One of the configuration file is missing!\n'))
		if found != 6:
			raise Exception(N_("The connection does not report an Artillery SW X4 printer"))

class Disconnect(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Disconnecting SSH Client"), TaskState.ALWAYS)
	def Do(self):
		super().Do()
		workflow = self.workflow
		if workflow.end_space.root_free > workflow.start_space.root_free:
			self.Bold(_("\n\n\tRecovered disk space: {}\n").format(FmtByteSize(workflow.end_space.root_free - workflow.start_space.root_free)))
		if (workflow.exception == False) \
			and (workflow.failed_connection == False) \
			and (workflow.cancel_flag == False):
			workflow.reboot_on_exit = True
			Warning('Rebooting printer')
			self.Warning(_("\n\tRebooting printer\n"))
		self.workflow.Disconnect()
