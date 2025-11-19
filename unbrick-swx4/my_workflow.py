#
# -*- coding: UTF-8 -*-

N_ = lambda t : t

from enum import Enum
import tkinter as tk
import queue
import threading
import time
import paramiko
import re
import select # Use the standard select module for checking readiness
import locale
import fnmatch
import shlex

import UserOptions
from i18n import _
from myenv import *
from mylib import *


USERNAME = 'root'
PASSWORD = 'makerbase'


class ArtSW4:
	"""
	Properties common to Artillery SideWinder 4
	"""
	LOGIN_PROMPTS = ('root@mkspi', 'mks@mkspi')
	@staticmethod
	def IsLoginPrompt(line : str) -> bool:
		for p in ArtSW4.LOGIN_PROMPTS:
			if line.startswith(p):
				return True
		return False

class DiskUsage:
	"""
	A record to store disk size information.
	"""
	def __init__(self):
		self.total = 0
		self.boot_size = 0
		self.boot_free = 0
		self.root_size = 0
		self.root_free = 0


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
	CONNECTED = 3	# run always if a connection was established, regardless of error state
	RUNNING = 4		# Task being run (one at a time)
	DONE = 5		#  task 
	FAIL = 6

class Task:
	def __init__(self, workflow : "Workflow", label : str, state : TaskState) -> None:
		self.workflow = workflow
		self.label = label
		self.state = state
	def Do(self):
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
			if workflow.exception or workflow.failed_connection or workflow.cancel_flag:
				self.SetState(TaskState.FAIL)
		elif (self.state == TaskState.CONNECTED) and workflow.failed_connection:
				self.SetState(TaskState.FAIL)
	def Bold(self, msg : str) -> None:
		self.workflow.UpdateUI(Message(MessageType.BOLD, msg))
	def Info(self, msg : str) -> None:
		self.workflow.UpdateUI(Message(MessageType.NORMAL, msg))
	def Warning(self, msg : str) -> None:
		self.workflow.UpdateUI(Message(MessageType.WARNING, msg))
	@staticmethod
	def FmtByteSize(num : int) -> str:
		if num > 1100000:
			num = float(num) / (1000.0 * 1000.0)
			sc = _(" GBi")
		elif num > 1100:
			num = float(num) / 1000.0
			sc = _(" MBi")
		else:
			num = float(num)
			sc = _(" KBi")
		res = locale.format_string("%5.3f", num, grouping=True)
		return res + sc


#class MinTemplate(Task):
#	def __init__(self, workflow : "Workflow") -> None:
#		super().__init__(workflow, N_("..."), TaskState.READY)
#	def Do(self):
#		super().Do()


