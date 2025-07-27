#
# -*- coding: UTF-8 -*-

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from Tooltip import Tooltip

from typing import Callable
_ : Callable[[str], str]
N_ = lambda t : t


class UserOptions(object):
	def __init__(self) -> None:
		self.printer = 0
		self.reset = 0
		self.optimize_disk_space = True
		self.file_permissions = True
		self.resize_bug = True
		self.trim = True
		self.model_attr = True
		self.extruder_accel = True
		self.stepper_z_current = True
		self.extruder_current = 1
		self.probe_offset = 1
		self.probe_sampling = True
		self.probe_validation = False
		self.screws_tilt_adjust = False
		self.fan_rename = True
		self.mb_fan_fix = True
		self.hb_fan_speed = 0
		self.mb_fan_speed = 0
		self.temp_mcu = True
		self.nozzle_wipe = 2
		self.purge_line = 2
		self.enable_m600 = True
		self.pause = 3


tt_printer = N_("""Please select the correct printer.
This parameter is very critical because hardware properties of both models are very different and incompatible.

If you fail to set the correct option, bad things will happen when you try to print something.
				
You can always repeat this tool with the correct option to fix a bad choice.""")


tt_reset = N_("""Configuration Reset
This option controls if your printer configuration file will be initialized to factory default.
Usually, there is no need to reset your configuration completely, because the tool will modify only very specific settings.

So, leave the default value and oly if the tool notices that your Klipper configuration is broken it will stop and suggests the reset option.
Then you have two options, with or without Klipper calibration data. If your printer behavior is absolutely weird, you should also reset calibration.""")


tt_optimize_disk_space = N_(
	"""Optimize Disk Space
This option erases old files and miniatures and also remove known developer files that "Artillery" just forgot to clear.

It is recommended to activate this option, because these printers are sold with an 8GB eMMC disk, which is quite restrictive. If the OS has no space for its own duties, your printer might not boot anymore."""
)


tt_file_permissions = N_(
	"""Fix File Permissions
There are known files on a factory default installation which have wrong file permission. Most of them are still harmless.

Also, this tool makes sure that Klipper environment has proper access to all related contents."""
)


tt_resize_bug = N_(
	"""Fix Resize Bug
The "Artillery Sidewinder X4 Plus" has a known bug that issues a warning on the system log related to disk partition resizing. 

Except for some performance impact this problem is rather harmless.

You can safely enable this tool, as it will check if the problem exists before trying to apply a fix."""
)


tt_trim = N_(
	"""Trim eMMC
Your printer has an 8GB (or optional 32GB) to store a Linux operating system, Klipper services and all your prints.
This type of memory technology suffers from one strong limitation: Memory clean costs too much time. As a countermeasure OS uses a technique called garbage collection, which means old data is actually not erased.
At some point, OS has to execute an operation called TRIM, that really erase this garbage.

This tool runs a TRIM operation to keep your eMMC fresh and speedy."""
)


tt_model_attr = N_(
	"""Fix Printer Model Settings
This option checks the various specific configurations for the selected printer model, and fixes elements that doesn't match your selection.

These tool checks very essential Klipper settings. This may affect the following settings: stepper motors, printer homing, bed mesh and macros""")


tt_extruder_accel = N_("""Limits Extruder Acceleration
Some older firmware have a higher extruder acceleration setting. But it has been reduced in recent configurations, probably to avoid higher temperatures on the extruder.
This setting can help reduce extruder temperature. Too much temperature in the extruder stepper has the potential to soften your filament and cause clogs.""")


tt_stepper_z_current = N_("""Higher Stepper Z Current
Usually the X4-Plus model runs with 800mA stepper current for the gantry and the X4-Pro model with 900mA. This seems inconsistent, since the Plus model has more mass to move.

This option will fix issues of Z-Axis movement, at the cost of slightly more power consumption.""")


