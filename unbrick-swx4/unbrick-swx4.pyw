#!py -3
# -*- coding: UTF-8 -*-
"""
This scripts automates the unbricking of Artillery Sidewinder X4 printers.
"""

import locale
import re
import serial.tools.list_ports
import serial
import time
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

LOG = None

# These are the chars used to mark the completion list
CHECKMARK_CHAR = "\u2714"
ERROR_CHAR = "\u2716"
EMPTYMARK_CHAR = "\u274F"
SKIP_CHAR = "\u26d2"


def Log(msg):
	"""
	This function writes a message to the log file. In the case the message is a byte stream, it 
	provides automatic conversion.
	It is expected that the `LOG` file instance exists.
	"""
	# Converts non-string input to string
	if type(msg) != str:
		msg = str(msg, "utf-8", errors="replace")
	LOG.write(msg)
	LOG.flush()

def ShowError(msg : str):
	"""
	This function writes the given error message to the log and also displays in a messagebox.
	"""
	Log(msg)
	messagebox.showerror("Error", msg)
	

def FindSerialPort():
	"""
	The pySerial Library allows one to list the serial ports. It also collects the VID/PID values for each instance. 
	This is used to filter only serial ports having PID=1A86 and PID=7523, which matches the hardware provided by 
	Artillery. This way other devices are not considered.

	Error conditions are:
		- No port having this PID/VID found
		- More than one instance was found. user have to disconnect unnecessary USB connections hardware to continue.
	"""
	ports = serial.tools.list_ports.comports()
	res = []
	for port, desc, hwid in sorted(ports):
		parts = hwid.split()
		if "VID:PID=1A86:7523" in parts:
			Log(port + '')
			res.append(port)
		#print("{}: {} [{}]".format(port, desc, hwid))
	if len(res) == 0:
		ShowError("Cannot find the serial port!\nPlease make sure that the cable is connected to the USB-C port of the printer and the printer is on.")
		return None
	if len(res) != 1:
		ShowError("There are too many compatible serial port!\nDisconnect all serial port cables except for the printer that you want to apply the fix.")
		return None
	return res[0]


