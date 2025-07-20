import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from Tooltip import Tooltip




class UserOptions(object):
	def __init__(self) -> None:
		self.printer = 0
		self.reset = 0
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


tt_printer = """Please select the correct printer.
This parameter is very critical because hardware properties of both models are very different and incompatible.

Please if you fail to set the correct option, bad things will happen!"""


tt_reset = """Configuration Reset
This option controls if your printer configuration file will be initialized to factory default.
Usually, there is no need to reset your configuration completely (leave default). 

If the tool notices that your Klipper configuration is useless it will stop and suggests the reset option.
Then you have two options, with or without Klipper calibration data. if your printer behavior is absolutely weird, then also reset calibration."""


tt_model_attr = """Check Model Attributes
This option checks the various model specific configurations for the selected printer model, and fixes elements that doesn't match the factory settings.

This may affect the following settings: stepper motors, printer homing, bed mesh, macros"""


tt_extruder_accel = """Limits Extruder Acceleration
Some printers have a higher extruder acceleration, that has been reduced in recent configurations, probably to avoid higher temperatures on the extruder.
This setting can help reduce extruder temperature and avoid a potential softening of your filament, and clogs as a consequence."""


tt_stepper_z_current = """Higher Stepper Z Current
Usually the X4-Plus model runs with 800mA stepper current for the gantry and the X4-Pro model with 900mA, even is inconsistent, since the Plus model has more weight.

This could fix issues with Z-Axis movement, but the steppers will consume more power."""


tt_extruder_current = """Extruder Run Current
Comparing configurations of the X4-Plus and X4-Pro has an inconsistency on the extruder current, even using the same parts.
The following settings happens to exist:
\t - 800mA: SW X4-Plus
\t - 900mA: average recommendation
\t - 1000mA: SW X4=Pro

Please note that increasing the current will make your extruder stepper warmer and may cause filament softening and potential clogs. On the other side, max filament flow could benefit of it, for faster print."""


tt_probe_offset = """Distance Sensor Offset
The offset value of the probe is slightly inconsistent on the factory settings. You can use this option to correct the offset values for the probe.

Note that Artillery mount this component on the opposite orientation as stated in the data-sheet. One recommended mod is to reorient this sensor according to data-sheet.
If your printer has this mod, then you have to select the "180° Mount" option.

My repository contains series of tests, procedures on how to do this and also links to the data-sheet."""


tt_probe_sampling = """Improved Z-Offset sampling
Regardless of the orientation of your distance sensor, you can improve the Z-offset sampling by using lower approximation speeds and more samples.

By using a more accurate sampling method, the overall Z-offset errors are reduced and first layer of your prints should be more consistent."""


tt_probe_validation = """Improved Z-Offset validation
Besides to better sampling conditions you can reduce the acceptance margin of the sampled data.
This means that after performing the samples all values have to fit a lower error margin to be accepted.

Note that error margins are on the limit. If you activate this option with an unmodified printer it may happen that you printer stops with errors during Z-offset calibration and also during bed-mesh calibration."""


tt_screws_tilt_adjust = """Activate Manual Leveling Feature
Klipper offers you a tool that helps adjusting the screws of your print bed. This option install the necessary configuration.

When activating this option the 'fluidd' interface will show an new "BED_SCREWS_ADJUST" button to perform the calibration. Please check guides on the web on how to use this command.

If you uncheck this option and your configuration already contains screws information, it will be left untouched."""

tt_fan_rename = """Rename Fans
This option renames printer fans to nice names. This is used on the 'fluidd' interface.

The 'Fan 0' is renamed to 'Heatbreak Cooling Fan';
The 'Fan 2' is renamed to 'Mainboard Fan'"""


tt_mb_fan_fix = """Improve Mainboard Fan
On the original configuration main-board fan is only activated by the print nozzle. This configuration is OK if you are doing oly printing.

But it's main function is to cool stepper motor drivers. This means that, if you activate steppers but keep the nozzle off, then perform lots of motion operations, you will overheat your stepper drivers and get errors.

By applying this option, your main-board fan will turn on as soon as any of the following elements are active: heat bed, print nozzle or any of your stepper drivers. So, I strongly recommend you set this option.

In the case you already have this modification the routine will not modify it, regardless if its 'on' or 'off'."""


tt_mb_fan_speed = """Main-board Fan Speed
This option allows you to reduce the speed of the main-board fan. The main goal is to lower noise levels.

You should note that the main function of this fan is to cool down the stepper motor drivers, which may get hot depending on the intensity of acceleration and speed values. If cooling is insufficient a thermal protection of the stepper driver may occur and the motion for the affected axis stops.

In my repository I suggest the mount of a 'fan duct' that concentrates more air flow to the steppers and allows you to safely reduce the fan speed."""


