#
# -*- coding: UTF-8 -*-

import fnmatch
import shlex

from i18n import _, N_
from my_workflow import Workflow, Task, TaskState


# spellchecker: disable
FIX_PERMISSION = [
	( "a-x", "/etc/systemd/system/logrotate.service" ),
	( "a-x", "/lib/systemd/system/armbian-firstrun-config.service" ),
	( "a-x", "/lib/systemd/system/armbian-hardware-optimize.service" ),
	( "a-x", "/lib/systemd/system/armbian-hardware-monitor.service" ),
	( "a-x", "/lib/systemd/system/armbian-ramlog.service" ),
	( "a-x", "/lib/systemd/system/armbian-zram-config.service" ),
	( "a-x", "/lib/systemd/system/bootsplash-hide-when-booted.service" ),
	( "a-x", "/lib/systemd/system/gpio-monitor.service" ),
	( "a-x", "/lib/systemd/system/makerbase-webcam.service" ),
	( "a-x", "/lib/systemd/system/makerbase-byid.service" ),
	( "a-x", "/usr/lib/systemd/system/getty@tty1.service.d/10-noclear.conf" ),
	( "a-x", "/usr/lib/systemd/system/serial-getty@.service.d/10-term.conf" ),
	( "a-x", "/usr/lib/systemd/system/systemd-journald.service.d/override.conf" ),
	( "a-x", "/usr/lib/systemd/system/systemd-modules-load.service.d/10-timeout.conf" ),
]
# spellchecker: enable


class FixFilePermission(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Fix file permission"), workflow.opts.file_permissions and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()
		# Standard collection (boot messages reports them)
		for perm, fname in FIX_PERMISSION:
			self.Info(_("\n\tApplying default permission for {}").format(shlex.quote(fname)))
			self.workflow.ExecCommand(f"chmod {perm} {shlex.quote(fname)}")


class FixHomePermission(Task):
	def __init__(self, workflow : "Workflow") -> None:
		super().__init__(workflow, N_("Fix home folder permissions"), workflow.opts.file_permissions and TaskState.READY or TaskState.DISABLED)
	def Do(self):
		super().Do()
		# spellchecker: enable
		self.Info(_("\n\tSearching for locked files on user folder...  "))
		files = self.workflow.ExecCommandEx("find /home/mks/ -not -user mks -not -group mks", 120)
		# Filter files used by 'root' services
		sel = []
		for f in files:
			if fnmatch.fnmatch(f, '/home/mks/klipper_logs/moonraker-obico.*'):
				continue
			# spellchecker:disable-next-line
			if fnmatch.fnmatch(f, '/home/mks/Desktop/myfile/ws/yuntu_plr*'):
				continue
			sel.append(f)
		# After filtering, this is the remainder
		self.Bold(_('{} files found\n').format(len(sel)))
		for f in sel:
			self.Info(_("\tFixing file {}...\n").format(f))
			self.workflow.ExecCommand("chown mks:mks {}".format(shlex.quote(f)))