class Conn(object):
	"""
	A dedicated class was created to handle the serial connection. The class is called `Conn` and the main challenge here 
	is to handle serial port echo received by the Linux terminal.
	Interestingly, this terminal also performs CR+LF expansion.

	I noticed during tests that the 1,500,000 bauds were very instable. Some USB ports have better results using a 
	1,497,600 baud. It was not conclusive, because even a USB hub connected between produced different results.

	I read in some MKSPI forum that the Armbian Linux has a 115,200 baud fallback if you like. And this was the way to go. 
	With this speed we are quite slower, but error rates are nearly inexistent.

	Regarding 115,200 rate, I could notice the following:
		- The first response bytes are trash and can be completely discarded.
		- Once Armbian switches to 115,200 bauds, it never switches back. You cannot reconnect with high rates and a 
		reboot is necessary.
	"""
	def __init__(self, port : str):
		self.port = port
		self.valid = False
		# Stores the resizing bug state
		self.resizing_issue = False
		self.reboot_on_exit = False

	def __enter__(self):
		"""
		Considering the 115,000 baud issues described above, the connection is established on class construction time, an 
		the following is done:
			- A loop tries 10 times to receive the Linux login prompt and start connection, before giving up.
			- The case were a session is still open, rare, but happens, is detected when the bash prompt is received. 
			In this case an `exit` command is issued, so that a new login session starts.
			- As soon as the *password prompt* is received, the connection sends the standard `makerbase` password.
			- When the login starts, the connection class continuously reads lines discarding them, which is the 
			*welcome message* of Armbian.

		The first problem that I noticed is that the **Artillery SW-X4 Plus** firmware has a bug that happens in this 
		*welcome message*, where the following message happens:
		
				Warning: a reboot is needed to finish resizing the filesystem
				Please reboot the system as soon as possible

		This issue, when present, a `True` value is stored on the `self.resizing_issue` member. 
		"""
		try:
			# We use a fallback speed of 115,200 to avoid communication errors, typical on 1.5 MBAUDS
			self.com = serial.Serial(self.port, baudrate=115200, timeout=3, xonxoff=True, exclusive=True)
			# Free serial port clutter
			self.com.reset_input_buffer()
			self.com.reset_output_buffer()
			# This will prompt login again
			self.Write("\n")
			# Try to connect in 115,200; because this is a fallback speed, usually start messages are corrupted. We need try harder...
			cnt = 10
			while cnt > 0:
				cnt -= 1
				# Get prompt message
				msg = self.ReadLineEx()
				# This is what we are looking for; so continue to login
				if self.IsLoginPrompt(msg):
					break
				# A prompt indicates that a session is ongoing; we have to exit the session
				if self.IsPrompt(msg):
					self.Write("exit\n")
				else:
					self.Write("\n")	# another ping
				time.sleep(0.3)
			# Login prompt
			if cnt > 0:
				# Free serial port clutter
				self.com.reset_input_buffer()
				# Enter root account
				self.Write("root\n")
				time.sleep(0.5)
				passwd = self.ReadLineEx()
				# Provide password
				if passwd == "Password: ":
					self.Write("makerbase\n")
					# ignore welcome string, with lots of ANSI color formatting
					cnt = 30
					while cnt != 0:
						cnt -= 1
						msg = self.ReadLine().strip()
						if "a reboot is needed to finish resizing the filesystem" in msg:
							self.resizing_issue = True
						# Command prompt stops this
						if self.IsPrompt(msg):
							break
					# Counter reaching zero, only if prompt never seen
					self.valid = cnt != 0
		except Exception as e:
			ShowError(str(e))
			self.valid = False
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		"""
		Another feature that this class implements is the automatic logout at the end of the connection.

		There are two ways to make this, which is controlled by the `self.reboot_on_exit` flag. On a normal situation 
		where the complete recovery steps are done, this flag is set to `True`, which issues a `reboot` command. The 
		other option is to simply execute the `exit` command, which is the usual way when the process interrupts for 
		whatever reason.

		Regardless of the way it ends, the connection breaks here and we free all devices.
		"""
		if self.com:
			if self.reboot_on_exit:
				self.Write("reboot\n")
			else:
				self.Write("exit\n")
			self.ReadLine()
			self.com.close()
			self.com = None
			self.port = None

	def IsValid(self):
		"""Returns true if a valid connection was established"""
		return self.valid
	
	@staticmethod
	def IsPrompt(msg : str):
		"""Check if the current contents is a recognized terminal prompt"""
		return msg.startswith('root@mkspi') or msg.startswith('mks@mkspi')
	
	@staticmethod
	def IsLoginPrompt(msg : str):
		"""Check if the current contents is a recognized terminal login prompt"""
		return msg.startswith('mkspi login:')

	def Write(self, msg : str):
		"""
		This is an important that sends messages to the printer. Messages are received as argument for that method, which 
		uses internal Python String representation. It has to be decoded to bytes format before sending to the printer 
		(this is essentially a formality of Python, since it is a UTF-8 to UTF-8 conversion).

		Data is written to the serial port and a flush command is issued so that the transmission can complete. Just after 
		that, the same amount of bytes are read, considering that CR+LF expansion happens on this connection. This is 
		required to clear the echo caused by the terminal service of Linux.

		Transmitted information is also sent to the log file.
		"""
		Log(msg)
		b = msg.encode("UTF-8", errors='ignore')
		self.com.write(b)
		self.com.flush()
		l = len(b)
		# for CR+LF expansion
		if 1:
			l += (b'\n' in b)
		Log(self.com.read(l))	# kill echo

	def ReadLine(self):
		"""
		The input queue is tested and a 200 ms sleep is issued if no information is present. This is required, since 
		commands may have a delay to return a response.

		The routine fetches byte by byte until the `\n` is received, indicating the end of a line.

		When a line is complete, it is decoded to the internal Python string representation. Before exiting, `CR+LF` 
		sequences are converted to simple Unix form.

		Received information is also sent to the log file.
		"""
		if self.com.in_waiting == 0:
			time.sleep(0.2)
		buf = b''
		while self.com.in_waiting:
			b = self.com.read(1)
			buf += b
			if b == b'\n':
				break
		str = buf.decode("UTF-8", errors='replace')
		str = str.replace("\r\n", "\n")
		Log(str)
		return str

	def ReadLineEx(self):
		"""
		Reads a line that has a contents. Empty lines are ignored.
		"""
		cnt = 30
		line = self.ReadLine()
		while (cnt != 0) and (line == '\n'):
			cnt -= 1
			line = self.ReadLine()
		return line
	
	def CaptureLines(self):
		"""
		This routine captures all lines until a prompt is encountered.
		"""
		lines = []
		line = self.ReadLine()
		while not self.IsPrompt(line):
			lines.append(line[:-1])
			line = self.ReadLine()
		return lines
	
	def WaitPrompt(self):
		"""
		Read lines and discards them until the terminal prompt is received
		"""
		cnt = 30
		line = self.ReadLine()
		while (cnt != 0) and (not self.IsPrompt(line)):
			cnt -= 1
			line = self.ReadLine()
		return line


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


	
class Repair(object):
	"""
	The class that has the collection of repair steps
	"""
	def __init__(self, conn : Conn):
		self.conn = conn
		self.curdir = self.GetCurDir()
		pass

	def GetCurDir(self):
		self.conn.Write("pwd\n")
		res = self.conn.ReadLineEx()[:-1]
		self.conn.WaitPrompt()
		return res

	def GetFreeScape(self) -> DiskUsage:
		self.conn.Write("df -k\n")
		buf = self.conn.CaptureLines()
		u = DiskUsage()
		for line in buf:
			if Conn.IsPrompt(line):
				break
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
	
	def StartService(self, name : str):
		self.conn.Write("systemctl start {}\n".format(name))
		self.conn.WaitPrompt()
	
	def StopService(self, name : str):
		self.conn.Write("systemctl stop {}\n".format(name))
		self.conn.WaitPrompt()
	
	def EnableService(self, name : str):
		self.conn.Write("systemctl enable {}\n".format(name))
		self.conn.WaitPrompt()
	
	def DisableService(self, name : str):
		self.conn.Write("systemctl disable {}\n".format(name))
		self.conn.WaitPrompt()

	def DelFile(self, name : str):
		self.conn.Write("rm {}\n".format(name))
		self.conn.WaitPrompt()

	def DelTree(self, name : str):
		self.conn.Write("rm -rf {}\n".format(name))
		self.conn.WaitPrompt()

	def ChMod(self, bits : str, name : str):
		self.conn.Write("chmod {} {}\n".format(bits, name))
		self.conn.WaitPrompt()

	def FixPermission(self):
		self.ChMod("a-x", "/usr/lib/systemd/system/systemd-journald.service.d/override.conf")
		self.ChMod("a-x", "/lib/systemd/system/armbian-ramlog.service")
		self.ChMod("a-x", "/lib/systemd/system/armbian-zram-config.service")
		self.ChMod("a-x", "/lib/systemd/system/armbian-hardware-optimize.service")
		self.ChMod("a-x", "/lib/systemd/system/armbian-hardware-monitor.service")
		self.ChMod("a-x", "/etc/systemd/system/logrotate.service")
		self.ChMod("a-x", "/lib/systemd/system/bootsplash-hide-when-booted.service")

	def DelGcodeFiles(self):
		self.DelFile("/home/mks/gcode_files/*")

	def DelMiniatureFiles(self):
		self.DelFile("/home/mks/simage_space/*")
		self.DelTree("/home/mks/gcode_files/.thumbs")

	def DelLogFiles(self):
		self.DelFile("/home/mks/klipper_logs/timelapse/*")
		self.DelFile("/home/mks/klipper_logs/*")
		self.DelFile("/home/mks/Desktop/myfile/ws/debug_log.txt")

	def DelClutterFiles(self):
		# Files
		self.DelFile("/home/mks/.bash_history")
		self.DelFile("/home/mks/.gitconfig")
		self.DelFile("/home/mks/.viminfo")
		self.DelFile("/home/mks/auto-webcam-id.sh")
		self.DelFile("/home/mks/moonraker-obico-master.zip")
		self.DelFile("/home/mks/moonraker-timelapse-main.zip")
		self.DelFile("/home/mks/plrtmpA.1606")
		self.DelFile("/home/mks/update_3b3bdc8.deb")
		self.DelFile("/home/mks/update_50701cc.deb")
		self.DelFile("/home/mks/update_f263f3d.deb")
		self.DelFile("/home/mks/webcam.txt")
		self.DelFile("/home/mks/Desktop/myfile/database.db")
		self.DelFile("/home/mks/Desktop/myfile/ws/build/src/database.db")
		self.DelFile("/home/mks/Desktop/myfile/ws.bak/build/mksclient")
		# Entire Folders
		self.DelTree("/home/mks/moonraker-timelapse-main")