tt_extruder_current = N_("""Extruder Run Current
Comparing configurations of the X4-Plus and X4-Pro has an inconsistency on the extruder current. It does not make sense if both uses the same head and seems that the factory did not pay due attention to the point.
The following settings happens to exist:
\t - 800mA: SW X4-Plus
\t - 900mA: average recommendation
\t - 1000mA: SW X4=Pro

Please note that increasing the current will make your extruder stepper warmer and potentially more susceptible to clogging. On the other side, max filament flow could benefit of it, for faster prints.""")


tt_probe_offset = N_("""Distance Sensor Offset
The offset value of the probe is slightly inconsistent on the factory settings. You can use this option to correct the offset values for the probe.

Note that Artillery mount this component on the opposite orientation of the data-sheet recommendation. So I strongly recommended a mod that reorient this sensor and follows the data-sheet mounting examples.
If your printer has this mod, then you have to select the "180° Mount" option.

My repository contains series of tests, procedures on how to do this and also links to the data-sheet.""")


tt_probe_sampling = N_("""Improved Z-Offset sampling
Regardless of the orientation of your distance sensor, you can improve the Z-offset sampling by using lower approximation speeds and more samples.

By using a more accurate sampling method, the overall Z-offset errors are reduced and first layer of your prints should be more consistent.""")


tt_probe_validation = N_("""Improved Z-Offset validation
Besides improving sampling conditions, you can reduce the acceptance threshold for the sampled data.
This means that after performing the samples, value differences have to fit a lower error margin to be accepted.

Note that error margins are on the limit. If you activate this option with an unmodified printer it may happen that you printer stops with errors during Z-offset calibration and also during bed-mesh calibration.""")


tt_screws_tilt_adjust = N_("""Activate Manual Leveling Feature
Klipper offers you a tool that helps adjusting the screws of your print bed. This option install the necessary configuration.

When activating this option the 'fluidd' interface will show a new "BED_SCREWS_ADJUST" button to perform the calibration. There are various guides on the web on how to use this command.

If you uncheck this option and your configuration already contains screws information, it will be left untouched.""")

tt_fan_rename = N_("""Rename Fans
This option renames printer fans to nice names. This is used on the 'fluidd' interface.

The 'Fan 0' is renamed to 'Heatbreak Cooling Fan';
The 'Fan 2' is renamed to 'Mainboard Fan'""")


tt_mb_fan_fix = N_("""Improved Mainboard Fan
On the original configuration main-board fan is only activated by the print nozzle. This configuration is OK if you are doing only printing.

But it's main function is to keep stepper motor drivers cool. This means that, if you activate steppers but keep the nozzle off, then perform lots of motion operations, you will overheat your stepper drivers and get errors.

By applying this option, your main-board fan will turn on as soon as any of the following elements are active: heat bed, print nozzle or any of your stepper drivers. So, I strongly recommend you set this option.

In the case you already have this modification the routine will not modify it, regardless if its 'on' or 'off'.""")


tt_mb_fan_speed = N_("""Main-board Fan Speed
This option allows you to reduce the speed of the main-board fan. The main goal is to lower noise levels.

You should note that the main function of this fan is to cool the stepper motor drivers down, which may get hot depending on the intensity of acceleration and speed values. If cooling is insufficient a thermal protection of the stepper driver may occur and the motion for the affected axis stops.

In my repository I suggest the mount of a 'fan duct' that concentrates more air flow to the steppers drivers and allows you to safely reduce the fan speed.""")


tt_hb_fan_speed = N_("""Heatbreak Fan Speed
This option allows you to reduce the speed of the heatbreak fan. This should reduce the noise levels.

Please consider the following: the main function of this fan is to protect the filament smoothing near the entry of the hot-end, which could deform when the extruder pushes. If you reduce the cooling fan too much you may experience clogs on the cold end.

But notice that this setup was designed for very high temperatures. If your max temperature never goes above 250°C you can reduce this value. This is my case and I use 90%, which already does a good job in noise levels.

Speculative Note: Artillery launched recently a new print head component, which seems to have less heatsink mass, which reduces vibration. On the other side, this indicates that the old heatsink is an overkill.""")


