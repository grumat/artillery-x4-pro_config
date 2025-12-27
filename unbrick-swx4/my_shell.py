#
# -*- coding: UTF-8 -*-
#
# spellchecker:words stty makerbase mkspi timelapse USWX


import os
import time
import re
import shlex
from typing import Callable, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from .i18n import N_, _
	from .my_env import Info, Debug, Error
	from .my_lib import TryParseInt
else:
	from i18n import N_, _
	from my_env import Info, Debug, Error
	from my_lib import TryParseInt

USERNAME = 'root'
PASSWORD = 'makerbase'

TEST_MODE = os.getenv("USWX4_TEST")

if (TEST_MODE is None):
	import paramiko
	import select # Use the standard select module for checking readiness


class ArtSW4:
	"""
	Properties common to Artillery SideWinder 4
	"""
	LOGIN_PROMPTS = ('root@mkspi', 'mks@mkspi')
	@staticmethod
	def IsShellPrompt(line : str) -> bool:
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


class ArtillerySideWinder(object):
	" SSH Connection to Artillery SideWinder 4 "
	def __init__(self) -> None:
		if (TEST_MODE is None):
			self.client = paramiko.SSHClient()
			self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			self.shell : paramiko.Channel | None = None
			self.sftp : paramiko.SFTPClient | None = None
		else:
			self.sftp = None
		self.reboot_on_exit = False
		self.motd_output : list[str] = []
		self.failed_connection = False

	# --- Helper Function to Clear the Buffer ---
	def _drain_shell_buffer(self, timeout=1.0) -> str:
		"""Reads all currently buffered data from the shell channel."""
		if self.shell is None:
			raise Exception(N_("Connection is invalid to complete the command!"))
		#time.sleep(max(0.2, timeout / 50))
		start_time_2 = start_time = time.time()
		
		# We will accumulate all the "garbage" data here, mostly the old prompt
		drained_data = b''
		
		while True:
			cur_time = time.time()
			dif = cur_time - start_time
			# 1. Check if the channel is ready to receive (i.e., has data in the buffer)
			if self.shell.recv_ready():
				# 2. Read the available data (use a large chunk size)
				drained_data += self.shell.recv(65535)
				# Reset timeout since we received data
				start_time = cur_time
				# Try to optimize timeout, when input ends with a login prompt
				tmp = drained_data.rsplit(b'\n')
				tail = tmp[-1].decode('utf-8', errors='ignore')
				for p in ArtSW4.LOGIN_PROMPTS:
					# login prompt cancel the timeout
					if tail.startswith(p):
						Debug("\tPrompt was seen. bailing out")
						# Try one more loop, before exiting (100 ms)
						start_time = cur_time - timeout + 0.100;
						break
			# 3. If there's nothing immediately ready, wait briefly
			elif (dif < timeout):
				time.sleep(0.1)
				# Check the channel status using select to avoid an infinite busy loop
				# and wait for data up to a very small interval (e.g., 0.1 seconds)
				r, w, e = select.select([self.shell], [], [], timeout - dif)
				if not r: # If select returns no readable handles, break the loop
					break
					
			# 4. If the timeout is hit, assume the output has stopped
			else:
				break
		# Return the data we drained (often useful for debugging)
		return drained_data.decode('utf-8', errors='ignore')

	def Connect(self, ip_addr : str) -> None:
		if (TEST_MODE is None):
			if self.client is None:
				self.client = paramiko.SSHClient()
			try:
				self.failed_connection = False
				self.client.connect(hostname=ip_addr, username=USERNAME, password=PASSWORD)
			except Exception as e:
				self.failed_connection = True
				raise
			Info("SSH connection established.")

			# 1. Open an interactive shell (use dumb terminal to eliminate soft-breaks)
			self.shell = self.client.invoke_shell(term='dumb', width=0, height=0)
			time.sleep(2)
			# 3. Read everything currently in the buffer. This should be the MOTD + prompt.
			tmp = self._drain_shell_buffer()
			self.motd_output = tmp.splitlines()
			# Disable echo
			self.ExecCommand('stty -echo')
			# Make sure messages are in English/US for correct parsing
			self.ExecCommand('export LC_ALL=en_US.UTF-8')
			# Open sftp channel for file transfer
			self.sftp = self.client.open_sftp()

	def Disconnect(self) -> None:
		if (TEST_MODE is None):
			if self.sftp:
				self.sftp.close()
				self.sftp = None
			if self.shell:
				if self.reboot_on_exit:
					self.reboot_on_exit = False
					self.ExecCommand('reboot', 5, True)
				else:
					self.ExecCommand('exit', 5, True)
				self.shell.close()
				self.shell = None
			if self.client:
				if self.failed_connection == False:
					self.client.close()
				self.client = None

	def ExecCommand(self, cmd : str, timeout = 10, can_exit = False) -> list[str]:
		if (TEST_MODE is None):
			if self.client is None:
				raise Exception(N_("Connection is invalid to complete the command!"))
			if self.shell is None:
				raise Exception(N_("Connection is invalid to complete the command!"))
			self._drain_shell_buffer(0.2)
			Debug(f'# {cmd}')
			if not cmd.endswith('\n'):
				cmd += '\n'
			self.shell.send(cmd.encode('utf-8'))
			output = self._drain_shell_buffer(timeout=timeout)
			# At least the shell prompt was expected!
			if (len(output) == 0) and (can_exit == False):
				msg = N_("No response seen during the specified timeout!")
				Error(msg)
				raise Exception(_(msg))

			output = output.splitlines()
			# Remove the command echo
			if len(output) and (output[0] == cmd[:-1]):
				del output[0]
			# Remove the prompt at tail
			while len(output) and ArtSW4.IsShellPrompt(output[-1]):
				del output[-1]
			# Write to log
			for line in output:
				Debug(f'\t\t{line.strip()}')
			return output
		else:
			return []
	
	def SftpGet(self, src : str, dest : str) -> None:
		if (TEST_MODE is None):
			if self.sftp is None:
				raise RuntimeError("Called method without connection")
			Debug(f"SFTP '{src}' {dest}")
			self.sftp.get(src, dest)
	
	def SftpPut(self, src : str, dest : str) -> None:
		if (TEST_MODE is None):
			if self.sftp is None:
				raise RuntimeError("Called method without connection")
			Debug(f"SFTP {src} '{dest}'")
			self.sftp.put(src, dest, None, True)

	def GetFreeScape(self) -> DiskUsage:
		u = DiskUsage()
		if (TEST_MODE is None):
			lines = self.ExecCommand("df -k")
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
	
	def FindFiles(self, name : str) -> list[str]:
		if (TEST_MODE is None):
			pat = re.compile(r'find:\s.+: No such file or directory')
			res = self.ExecCommand("find {} -type f".format(name), 30)
			# Removes message like: find: ‘/home/mks/moonraker-timelapse-main’: No such file or directory
			if res and pat.match(res[0]):
				del res[0]
			return res
		else:
			return []

	def DelFileMatch(self, names : str|list[str], info: Optional[Callable[[str, bool], None]] = None) -> int:
		cnt = 0
		if (TEST_MODE is None):
			if names is str:
				names = [names]
			for name in names:
				if info:
					info(name, True)
				res = self.FindFiles(name)
				if res:
					cnt += len(res)
					for f in res:
						if info:
							info(f, False)
						self.ExecCommand("rm {}".format(shlex.quote(f)))
		return cnt

	def DelTreeMatch(self, names : str|list[str], info: Optional[Callable[[str, bool], None]] = None) -> int:
		cnt = 0
		if (TEST_MODE is None):
			pat = re.compile(r'find:\s.+: No such file or directory')
			if names is str:
				names = [names]
			for name in names:
				if info:
					info(name, True)
				res = self.ExecCommand("find {} -type f | wc -l".format(shlex.quote(name)), 30)
				# Removes message like: find: ‘/home/mks/moonraker-timelapse-main’: No such file or directory
				if res and pat.match(res[0]):
					continue
				else:
					if info:
						info(name, False)
					cnt += TryParseInt(res[0].strip(), 0)
					self.ExecCommand("rm -rf {}".format(shlex.quote(name)))
		return cnt

