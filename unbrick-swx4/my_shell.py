#
# -*- coding: UTF-8 -*-


import paramiko
import select # Use the standard select module for checking readiness
import time
import re
import shlex

from i18n import N_
from my_env import Info, Debug, Error
from my_lib import TryParseInt
from typing import Callable, Optional


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


class ArtillerySideWinder(object):
	" SSH Connection to Artillery SideWinder 4 "
	def __init__(self) -> None:
		self.client = paramiko.SSHClient()
		self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.shell : paramiko.Channel | None = None
		self.sftp : paramiko.SFTPClient | None = None
		self.reboot_on_exit = False
		self.motd_output : list[str] = []
		self.failed_connection = False

	# --- Helper Function to Clear the Buffer ---
	def _drain_shell_buffer(self, timeout=1.0) -> tuple[str, str]:
		"""Reads all currently buffered data from the shell channel."""
		if self.shell is None:
			raise Exception(N_("Connection is invalid to complete the command!"))
		time.sleep(max(0.2, timeout / 50))
		start_time_2 = start_time = time.time()
		
		# We will accumulate all the "garbage" data here, mostly the old prompt
		drained_data = b''
		drained_err = b''
		
		while True:
			cur_time = time.time()
			# 1. Check if the channel is ready to receive (i.e., has data in the buffer)
			if self.shell.recv_stderr_ready():
				# 2. Read the available data (use a large chunk size)
				drained_err += self.shell.recv_stderr(65535)
				# Reset timeout since we received data
				start_time_2 = cur_time

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
						# Try one more loop, before exiting (200 ms)
						start_time = cur_time - timeout + 0.25;
						break
			# 3. If there's nothing immediately ready, wait briefly
			elif ((cur_time - start_time) < timeout) \
				or ((cur_time - start_time_2) < timeout):
				# Check the channel status using select to avoid an infinite busy loop
				# and wait for data up to a very small interval (e.g., 0.1 seconds)
				r, w, e = select.select([self.shell], [], [], 0.1)
				if not r: # If select returns no readable handles, break the loop
					break
				if not e: # If select returns no readable handles, break the loop
					break
					
			# 4. If the timeout is hit, assume the output has stopped
			elif (cur_time - start_time_2) > 0.25:
				break
		# Return the data we drained (often useful for debugging)
		return (drained_data.decode('utf-8', errors='ignore'), drained_err.decode('utf-8', errors='ignore'))

	def Connect(self, ip_addr : str):
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
		self.motd_output = tmp[0].splitlines()
		# Make sure messages are in English/US for correct parsing
		self.ExecCommand('export LC_ALL=C')
		# Open sftp channel for file transfer
		self.sftp = self.client.open_sftp()

	def Disconnect(self):
		if self.sftp:
			self.sftp.close()
			self.sftp = None
		if self.shell:
			if self.reboot_on_exit:
				self.reboot_on_exit = False
				self.ExecCommand('reboot', 5)
			else:
				self.ExecCommand('exit', 5)
			self.shell.close()
			self.shell = None
		if self.client:
			if self.failed_connection == False:
				self.client.close()
			self.client = None

	def ExecCommand(self, cmd : str, timeout = 10) -> tuple[list[str], list[str]]:
		if self.client is None:
			raise Exception(N_("Connection is invalid to complete the command!"))
		if self.shell is None:
			raise Exception(N_("Connection is invalid to complete the command!"))
		self._drain_shell_buffer(0.2)
		Debug(f'# {cmd}')
		if not cmd.endswith('\n'):
			cmd += '\n'
		self.shell.send(cmd.encode('utf-8'))
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
			Debug(f'\t\t{line.strip()}')
		for line in error:
			Error(f'\t\t{line.strip()}')
		return (output, error)

	def ExecCommandEx(self, cmd : str, timeout = 10) -> list[str]:
		output, error = self.ExecCommand(cmd, timeout)
		if error:
			raise Exception('\n'.join(error))
		return output

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
	
	def FindFiles(self, name : str) -> list[str]:
		pat = re.compile(r'find:\s.+: No such file or directory')
		res = self.ExecCommandEx("find {} -type f".format(name), 30)
		# Removes message like: find: ‘/home/mks/moonraker-timelapse-main’: No such file or directory
		if res and pat.match(res[0]):
			del res[0]
		return res

	def DelFileMatch(self, names : str|list[str], info: Optional[Callable[[str, bool], None]] = None) -> int:
		if names is str:
			names = [names]
		cnt = 0
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
		pat = re.compile(r'find:\s.+: No such file or directory')
		if names is str:
			names = [names]
		cnt = 0
		for name in names:
			if info:
				info(name, True)
			res = self.ExecCommandEx("find {} -type f | wc -l".format(shlex.quote(name)), 30)
			# Removes message like: find: ‘/home/mks/moonraker-timelapse-main’: No such file or directory
			if res and pat.match(res[0]):
				continue
			else:
				if info:
					info(name, False)
				cnt += TryParseInt(res[0].strip(), 0)
				self.ExecCommand("rm -rf {}".format(shlex.quote(name)))
		return cnt