tt_temp_mcu = N_("""Temperature Reading for Host and MCU
If you use the 'fluidd' interface you will like this option: It activates the temperature sensors for the Host CPU and the drivers MCU.

Note that this option does not modify your settings if this sensors are already active.""")


tt_nozzle_wipe = N_("""Nozzle Wipe
This macro controls how the nozzle will be cleaned. But, "Artillery" published two different versions of it.

The legacy version wipes the nozzle many times at a slower speed, but it tends to wear the wipe pad prematurely out. The new version wipes less times but at a faster speed.

Note that updating this setting may not change anything, since it's use depends on your slicer software configuration.""")


tt_purge_line = N_("""Purge Line
This macro controls how the purge line is drawn and "Artillery" published two different versions of it.

The legacy version draws multiple lines in a stack. Because this pattern causes more adhesion a newer version was developed that is very easy to be removed.

Note that updating this setting may not change anything, since it's use depends on your slicer software configuration.""")


tt_enable_m600 = N_("""Enable M600
This option adds the new published macros to support the M600 filament change feature.

The following changes will be done:
	- Configuration support for beeper
	- M300 g-code macro (Play Tone)
	- M600 g-code macro (Filament Change)
	- T600 g-code macro (Artillery custom: Resume Print)
	
Note that if these settings are already installed this tool will not modify, neither remove them.""")


tt_pause = N_("""Pause Macro
The pause macro controls the behavior your printer when you press the pause button on the control panel.

The following options are offered:
	- Do Not Change: will not modify it
	- Legacy: Use legacy "Artillery" code
	- New: Use newer "Artillery" code
	- Grumat: My custom version.

The new version of "Artillery" adds support for control parameters used by the M600 command.

My custom version is based on the new "Artillery" macro and evaluates the filament sensor. In the case where filament is out, it homes th print head and moves the printed object far away.
You don't need to load and purge filament right over your printed object.""")