tt_hb_fan_speed = """Heatbreak Fan Speed
This option allows you to reduce the speed of the heatbreak fan. This should reduce the noise levels.

You should consider the following: the main function of this fan is to protect the filament smoothing near the entry of the hot-end, which would easily deform when the extruder pushes. As a consequence you increase the chance of causing clogs if you reduce the cooling fan.

But notice that this was designed for very high temperatures. If your max temperature never goes above 250°C you can reduce this value. This is my case and I use 90%, which already does a good job in noise levels.

Speculative Note: Artillery launched recently a new hot-end, which seems to have less heatsink mass, probably because less weight reduces vibration. On the other side, this could indicate that the old hot-end heatsink is an overkill."""


tt_temp_mcu = """Temperature Reading for Host and MCU
If you se the 'fluidd' interface you will like this option. It activates the temperature sensors for the Host and the motion MCU.

Note that this option does not modify your settings if this sensors are already active."""


tt_nozzle_wipe = """Nozzle Wipe
This macro controls how it will be drawn and Artillery published two different versions of it.
The use of this g-code macro depends on your slicer software configuration.

The legacy version wipes the nozzle many times at a slower speed, but it tends to wear the wipe pad prematurely out. The new version wipes less times but at a faster speed."""


tt_purge_line = """Purge Line
This macro controls how the purge line is drawn and Artillery published two different versions of it.
The use of this g-code macro depends on your slicer software configuration.

The legacy version draws lines in layers and because it causes more adhesion a newer version was developed that is very easy to be removed."""


tt_enable_m600 = """Enable M600
This option adds the new published macros to support the M600 filament change feature.

The following changes will be done:
	- Configuration support for beeper
	- M300 g-code (Play Tone)
	- M600 g-code (Filament Change)
	- T600 g-code (Artillery custom: Resume Print)
	
Note that if these settings are already installed the tool will not modify, neither remove them."""


tt_pause ="""Pause Macro
The pause macro controls the behavior your printer when you press the pause button on the control panel.

The following options are offered:
	- Do Not Change: will not modify it
	- Legacy: Use legacy Artillery code
	- New: Use newer Artillery code
	- Grumat: My custom version.

The new version of Artillery adds support for control parameters used by the M600 command.
My custom version evaluates the filament sensor and docks the print head when filament runs out, which helps not to generate plastic purge over your printed object."""