class Connect(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Connecting to printer using SSH"), TaskState.ALWAYS)
	def Do(self):
		self.workflow.Connect()

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
			res = self.workflow.ExecCommandEx('uname -a')
			if len(res):
				m = re.match(r'Linux mkspi (\d+\.\d+\.\d+)-rockchip64 .*', res[0])
				if m:
					msg = _('\n\tDetected OS is Linux mkspi {0}\n').format(m[1])
					self.Info(msg)
					found += 1
		if found != 2:
			self.Warning(_("Failed to retrieve OS version information!"))
		else:
			time.sleep(0.2)
			# Check `./get_id` mkspi utility and verify MCU model
			res = self.workflow.ExecCommandEx('./get_id')
			for line in res:
				line = line.strip()
				m = re.match(r'/dev/serial/by-id/usb-Klipper_stm32f401xc_[A-Z0-9]{24}-if00', line)
				if m:
					msg = _('\tMCU STM32F401XC found on {0}\n').format(line)
					self.Info(msg)
					found += 1
					break
		if found != 3:
			self.Warning(_("Failed to retrieve MCU Klipper connection!"))
		else:
			time.sleep(0.2)
			# Check `ls -1 /home/mks/Desktop/myfile/others/artillery_X4_*.cfg` to find configuration restore files
			res = self.workflow.ExecCommandEx('ls -1 /home/mks/Desktop/myfile/others/artillery_X4_*.cfg')
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

class GetInitialDiskSpace(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Reading initial disk space"), TaskState.READY)
	def Do(self):
		workflow = self.workflow
		workflow.start_space = workflow.GetFreeScape()
		self.Info(_("\n\tBoot partition total size: {0}").format(Task.FmtByteSize(workflow.start_space.boot_size)))
		self.Info(_("\n\tBoot partition free size: {0}").format(Task.FmtByteSize(workflow.start_space.boot_free)))
		self.Info(_("\n\tRoot partition total size: {0}").format(Task.FmtByteSize(workflow.start_space.root_size)))
		self.Info(_("\n\tRoot partition free size: {0}").format(Task.FmtByteSize(workflow.start_space.root_free)) + '\n')

class GetFinalDiskSpace(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Reading final disk space"), TaskState.READY)
	def Do(self):
		workflow = self.workflow
		workflow.end_space = workflow.GetFreeScape()
		self.Info(_("\n\tBoot partition total size: {0}").format(Task.FmtByteSize(workflow.end_space.boot_size)))
		self.Info(_("\n\tBoot partition free size: {0}").format(Task.FmtByteSize(workflow.end_space.boot_free)))
		self.Info(_("\n\tRoot partition total size: {0}").format(Task.FmtByteSize(workflow.end_space.root_size)))
		self.Info(_("\n\tRoot partition free size: {0}").format(Task.FmtByteSize(workflow.end_space.root_free)))
		if workflow.end_space.root_free > workflow.start_space.root_free:
			self.Bold(_("\n\tRecovered disk space: {0}").format(Task.FmtByteSize(workflow.end_space.root_free - workflow.start_space.root_free)) + '\n')

class StopUserInterface(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Stopping User Interface Service"), TaskState.READY)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl stop makerbase-client")
		self.Info(_("\n\tPrinter display is now unresponsive.\n"))

class StopWebCam(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Stopping WebCam Service"), TaskState.READY)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl stop makerbase-webcam")

class StopMoonraker(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Stopping Moonraker Service"), TaskState.READY)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl stop moonraker-obico")
		self.workflow.ExecCommand("systemctl stop moonraker")
		self.Info(_("\n\tWeb access is down.\n"))

class StopKlipper(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Stopping Klipper Service"), TaskState.READY)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl stop klipper")
		self.Info(_("\n\tKlipper is down.\n"))

class EraseGcodeFiles(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Erase .gcode files"), workflow.opts.optimize_disk_space and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()
		cnt = 0
		cnt += self.workflow.DelFileCount("/home/mks/gcode_files/*")
		self.Info(_("\n\tRemoved {} .gcode files.\n").format(cnt))

class EraseMiniatures(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Erase miniature files"), workflow.opts.optimize_disk_space and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		cnt = 0
		cnt += self.workflow.DelFileCount("/home/mks/simage_space/*")
		cnt += self.workflow.DelFileCount("/home/mks/gcode_files/.thumbs/*")
		cnt += self.workflow.DelFileCount("/home/mks/Videos/*")
		self.Info(_("\n\tRemoved {} miniature files.\n").format(cnt))

class EraseOldConfig(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Erase old configuration files"), workflow.opts.optimize_disk_space and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()
		cnt = 0
		cnt += self.workflow.DelFileCount("/home/mks/klipper_config/.moonraker.conf.bkp")
		cnt += self.workflow.DelFileCount("/home/mks/klipper_config/printer-2*.cfg")
		self.Info(_("\n\tRemoved {} old configuration files.\n").format(cnt))

class EraseLogFiles(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Erase log files"), workflow.opts.optimize_disk_space and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()
		cnt = 0
		cnt += self.workflow.DelFileCount("/home/mks/klipper_logs/timelapse/*")
		cnt += self.workflow.DelFileCount("/home/mks/klipper_logs/*")
		cnt += self.workflow.DelFileCount("/home/mks/Desktop/myfile/ws/debug_log.txt")
		self.Info(_("\n\tRemoved {} log files.\n").format(cnt))

class EraseClutterFiles(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Erase Artillery clutter files"), workflow.opts.optimize_disk_space and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()
		self.Info(_("\n\tBe patient...\n"))
		cnt = 0
		cnt += self.workflow.DelFileCount("/home/mks/.bash_history")
		cnt += self.workflow.DelFileCount("/home/mks/.gitconfig")
		cnt += self.workflow.DelFileCount("/home/mks/.viminfo")
		cnt += self.workflow.DelFileCount("/home/mks/auto-webcam-id.sh")
		cnt += self.workflow.DelFileCount("/home/mks/moonraker-obico-master.zip")
		cnt += self.workflow.DelFileCount("/home/mks/moonraker-timelapse-main.zip")
		cnt += self.workflow.DelFileCount("/home/mks/plrtmpA.1606")
		cnt += self.workflow.DelFileCount("/home/mks/update_3b3bdc8.deb")
		cnt += self.workflow.DelFileCount("/home/mks/update_50701cc.deb")
		cnt += self.workflow.DelFileCount("/home/mks/update_f263f3d.deb")
		cnt += self.workflow.DelFileCount("/home/mks/webcam.txt")
		cnt += self.workflow.DelFileCount("/home/mks/Desktop/myfile/database.db")
		cnt += self.workflow.DelFileCount("/home/mks/Desktop/myfile/ws/build/src/database.db")
		cnt += self.workflow.DelFileCount("/home/mks/Desktop/myfile/ws.bak/build/mksclient")
		# Entire Folders
		cnt += self.workflow.DelTreeCount("/home/mks/moonraker-timelapse-main")
		self.Info(_("\n\tRemoved {} unneeded files.\n").format(cnt))

class FixFilePermission(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Fix file permission"), workflow.opts.file_permissions and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()
		self.Info(_("\n\tBe patient...\n"))
		self.workflow.ExecCommand("chmod a-x /etc/systemd/system/logrotate.service")
		self.workflow.ExecCommand("chmod a-x /lib/systemd/system/armbian-firstrun-config.service")
		self.workflow.ExecCommand("chmod a-x /lib/systemd/system/armbian-hardware-optimize.service")
		self.workflow.ExecCommand("chmod a-x /lib/systemd/system/armbian-hardware-monitor.service")
		self.workflow.ExecCommand("chmod a-x /lib/systemd/system/armbian-ramlog.service")
		self.workflow.ExecCommand("chmod a-x /lib/systemd/system/armbian-zram-config.service")
		self.workflow.ExecCommand("chmod a-x /lib/systemd/system/bootsplash-hide-when-booted.service")
		self.workflow.ExecCommand("chmod a-x /lib/systemd/system/gpio-monitor.service")
		self.workflow.ExecCommand("chmod a-x /lib/systemd/system/makerbase-webcam.service")
		self.workflow.ExecCommand("chmod a-x /lib/systemd/system/makerbase-byid.service")
		self.workflow.ExecCommand("chmod a-x /usr/lib/systemd/system/getty@tty1.service.d/10-noclear.conf")
		self.workflow.ExecCommand("chmod a-x /usr/lib/systemd/system/serial-getty@.service.d/10-term.conf")
		self.workflow.ExecCommand("chmod a-x /usr/lib/systemd/system/systemd-journald.service.d/override.conf")
		self.workflow.ExecCommand("chmod a-x /usr/lib/systemd/system/systemd-modules-load.service.d/10-timeout.conf")
		self.Info(_("\n\tFixed/verified {} system files permissions.").format(15))
		self.Info(_("\n\tSearching user folder...  "))
		files = self.workflow.ExecCommandEx("find /home/mks/ -not -user mks -not -group mks")
		sel = []
		for f in files:
			if fnmatch.fnmatch(f, '/home/mks/klipper_logs/moonraker-obico.*'):
				continue
			if fnmatch.fnmatch(f, '/home/mks/Desktop/myfile/ws/yuntu_plr*'):
				continue
			sel.append(f)
		self.Bold(_('{} files found\n').format(len(sel)))
		for f in sel:
			self.Info(_("\tFixing file {}...\n").format(f))
			self.workflow.ExecCommand("chown mks:mks {}".format(shlex.quote(f)))

class FixCardResizeBug(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Fix for card resize bug"), workflow.opts.resize_bug and TaskState.READY or TaskState.DISABLED)
	def UpdateState(self):
		super().UpdateState()
		if self.CanFail() and self.workflow.resizing_issue == False:
			self.SetState(TaskState.DISABLED)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl disable armbian-resize-filesystem")

class TrimDisk(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Trimming eMMC disk"), workflow.opts.trim and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("fstrim /")

class EnableUserInterface(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Enabling User Interface Service"), TaskState.CONNECTED)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl enable makerbase-client")

class EnableWebCam(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Enabling WebCam Service"), TaskState.CONNECTED)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl enable makerbase-webcam")

class EnableMoonraker(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Enabling Moonraker Service"), TaskState.CONNECTED)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl enable moonraker-obico")
		self.workflow.ExecCommand("systemctl enable moonraker")

class EnableKlipper(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Enabling Klipper Service"), TaskState.CONNECTED)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl enable klipper")

class StartKlipper(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Starting Klipper Service"), TaskState.CONNECTED)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl start klipper")

class StartMoonraker(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Starting Moonraker Service"), TaskState.CONNECTED)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl start moonraker")
		self.workflow.ExecCommand("systemctl start moonraker-obico")

class StartWebCam(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Starting WebCam Service"), TaskState.CONNECTED)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl start makerbase-webcam")

class StartUserInterface(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Starting User Interface Service"), TaskState.CONNECTED)
	def Do(self):
		super().Do()
		self.workflow.ExecCommand("systemctl start makerbase-client")

class Disconnect(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Disconnecting SSH Client"), TaskState.ALWAYS)
	def Do(self):
		super().Do()
		workflow = self.workflow
		if (workflow.exception == False) \
			and (workflow.failed_connection == False) \
			and (workflow.cancel_flag == False):
			workflow.reboot_on_exit = True
			Warning('Rebooting printer')
			self.Warning(_("\n\n\tRebooting printer\n"))
		self.workflow.Disconnect()



class Workflow(object):
	" Class to run all operations "
	def __init__(self, opts : UserOptions.UserOptions) -> None:
		self.opts = opts
		self.exception = False
		self.failed_connection = False
		self.cancel_flag = False
		self.dlg : tk.Misc
		self.queue : queue.Queue
		self.thread : threading.Thread
		self.client = paramiko.SSHClient()
		self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.shell : paramiko.Channel | None = None
		self.sftp : paramiko.SFTPClient | None = None
		self.motd_output : list[str] = []
		self.resizing_issue = False
		self.reboot_on_exit = False
		self.start_space = DiskUsage()
		self.end_space = DiskUsage()

		self.tasks : list[Task] = []
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
		self.tasks.append(FixCardResizeBug(self))
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

	###################################
	# SSH INTERFACE METHODS
	###################################

	# --- Helper Function to Clear the Buffer ---
	def _drain_shell_buffer(self, timeout=1.0) -> tuple[str, str]:
		"""Reads all currently buffered data from the shell channel."""
		if self.shell is None:
			raise Exception(N_("Connection is invalid to complete the command!"))
		start_time = time.time()
		
		# We will accumulate all the "garbage" data here, mostly the old prompt
		drained_data = b''
		drained_err = b''
		
		while True:
			# 1. Check if the channel is ready to receive (i.e., has data in the buffer)
			if self.shell.recv_stderr_ready():
				# 2. Read the available data (use a large chunk size)
				drained_err += self.shell.recv_stderr(65535)
				# Reset timeout since we received data
				start_time = time.time()

			if self.shell.recv_ready():
				# 2. Read the available data (use a large chunk size)
				drained_data += self.shell.recv(65535)
				# Reset timeout since we received data
				start_time = time.time()
				# Try to optimize timeout, when input ends with a login prompt
				tmp = drained_data.rsplit(b'\n')
				tail = tmp[-1].decode('utf-8', errors='ignore')
				for p in ArtSW4.LOGIN_PROMPTS:
					# login prompt cancel the timeout, but lets loop one more time before bailing out
					if tail.startswith(p):
						start_time -= timeout;
			# 3. If there's nothing immediately ready, wait briefly
			elif (time.time() - start_time) < timeout:
				# Check the channel status using select to avoid an infinite busy loop
				# and wait for data up to a very small interval (e.g., 0.1 seconds)
				r, w, e = select.select([self.shell], [], [], 0.1)
				if not r: # If select returns no readable handles, break the loop
					break
				if not e: # If select returns no readable handles, break the loop
					break
					
			# 4. If the timeout is hit, assume the output has stopped
			else:
				break
				
		# Return the data we drained (often useful for debugging)
		return (drained_data.decode('utf-8', errors='ignore'), drained_err.decode('utf-8', errors='ignore'))

	def Connect(self):
		if self.client is None:
			self.client = paramiko.SSHClient()
		self.client.connect(hostname=self.opts.ip_addr, username=USERNAME, password=PASSWORD)
		Info("SSH connection established.")
		self.UpdateUI(Message(MessageType.NORMAL, _("\n\tSSH connection established.")))

		# 1. Open an interactive shell
		self.shell = self.client.invoke_shell()
		time.sleep(2)
		# 3. Read everything currently in the buffer. This should be the MOTD + prompt.
		tmp = self._drain_shell_buffer()
		self.motd_output = tmp[0].splitlines()
		self.sftp = self.client.open_sftp()

	def Disconnect(self):
		if self.sftp:
			self.sftp.close()
			self.sftp = None
		if self.shell:
			if self.reboot_on_exit:
				self.reboot_on_exit = False
				self.ExecCommand('reboot')
			else:
				self.ExecCommand('exit')
			self.shell.close()
			self.shell = None
		if self.client:
			self.client.close()
			self.client = None

	def ExecCommand(self, cmd : str, timeout = 1) -> tuple[list[str], list[str]]:
		if self.client is None:
			raise Exception(N_("Connection is invalid to complete the command!"))
		if self.shell is None:
			raise Exception(N_("Connection is invalid to complete the command!"))
		self._drain_shell_buffer(0.1)
		Debug(f'# {cmd}')
		if not cmd.endswith('\n'):
			cmd += '\n'
		self.shell.send(cmd.encode('utf-8'))
		time.sleep(timeout)
		output, error = self._drain_shell_buffer(timeout=timeout)
		output = output.splitlines()
		# Remove the command echo
		if len(output) and (output[0] == cmd[:-1]):
			del output[0]
		# Remove the prompt at tail
		while len(output) and ArtSW4.IsLoginPrompt(output[-1]):
			del output[-1]
		# Convert errors into list
		error = error.splitlines()
		# Write to log
		for line in output:
			Debug(f'\t{line.strip()}')
		for line in error:
			Error(f'\t{line.strip()}')
		return (output, error)

	def ExecCommandEx(self, cmd : str) -> list[str]:
		output, error = self.ExecCommand(cmd)
		if error:
			raise Exception('\n'.join(error))
		return output

	def GetCurDir(self) -> str:
		res = self.ExecCommandEx("pwd")
		return len(res) and res[0] or ""

	def GetFreeScape(self) -> DiskUsage:
		lines = self.ExecCommandEx("df -k")
		u = DiskUsage()
		for line in lines:
			m = re.match(r'(\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s+\d+%\s(\S+)', line)
			if m:
				if m[5] == '/':
					u.root_size = int(m[2])
					u.root_free = int(m[4])
					u.total += u.root_size
				elif m[5] == '/boot':
					u.boot_size = int(m[2])
					u.boot_free = int(m[4])
					u.total += u.boot_size
		return u

	def DelFileCount(self, name : str) -> int:
		res = self.ExecCommandEx("find {} -type f | wc -l".format(name))
		cnt = 0
		if res:
			cnt = TryParseInt(res[0].strip(), 0)
		self.ExecCommandEx("rm {}".format(name))
		return cnt

	def DelTreeCount(self, name : str) -> int:
		res = self.ExecCommandEx("find {} -type f | wc -l".format(name))
		cnt = 0
		if res:
			cnt = TryParseInt(res[0].strip(), 0)
		self.ExecCommandEx("rm -rf {}".format(name))
		return cnt


	###################################
	# GUI INTERFACE METHODS
	###################################

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
	
	def _set_task_state(self, task : Task, state : TaskState) -> None:
		task.state = state
		self.UpdateUI(task)

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
					self.UpdateUI(Message(MessageType.BOLD, _('Begin Step: ') + _(task.label) + '...  '))
					self._set_task_state(task, TaskState.RUNNING)
					task.Do()
					self.UpdateUI(Message(MessageType.BOLD, _('OK!') + '\n'))
					Info('  OK!')
					self._set_task_state(task, TaskState.DONE)
				except Exception as e:
					error_message = str(e)
					self.exception = True
					self._set_task_state(task, TaskState.FAIL)
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