# --- SetupDialog Class ---
class SetupDialog(tk.Toplevel):
	def __init__(self, parent, opt : UserOptions):
		super().__init__(parent)
		self.parent = parent
		self.title("Setup Dialog")
		self.opt = opt
		self.vars = {}
		# Root row counter
		self.d_cnt = 0
		# Column Counter subject to current row counter
		self.c_cnt = 0
		# Item row counter subject to current column counter
		self.i_cnt = 0

		# Make the dialog modal
		self.transient(parent)
		self.grab_set()

		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		# Frame for main content (contains rows)
		self.dlg = ttk.Frame(self, padding="10")
		self.dlg.grid(sticky="nsew")
		self.dlg.columnconfigure(0, weight=1)
		# Head stores head information (organized in columns)
		self.head = ttk.Frame(self.dlg)
		# Body stores all configurable options (organized in columns)
		self.body = ttk.Frame(self.dlg)
		# Footer usually contains a button bar (organized in columns)
		self.footer = ttk.Frame(self.dlg)
		self.footer.grid()
		self.footer.columnconfigure(0, weight=1)

		self.CreateWidgets()
		self.CenterWindow()

		self.protocol("WM_DELETE_WINDOW", self._on_closing)

		self.wait_window(self)

	def CreateWidgets(self):

		data = [
			[self.InsertHead,	None,	()],
			[self.Empty,		self.h,	()],
			[self.PrinterModel,	self.h,	(_("Select Printer Model"), [_("Artillery SideWinder X4 Pro"), _("Artillery SideWinder X4 Plus")], "printer")],
			[self.Empty,		self.h,	()],

			[self.InsertBody,	None,	()],

			[self.CreateColumn,	None,	()],
			[self.Title,		None,	(_("Linux Operating System Cleanup"),)],
			[self.Check,		None,	(_("Optimize Disk Space"), "optimize_disk_space")],
			[self.Check,		None,	(_("Fix File Permission"), "file_permissions")],
			[self.Check,		None,	(_("Fix Resize Bug"), "resize_bug")],
			[self.Check,		None,	(_("Trim eMMC"), "trim")],
			[self.Title,		None,	(_("Klipper Hardware Configuration"),)],
			[self.Menu,			None,	(_("Configuration Reset"), [_("Update only (default)"), _("Factory Reset (keep calibration)"), _("Complete Factory Reset")], "reset")],
			[self.Check,		None,	(_("Fix Printer Model Settings"), "model_attr")],
			[self.Title,		None,	(_("Gantry"),)],
			[self.Check,		None,	(_("Higher Stepper Z Current"), "stepper_z_current")],
			[self.Title,		None,	(_("Extruder"),)],
			[self.Check,		None,	(_("Limits Extruder Acceleration"), "extruder_accel")],
			[self.Menu,			None,	(_("Extruder Run Current"), [_("800mA (SW X4-Plus)"), _("900mA (recommendation)"), _("1000mA (SW X4-Pro)")], "extruder_current")],
			[self.Title,		None,	(_("Z-Axis Distance Sensor"),)],
			[self.Menu,			None,	(_("Offset"), [_("Do not change"), _("Factory Mount (default)"), _("180° Mount")], "probe_offset")],
			[self.Check,		None,	(_("Improved Z-Offset Sampling"), "probe_sampling")],
			[self.Check,		None,	(_("Improved Z-Offset Error Margin"), "probe_validation")],

			[self.VLine,		None,	()],

			[self.CreateColumn,	None,	()],

			[self.Title,		None,	(_("Print Bed"),)],
			[self.Check,		None,	(_("Activate Manual Leveling Feature"), "screws_tilt_adjust")],
			[self.Title,		None,	(_("Printer Fans"),)],
			[self.Check,		None,	(_("Rename Fans"), "fan_rename")],
			[self.Check,		None,	(_("Improved Mainboard Fan control"), "mb_fan_fix")],
			[self.Menu,			None,	(_("Mainboard Fan Speed"), [_("Max (default)"), _("95%"), _("90%"), _("85%"), _("80%"), _("75%"), _("70%")], "mb_fan_speed")],
			[self.Menu,			None,	(_("Heatbreak Fan Speed"), [_("Max (default)"), _("95%"), _("90%"), _("85%"), _("80%"), _("75%"), _("70%")], "hb_fan_speed")],
			[self.Title,		None,	(_("Temperatures"),)],
			[self.Check,		None,	(_("Temperature Reading for Host and MCU"), "temp_mcu")],
			[self.Title,		None,	(_("G-Code"),)],
			[self.Menu,			None,	(_("Nozzle Wipe"), [_("Do not Change"), _("Legacy Version"), _("New Version")], "nozzle_wipe")],
			[self.Menu,			None,	(_("Purge Line"), [_("Do not Change"), _("Legacy Version"), _("New Version")], "purge_line")],
			[self.Check,		None,	(_("M600: Filament Change Support"), "enable_m600")],
			[self.Menu,			None,	(_("Pause Macro"), [_("Do not Change"), _("Legacy Version"), _("New Version"), _("Grumat Version")], "pause")],

			[self.OkCancel,		None,	()],
		]

		for method, pos, args in data:
			method(pos, *args)

	class Layout:
		def __init__(self, p : ttk.Frame, r, c, px = None, py = None):
			self.parent = p
			self.row = r
			self.col = c
			self.sticky = ""
			self.padx = (px is not None) and px or 0
			self.pady = (py is not None) and py or 0
		def Setup(self, widget : ttk.Widget) -> None:
			"""
			Returns a dictionary suitable for passing to widget.grid(**options).
			"""
			options = {
				"row": self.row,
				"column": self.col, # Note: grid uses 'column', not 'col'
			}
			if self.padx is not None:
				options["padx"] = self.padx
			if self.pady is not None:
				options["pady"] = self.pady
			if self.sticky: # Only add if sticky is not an empty string
				options["sticky"] = self.sticky
			widget.grid(**options)

	#           dlg:
	# d_cnt = 0 +-------------------------------------------+
	#			|	head:									|
	# 			|	+-----------+-----------+-----------|	|
	# 			|	| c_cnt = 0 | c_cnt = 1 | c_cnt = 2 |	|
	# 			|	+-----------+-----------+-----------|	|
	#           |											|
	# d_cnt = 1 |	body:									|
	#			|	+-------------------------------------+	|
	#			|	|	  c_cnt = 0...n 				  |	|
	#			|	|     +-------------------------+	  |	|
	#			|	| ... | column: 			    | ... |	|
	#			|	|	  |   i_cnt = 0 <widgets 0> |	  |	|
	#			|	|	  |   i_cnt = 1 <widgets 1> |	  |	|
	#			|	|	  |							|	  |	|
	#			|	| ... |   i_cnt = n <widgets n> | ... |	|
	#			|	|	  +-------------------------+	  |	|
	#			|	+-------------------------------------+	|
	#           |											|
	# d_cnt = 2 |	footer:									|
	#			|	+-------------------------------------+	|
	#			|	|				[  OK  ]   [ Cancel ] |	|
	#			|	+-------------------------------------+	|
	#			+-------------------------------------------+
	def d(self) -> "SetupDialog.Layout":
		"Layout for dialog/root level"
		if self.d_cnt:
			lyt = self.Layout(self.dlg, self.d_cnt, 0, 0, 8)
		else:
			lyt = self.Layout(self.dlg, self.d_cnt, 0, 0, (0,8))
		lyt.sticky = "nsew"
		self.d_cnt += 1
		self.c_cnt = 0
		self.i_cnt = 0
		return lyt
	def h(self) -> "SetupDialog.Layout":
		"Layout for header (borrows column counter)"
		lyt = self.Layout(self.head, 0, self.c_cnt, 0, 0)
		lyt.sticky = "ew"
		self.c_cnt += 1
		self.i_cnt = 0
		return lyt
	def b(self) -> "SetupDialog.Layout":
		"Layout for Body, which contains columns with all widgets"
		lyt = self.Layout(self.body, 0, self.c_cnt, 5, 0)
		lyt.sticky = "nsew"
		self.c_cnt += 1
		self.i_cnt = 0
		return lyt
	def c(self) -> "SetupDialog.Layout":
		"Layout for body column. Container for most configuration widgets"
		lyt = self.Layout(self.column, self.i_cnt, 0, (20,0), 0)
		lyt.sticky = "ew"
		self.i_cnt += 1
		return lyt
	def c2(self) -> "SetupDialog.Layout":
		lyt = self.c()
		lyt.padx = 0
		return lyt

	def InsertHead(self, lyt_call : Callable[[], "SetupDialog.Layout"]):
		lyt_call = (lyt_call is not None) and lyt_call or self.d
		lyt : "SetupDialog.Layout" = lyt_call()
		lyt.Setup(self.head)
		lyt.parent.grid_rowconfigure(lyt.row, weight=0)
		self.head.grid_columnconfigure(0, weight=1)
		self.head.grid_columnconfigure(1, weight=0)
		self.head.grid_columnconfigure(2, weight=1)

	def InsertBody(self, lyt_call : Callable[[], "SetupDialog.Layout"]):
		lyt_call = (lyt_call is not None) and lyt_call or self.d
		lyt : "SetupDialog.Layout" = lyt_call()
		lyt.Setup(self.body)
		self.body.grid_rowconfigure(0, weight=1)
		lyt.parent.grid_rowconfigure(lyt.row, weight=1)

	def CreateColumn(self, lyt_call : Callable[[], "SetupDialog.Layout"]):
		lyt_call = (lyt_call is not None) and lyt_call or self.b
		lyt : "SetupDialog.Layout" = lyt_call()

		lyt.parent.grid_columnconfigure(lyt.col, uniform="col_width", weight=1)
		self.column = ttk.Frame(lyt.parent)
		lyt.Setup(self.column)
		self.column.grid_columnconfigure(0, weight=1)

	def HLine(self, lyt_call : Callable[[], "SetupDialog.Layout"]):
		lyt_call = (lyt_call is not None) and lyt_call or self.c
		lyt : "SetupDialog.Layout" = lyt_call()
		lyt.sticky = "ns"
		sep = ttk.Separator(lyt.parent, orient="horizontal")
		lyt.Setup(sep)

	def VLine(self, lyt_call : Callable[[], "SetupDialog.Layout"]):
		lyt_call = (lyt_call is not None) and lyt_call or self.b
		lyt : "SetupDialog.Layout" = lyt_call()
		lyt.parent.grid_columnconfigure(lyt.col, weight=0)
		sep = ttk.Separator(lyt.parent, orient="vertical")
		lyt.Setup(sep)

	def Empty(self, lyt_call : Callable[[], "SetupDialog.Layout"]):
		lyt_call = (lyt_call is not None) and lyt_call or self.c
		lyt : "SetupDialog.Layout" = lyt_call()
		label = ttk.Label(lyt.parent, text="", state="disabled")
		lyt.Setup(label)

	def PrinterModel(self, lyt_call : Callable[[], "SetupDialog.Layout"], title : str, labels : list[str], var, callback = None):
		lyt_call = (lyt_call is not None) and lyt_call or self.h
		lyt : "SetupDialog.Layout" = lyt_call()

		v = tk.IntVar(self)
		v.set(getattr(self.opt, var))
		self.vars[var] = v

		radio_frame = ttk.LabelFrame(lyt.parent, text=_(title))
		lyt.Setup(radio_frame)
		for i, label in enumerate(labels):
			ttk.Radiobutton(radio_frame, text=label, variable=v, value=i).grid(row = i, column=0, sticky="w")
		self.Finalize(radio_frame, var, callback)

	def Title(self, lyt_call : Callable[[], "SetupDialog.Layout"], label):
		lyt_call = (lyt_call is not None) and lyt_call or self.c2
		lyt : "SetupDialog.Layout" = lyt_call()

		frame = ttk.Frame(lyt.parent, borderwidth=2)
		lyt.Setup(frame)
		ttk.Label(frame, text=label).pack(side="left")
		ttk.Separator(frame, orient="horizontal").pack(side="left", fill="x", expand=True)

	def Finalize(self, widget, var, callback):
		tt = "tt_"+var
		g = globals()
		if tt in g:
			xl = _(g[tt])
			Tooltip(widget, xl)
			for wc in widget.winfo_children():
				Tooltip(wc, xl)
		if callback:
			widget.config(command=callback)

	def Check(self, lyt_call : Callable[[], "SetupDialog.Layout"], label, var, cmd = None, callback = None):
		lyt_call = (lyt_call is not None) and lyt_call or self.c
		lyt : "SetupDialog.Layout" = lyt_call()

		v = tk.BooleanVar(self)
		v.set(getattr(self.opt, var))
		self.vars[var] = v

		cb = ttk.Checkbutton(lyt.parent, text=label, variable=self.vars[var])
		lyt.Setup(cb)
		self.Finalize(cb, var, callback)

	def Menu(self, lyt_call : Callable[[], "SetupDialog.Layout"], title, labels, var, callback = None):
		lyt_call = (lyt_call is not None) and lyt_call or self.c
		lyt : "SetupDialog.Layout" = lyt_call()

		v = tk.IntVar(self)
		v.set(getattr(self.opt, var))
		self.vars[var] = v

		frame = ttk.Frame(lyt.parent)
		lyt.Setup(frame)
		ml = 0
		for l in labels:
			if ml < len(l):
				ml = len(l)
		frame.grid_columnconfigure(1, weight=1, minsize=ml*6+20)
		ttk.Label(frame, text=title).grid(row=0, column=0)
		om = ttk.OptionMenu(frame, tk.StringVar(self), labels[v.get()], *labels, command=lambda value: v.set(labels.index(value)))
		om.grid(row=0, column=1, sticky="ew")
		self.Finalize(frame, var, callback)

	def OkCancel(self, lyt_call : Callable[[], "SetupDialog.Layout"]):
		lyt_call = (lyt_call is not None) and lyt_call or self.d
		lyt : "SetupDialog.Layout" = lyt_call()
		lyt.Setup(self.footer)
		lyt.parent.grid_rowconfigure(lyt.row, weight=0)

		self.footer.grid_columnconfigure(0, weight=1)
		self.footer.grid_columnconfigure(1, uniform="same_1_2")
		self.footer.grid_columnconfigure(2, uniform="same_1_2")
		# --- OK/Cancel Button ---
		tk.Label(self.footer, text="", state="disabled").grid(row=0, column=0)
		tk.Button(self.footer, text=_("Ok"), command=self._on_save_and_close, width=12).grid(row=0, column=1, padx=4, sticky="we")
		tk.Button(self.footer, text=_("Cancel"), command=self._on_closing, width=12).grid(row=0, column=2, padx=4, sticky="we")


	def _on_save_and_close(self):
		for k, v in self.vars.items():
			setattr(self.opt, k, v.get())
		self.destroy()

	def _on_closing(self):
		self.destroy()

	def CenterWindow(self):
		self.update_idletasks()
		parent_x = self.parent.winfo_x()
		parent_y = self.parent.winfo_y()
		parent_width = self.parent.winfo_width()
		parent_height = self.parent.winfo_height()

		dialog_width = self.winfo_width()
		dialog_height = self.winfo_height()

		x = parent_x + (parent_width // 2) - (dialog_width // 2)
		y = parent_y + (parent_height // 2) - (dialog_height // 2)

		self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")








#################################################################################################
#################################################################################################
#################################################################################################
#################################################################################################
#################################################################################################


# --- Dialog Test Application Class ---
class Application(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title("Main Application")
		self.geometry("250x100")

		self.create_widgets()
		self.center_window()

	def create_widgets(self):
		self.main_frame = ttk.Frame(self, padding="10")
		self.main_frame.grid()
		self.opts = UserOptions()

		self.label = ttk.Label(self.main_frame, text="Welcome to the Main Application!").grid(row=0, column=0)

		ttk.Button(self.main_frame, text="Open Setup Dialog", command=self.open_setup_dialog).grid(row=1, column=0)

	def center_window(self):
		# Update idletasks to ensure the window's requested size is calculated
		# without this, winfo_width/height might return 1 if the window hasn't rendered yet
		self.update_idletasks()

		# Get the screen dimensions
		screen_width = self.winfo_screenwidth()
		screen_height = self.winfo_screenheight()

		# Get the window's current dimensions (after self.geometry() and update_idletasks)
		window_width = self.winfo_width()
		window_height = self.winfo_height()

		# Calculate the top-left corner coordinates for centering
		x = (screen_width // 2) - (window_width // 2)
		y = (screen_height // 2) - (window_height // 2)

		# Set the window's position using geometry method
		# The format is "widthxheight+x+y"
		self.geometry(f"{window_width}x{window_height}+{x}+{y}")

	def open_setup_dialog(self):
		# Pass both initial values to the dialog
		dialog = SetupDialog(self, self.opts)


if __name__ == "__main__":
	_ = lambda t : t
	app = Application()
	app.mainloop()