# --- SetupDialog Class ---
class SetupDialog(tk.Toplevel):
	def __init__(self, parent, opt : UserOptions):
		super().__init__(parent)
		self.parent = parent
		self.title("Setup Dialog")
		self.opt = opt
		self.vars = {}
		self.last_col = 0;

		# Make the dialog modal
		self.transient(parent)
		self.grab_set()

		self.CreateWidgets()
		self.CenterWindow()

		self.protocol("WM_DELETE_WINDOW", self._on_closing)

		self.wait_window(self)

	def CreateWidgets(self):
		# Frame for main content
		self.dlg = ttk.Frame(self, padding="10")
		self.dlg.grid()

		data = [
			[self.CreateColumn, (0,)],

			[self.Title, ("General Settings",)],
			[self.Radio, ("Select Printer Model", ["Artillery SideWinder X4 Pro", "Artillery SideWinder X4 Plus"], "printer")],
			[self.Menu, ("Configuration Reset", ["Update only (default)", "Factory Reset (keep calibration)", "Complete Factory Reset"], "reset")],
			[self.Check, ("Check Model Attributes", "model_attr")],

			[self.Title, ("Gantry",)],
			[self.Check, ("Higher Stepper Z Current", "stepper_z_current")],

			[self.Title, ("Extruder",)],
			[self.Check, ("Limits Extruder Acceleration", "extruder_accel")],
			[self.Menu, ("Extruder Run Current", ["800mA (SW X4-Plus)", "900mA (recommendation)", "1000mA (SW X4-Pro)"], "extruder_current")],

			[self.Title, ("Z-Axis Distance Sensor",)],
			[self.Menu, ("Offset", ["Do not change", "Factory Mount (default)", "180° Mount"], "probe_offset")],
			[self.Check, ("Improved Z-Offset Sampling", "probe_sampling")],
			[self.Check, ("Improved Z-Offset Error Margin", "probe_validation")],

			[self.CreateColumn, (1,)],

			[self.Title, ("Print Bed",)],
			[self.Check, ("Activate Manual Leveling Feature", "screws_tilt_adjust")],

			[self.Title, ("Printer Fans",)],
			[self.Check, ("Rename Fans", "fan_rename")],
			[self.Check, ("Improved Mainboard Fan control", "mb_fan_fix")],
			[self.Menu, ("Mainboard Fan Speed", ["Max (default)", "95%", "90%", "85%", "80%", "75%", "70%"], "mb_fan_speed")],
			[self.Menu, ("Heatbreak Fan Speed", ["Max (default)", "95%", "90%", "85%", "80%", "75%", "70%"], "hb_fan_speed")],

			[self.Title, ("Temperatures",)],
			[self.Check, ("Temperature Reading for Host and MCU", "temp_mcu")],

			[self.Title, ("G-Code",)],
			[self.Menu, ("Nozzle Wipe", ["Do not Change", "Legacy Version", "New Version"], "nozzle_wipe")],
			[self.Menu, ("Purge Line", ["Do not Change", "Legacy Version", "New Version"], "purge_line")],
			[self.Check, ("M600: Filament Change Support", "enable_m600")],
			[self.Menu, ("Pause Macro", ["Do not Change", "Legacy Version", "New Version", "Grumat Version"], "pause")],

			[self.OkCancel, ()],
		]

		for method, args in data:
			method(*args)

	def CreateColumn(self, col):
		c = 2*col
		if c:
			ttk.Separator(self.dlg, orient="vertical").grid(row=0, column=c-1, sticky="ns", padx=15, pady=4)
		self.column = ttk.Frame(self.dlg)
		self.column.grid(row=0, column=c, sticky="nsew", padx=8)
		self.dlg.grid_columnconfigure(c, uniform="same_width")
		self.column.grid_columnconfigure(0, weight=1)
		self.last_col = c
		self.row = 0

	def Empty(self):
		ttk.Label(self.column, text="", state="disabled").grid(row=self.row, column=0)
		self.row += 1

	def Title(self, label):
		py = self.row and (15, 0) or (0, 0)
		frame = ttk.Frame(self.column, borderwidth=2)
		frame.grid(row=self.row, column=0, sticky="ew", pady=py)
		frame.grid_columnconfigure(1, weight=1)
		ttk.Label(frame, text=label, state="disabled").grid(row=0, column=0)
		ttk.Separator(frame, orient="horizontal").grid(row=0, column=1, sticky="ew")
		self.row += 1

	def Finalize(self, widget, var, callback):
		tt = "tt_"+var
		g = globals()
		if tt in g:
			Tooltip(widget, g[tt])
			for wc in widget.winfo_children():
				Tooltip(wc, g[tt])
		if callback:
			widget.config(command=callback)
		self.row += 1

	def Radio(self, title, labels, var, callback = None):
		v = tk.IntVar(self)
		v.set(getattr(self.opt, var))
		self.vars[var] = v
		radio_frame = ttk.LabelFrame(self.column, text=title)
		radio_frame.grid(row=self.row, column=0, sticky="we", padx=(20,0), pady=3)
		for i, label in enumerate(labels):
			ttk.Radiobutton(radio_frame, text=label, variable=v, value=i).grid(row = i, column=0, sticky="w")
		self.Finalize(radio_frame, var, callback)

	def Check(self, label, var, cmd = None, callback = None):
		v = tk.BooleanVar(self)
		v.set(getattr(self.opt, var))
		self.vars[var] = v
		cb = ttk.Checkbutton(self.column, text=label, variable=self.vars[var])
		cb.grid(row=self.row, column=0, sticky="w", padx=(20,0))
		self.Finalize(cb, var, callback)

	def Menu(self, title, labels, var, callback = None):
		v = tk.IntVar(self)
		v.set(getattr(self.opt, var))
		self.vars[var] = v
		frame = ttk.Frame(self.column)
		frame.grid(row=self.row, column=0, sticky="ew", padx=(20,0))
		ml = 0
		for l in labels:
			if ml < len(l):
				ml = len(l)
		frame.grid_columnconfigure(1, weight=1, minsize=ml*6+20)
		ttk.Label(frame, text=title, state="disabled").grid(row=0, column=0)
		om = ttk.OptionMenu(frame, tk.StringVar(self), labels[v.get()], *labels, command=lambda value: v.set(labels.index(value)))
		om.grid(row=0, column=1, sticky="ew")
		self.Finalize(frame, var, callback)

	def OkCancel(self):
		content_frame = ttk.Frame(self.dlg)
		content_frame.grid(row=1, column=0, columnspan=self.last_col+1, sticky="swe", pady=(15, 10), padx=8)
		content_frame.grid_columnconfigure(0, weight=1)
		content_frame.grid_columnconfigure(1, uniform="same_1_2")
		content_frame.grid_columnconfigure(2, uniform="same_1_2")
		# --- OK/Cancel Button ---
		tk.Label(content_frame, text="", state="disabled").grid(row=0, column=0)
		tk.Button(content_frame, text="Ok", command=self._on_save_and_close, width=12).grid(row=0, column=1, padx=4, sticky="we")
		tk.Button(content_frame, text="Cancel", command=self._on_closing, width=12).grid(row=0, column=2, padx=4, sticky="we")


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
	app = Application()
	app.mainloop()