class Gui(object):
	def __init__(self):
		self.root = Tk()
		self.root.title("Artillery SideWinder X4 Unbrick Tool v0.2")
		self.frm = ttk.Frame(self.root, padding=10)
		self.frm.grid()
		self.frm.grid_columnconfigure(1, minsize=180)
		data = [
			( "Detecting Serial Port of OS system", "serial_port", EMPTYMARK_CHAR, None),
			( "Check if Artillery Sidewinder X4 Printer Connected", "connected", EMPTYMARK_CHAR, None),
			( "Stopping Client Service", "stop_client", EMPTYMARK_CHAR, "p"),
			( "Stopping WebCam Service", "stop_webcam", EMPTYMARK_CHAR, None),
			( "Stopping Moonraker Service", "stop_moonraker", EMPTYMARK_CHAR, None),
			( "Stopping Klipper Service", "stop_klipper", EMPTYMARK_CHAR, None),
			( "Total Disk Size", "total_size", None, 'p'),
			( "Available Disk Space", "free_start", None, None),
			( "Erase .gcode files", "gcode_files", EMPTYMARK_CHAR, 'p'),
			( "Erase miniature files", "miniature_files", EMPTYMARK_CHAR, None),
			( "Erase log files", "log_files", EMPTYMARK_CHAR, None),
			( "Erase Artillery clutter files", "clutter_files", EMPTYMARK_CHAR, None),
			( "Fix file permission", "fix_permission", EMPTYMARK_CHAR, None),
			( "Fix for card resize bug", "resize_bug", SKIP_CHAR, None),
			( "Enabling Client Service", "enable_client", EMPTYMARK_CHAR, 'p'),
			( "Enabling WebCam Service", "enable_webcam", EMPTYMARK_CHAR, None),
			( "Enabling Moonraker Service", "enable_moonraker", EMPTYMARK_CHAR, None),
			( "Enabling Klipper Service", "enable_klipper", EMPTYMARK_CHAR, None),
			( "Available Disk Space After Cleanup", "free_after", None, 'p'),
			( "Starting Klipper Service", "start_klipper", EMPTYMARK_CHAR, 'p'),
			( "Starting Moonraker Service", "start_moonraker", EMPTYMARK_CHAR, None),
			( "Starting WebCam Service", "start_webcam", EMPTYMARK_CHAR, None),
			( "Starting Client Service", "start_client", EMPTYMARK_CHAR, None),
		]
		row = -1
		for t, v, i, p in data:
			row += 1
			setattr(self, v, StringVar())
			var = getattr(self, v)
			if (i):
				var.set(i)
			pad = 0
			if p:
				if p == 'p':
					pad = 10
			ttk.Label(self.frm, text=t, state="disabled").grid(column=0, row=row, pady=(pad, 0))
			ttk.Label(self.frm, textvariable=var, state="disabled").grid(column=1, row=row, pady=(pad, 0))
		row += 1
		self.run = ttk.Button(self.frm, text="Run", command=self.Run)
		self.run.grid(column=0, row=row, pady = 10)
		ttk.Button(self.frm, text="Quit", command=self.root.destroy).grid(column=1, row=row, pady = 10)
		self.root.mainloop()

	@staticmethod
	def FmtByteSize(num : int) -> str:
		if num > 1100000:
			num = float(num) / (1000.0 * 1000.0)
			sc = " GBi"
		elif num > 1100:
			num = float(num) / 1000.0
			sc = " MBi"
		else:
			num = float(num)
			sc = " KBi"
		res = locale.format_string("%5.3f", num, grouping=True)
		return res + sc

	def _StopClientService(self, repair : Repair):
		repair.StopService("makerbase-client")
		self.stop_client.set(CHECKMARK_CHAR)
		self.root.update_idletasks()

	def _StopWebCamService(self, repair : Repair):
		repair.StopService("makerbase-webcam")
		self.stop_webcam.set(CHECKMARK_CHAR)
		self.root.update_idletasks()

	def _StopMoonrakerService(self, repair : Repair):
		repair.StopService("moonraker")
		self.stop_moonraker.set(CHECKMARK_CHAR)
		self.root.update_idletasks()

	def _StopKlipperService(self, repair : Repair):
		repair.StopService("klipper")
		self.stop_klipper.set(CHECKMARK_CHAR)
		self.root.update_idletasks()

	def _GetStartFreeSize(self, repair : Repair):
		u = repair.GetFreeScape()
		self.total_size.set(Gui.FmtByteSize(u.total))
		self.free_start.set(Gui.FmtByteSize(u.root_free))
		self.root.update_idletasks()

	def _GetEndFreeSize(self, repair : Repair):
		u = repair.GetFreeScape()
		self.free_after.set(Gui.FmtByteSize(u.root_free))
		self.root.update_idletasks()

	def _FixPermission(self, repair : Repair):
		repair.FixPermission()
		self.fix_permission.set(CHECKMARK_CHAR)
		self.root.update_idletasks()

	def _FixResizeMessage(self, repair : Repair):
		repair.DisableService("armbian-resize-filesystem")
		self.resize_bug.set(CHECKMARK_CHAR)
		self.root.update_idletasks()

	def _EnableClientService(self, repair : Repair):
		repair.EnableService("makerbase-client")
		self.enable_client.set(CHECKMARK_CHAR)
		self.root.update_idletasks()

	def _EnableWebCamService(self, repair : Repair):
		repair.EnableService("makerbase-webcam")
		self.enable_webcam.set(CHECKMARK_CHAR)
		self.root.update_idletasks()

	def _EnableMoonrakerService(self, repair : Repair):
		repair.EnableService("moonraker")
		self.enable_moonraker.set(CHECKMARK_CHAR)
		self.root.update_idletasks()

	def _EnableKlipperService(self, repair : Repair):
		repair.EnableService("klipper")
		self.enable_klipper.set(CHECKMARK_CHAR)
		self.root.update_idletasks()

	def _StartClientService(self, repair : Repair):
		repair.StartService("makerbase-client")
		self.start_client.set(CHECKMARK_CHAR)
		self.root.update_idletasks()

	def _StartWebCamService(self, repair : Repair):
		repair.StartService("makerbase-webcam")
		self.start_webcam.set(CHECKMARK_CHAR)
		self.root.update_idletasks()

	def _StartMoonrakerService(self, repair : Repair):
		repair.StartService("moonraker")
		self.start_moonraker.set(CHECKMARK_CHAR)
		self.root.update_idletasks()

	def _StartKlipperService(self, repair : Repair):
		repair.StartService("klipper")
		self.start_klipper.set(CHECKMARK_CHAR)
		self.root.update_idletasks()

	def _DelGcodeFiles(self, repair : Repair):
		repair.DelGcodeFiles()
		self.gcode_files.set(CHECKMARK_CHAR)
		self.root.update_idletasks()

	def _DelMiniatureFiles(self, repair : Repair):
		repair.DelMiniatureFiles()
		self.miniature_files.set(CHECKMARK_CHAR)
		self.root.update_idletasks()

	def _DelLogFiles(self, repair : Repair):
		repair.DelLogFiles()
		self.log_files.set(CHECKMARK_CHAR)
		self.root.update_idletasks()

	def _DelClutterFiles(self, repair : Repair):
		repair.DelClutterFiles()
		self.clutter_files.set(CHECKMARK_CHAR)
		self.root.update_idletasks()
	

	def Run(self):
		name = FindSerialPort()
		if name:
			done = False
			self.serial_port.set(CHECKMARK_CHAR)
			self.root.update_idletasks()
			with Conn(name) as conn:
				if conn.IsValid():
					self.connected.set(CHECKMARK_CHAR)
					if conn.resizing_issue:
						self.resize_bug.set(EMPTYMARK_CHAR)
					else:
						self.resize_bug.set(SKIP_CHAR)
					self.root.update_idletasks()
					repair = Repair(conn)

					self._StopClientService(repair)
					self._StopWebCamService(repair)
					self._StopMoonrakerService(repair)
					self._StopKlipperService(repair)

					self._GetStartFreeSize(repair)

					self._DelGcodeFiles(repair)
					self._DelMiniatureFiles(repair)
					self._DelLogFiles(repair)
					self._DelClutterFiles(repair)

					self._FixPermission(repair)
					if conn.resizing_issue:
						self._FixResizeMessage(repair)

					self._EnableClientService(repair)
					self._EnableWebCamService(repair)
					self._EnableMoonrakerService(repair)
					self._EnableKlipperService(repair)

					self._GetEndFreeSize(repair)

					self._StartKlipperService(repair)
					self._StartMoonrakerService(repair)
					self._StartWebCamService(repair)
					self._StartClientService(repair)
					# Disable a second attempt
					self.run.config(state="disabled")
					# Force a reboot
					repair.conn.reboot_on_exit = True
					done = True
				else:
					self.connected.set(ERROR_CHAR)
					ShowError("Connection is not an artillery printer")
			if done:
				messagebox.showinfo("Rebooting Printer", "All steps were done!\n\nWait for your printer to reboot (please be patient)...")
		else:
			self.serial_port.set(ERROR_CHAR)


if __name__ == "__main__":
	locale.setlocale(locale.LC_ALL, '')
	with open("unbrick-swx4.log", "a", encoding="UTF-8") as log:
		LOG = log
		Gui()

