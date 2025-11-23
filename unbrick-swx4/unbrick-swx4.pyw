#
# -*- coding: UTF-8 -*-

"""
This scripts automates the un-bricking of Artillery Sidewinder X4 printers.
"""

# spellchecker: words themename padx pady bootstyle columnspan Grumat uopts unbrick klipper

from i18n import SetupI18nAuto, _, N_
import os

# spellchecker:disable
import ttkbootstrap as tb
from ttkbootstrap.constants import BOTH, NSEW, EW, W, RIGHT
from ttkbootstrap.widgets import ToolTip
# spellchecker:enable

from user_options import UserOptions
import help
from progress_dialog import ProgressDialog
from my_workflow import Workflow
from my_env import GetAssetsFolder, GetIniFileName, Info



class SetupDialog:
	def __init__(self, fields, title="", initial_values=None):
		self.app = tb.Window(themename="superhero")
		self.app.title(_(title))  # Translate window title
		self.app.iconbitmap(os.path.join(GetAssetsFolder(), 'unbrick-swx4.ico'))
		self.widgets = {}
		self.values = None
		self.fields = fields
		self.tooltip_style = "info"

		# Create a frame for the two columns
		self.main_frame = tb.Frame(self.app)
		self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

		# Left and right column frames
		self.left_frame = tb.Frame(self.main_frame)
		self.left_frame.grid(row=0, column=0, sticky=NSEW, padx=20)
		self.right_frame = tb.Frame(self.main_frame)
		self.right_frame.grid(row=0, column=1, sticky=NSEW, padx=20)

		# Configure grid weights for resizing
		self.main_frame.columnconfigure(0, weight=1)
		self.main_frame.columnconfigure(1, weight=1)
		self.left_frame.columnconfigure(1, weight=1)
		self.right_frame.columnconfigure(1, weight=1)

		self._build_dialog(initial_values)

		# Bind to the window's idle task to adjust widths after everything is loaded
		self.app.after_idle(self._adjust_widget_widths)

	def _build_dialog(self, initial_values):
		current_frame = self.left_frame
		row_base = row = 0

		for field in self.fields:
			if field.get("column_break", False):
				current_frame = self.right_frame
				row = row_base
				continue

			if field.get("section_break", False):
				separator = tb.Separator(self.left_frame, orient="horizontal", bootstyle="primary")
				separator.grid(row=row, column=0, columnspan=2, sticky=EW, pady=(15, 10))
				separator = tb.Separator(self.right_frame, orient="horizontal", bootstyle="primary")
				separator.grid(row=row, column=0, columnspan=2, sticky=EW, pady=(15, 10))
				row += 1
				current_frame = self.left_frame
				row_base = row
				continue

			type = field["type"]
			if type == "title":
				title_label = tb.Label(current_frame, text=_(field["text"]), font=("Helvetica", 10, "bold"))
				title_label.grid(row=row, column=0, columnspan=2, sticky=W, pady=(10, 0))
				row += 1
				separator = tb.Separator(current_frame, orient="horizontal")
				separator.grid(row=row, column=0, columnspan=2, sticky=EW, pady=(0, 10))
				row += 1
				continue

			name = field["name"]
			tooltip = ""
			if hasattr(help, 'tt_' + name):
				tooltip = _(getattr(help, 'tt_' + name))
			if type == "checkbox":
				var = tb.BooleanVar()
				cb = tb.Checkbutton(current_frame, text=_(field["text"]), variable=var, bootstyle="primary,round-toggle")
				cb.grid(row=row, column=0, columnspan=2, sticky=W, pady=5)
				if tooltip:
					ToolTip(cb, text=tooltip, bootstyle=self.tooltip_style)
				self.widgets[name] = var
				if initial_values:
					value = getattr(initial_values, name)
					var.set(value)
				row += 1
				continue

			# Label (translated)
			label = tb.Label(current_frame, text=_(field["label"]), anchor=W)
			label.grid(row=row, column=0, sticky=W, padx=(0, 5), pady=5)
			if tooltip:
				ToolTip(label, text=tooltip, bootstyle=self.tooltip_style)

			# Entry or Combobox
			if type == "entry":
				entry = tb.Entry(current_frame, bootstyle="primary")
				entry.grid(row=row, column=1, sticky=EW, pady=5)
				if tooltip:
					ToolTip(entry, text=tooltip, bootstyle=self.tooltip_style)
				self.widgets[name] = entry
				if initial_values:
					value = getattr(initial_values, name)
					entry.insert(0, value)

			elif type == "combobox":
				# Translate combobox options
				translated_options = [_(opt) for opt in field["options"]]
				combo = tb.Combobox(current_frame, values=translated_options, state="readonly", bootstyle="primary")
				combo.grid(row=row, column=1, sticky=EW, pady=5)
				if tooltip:
					ToolTip(combo, text=tooltip, bootstyle=self.tooltip_style)
				self.widgets[name] = combo
				if initial_values:
					value = getattr(initial_values, name)
					if isinstance(value, int):
						combo.current(value)
					else:
						try:
							# Try to match the translated value
							translated_value = _(value)
							index = translated_options.index(translated_value)
							combo.current(index)
						except ValueError:
							pass

			row += 1

		# Button frame (spanning both columns)
		button_frame = tb.Frame(self.main_frame)
		button_frame.grid(row=1, column=0, columnspan=2, sticky=EW, padx=10, pady=10)

		# Exit button (translated)
		tb.Button(button_frame, text=_("Exit"), bootstyle="danger", command=self._on_exit).pack(side=RIGHT, padx=5)
		# Run button (translated)
		tb.Button(button_frame, text=_("Run"), bootstyle="success", command=self._on_run).pack(side=RIGHT, padx=5)

		self.app.protocol("WM_DELETE_WINDOW", self._on_exit)

	def _center_dialog(self):
		"""Center the dialog on the screen."""
		self.app.update_idletasks()  # Ensure the window is drawn

		# Get screen dimensions
		screen_width = self.app.winfo_screenwidth()
		screen_height = self.app.winfo_screenheight()

		# Get window dimensions
		window_width = self.app.winfo_width()
		window_height = self.app.winfo_height()

		# Calculate position to center the window
		x = (screen_width - window_width) // 2
		y = (screen_height - window_height) // 2

		# Set the window position
		self.app.geometry(f"+{x}+{y}")

	def _adjust_widget_widths(self):
		"""Adjust the width of each widget based on its actual translated content"""
		for field in self.fields:
			if "name" not in field:
				continue
			if field["name"] not in self.widgets:
				continue

			widget = self.widgets[field["name"]]

			if isinstance(widget, tb.Combobox):
				# For comboboxes, find the longest translated option or current selection
				options = [_(opt) for opt in field["options"]] if type == "combobox" else []
				current_text = widget.get()

				# Calculate max length considering all options and current selection
				max_len = max(len(current_text), *(len(opt) for opt in options), 25)
				widget.configure(width=max_len)

			elif isinstance(widget, tb.Entry):
				# For entries, set width based on current content
				content = widget.get()
				# Estimate width based on average character width (simplified)
				width = max(len(content), 25)
				widget.configure(width=width)

	def _on_run(self):
		self.values = self._get_values()
		self.values.SaveIni(GetIniFileName())
		workflow = Workflow(self.values)
		# Launch the progress dialog
		progress_dialog = ProgressDialog(self.app, workflow, title=_("Processing..."))

		workflow.Do(progress_dialog.dialog, progress_dialog.queue)

	def _on_exit(self):
		self.values = None
		self.app.destroy()

	def _get_values(self):
		values = UserOptions()
		for name, widget in self.widgets.items():
			if isinstance(widget, tb.Combobox):
				setattr(values, name, widget.current())
			elif isinstance(widget, tb.Entry):
				target = widget.get()
				setattr(values, name, widget.get())
			elif isinstance(widget, tb.BooleanVar):
				setattr(values, name, widget.get())
		return values

	def Show(self):
		self.app.update_idletasks()
		self.app.geometry("")
		self.app.minsize(500, 300)
		self._center_dialog()  # Center the dialog
		self.app.mainloop()
		return self.values

# Example usage:
fields = [
	{"type": "entry", 		"name": "ip_addr", 				"label": N_("Printer IP Address"), },
	{"column_break": True},		# Switch to the right column
	{"type": "combobox", 	"name": "printer", 				"label": N_("Select Printer Model"), "options": [N_("Artillery SideWinder X4 Pro"), N_("Artillery SideWinder X4 Plus")], },
	{"section_break": True},	# New section

	{"type": "title", 										"text": N_("Linux Operating System Cleanup")},
	{"type": "checkbox", 	"name": "optimize_disk_space", 	"text": N_("Optimize Disk Space"), "label": ""},
	{"type": "checkbox", 	"name": "file_permissions", 	"text": N_("Fix File Permission"), "label": ""},
	{"type": "checkbox", 	"name": "resize_bug", 			"text": N_("Fix Resize Bug"), "label": ""},
	{"type": "checkbox", 	"name": "trim", 				"text": N_("Trim eMMC"), "label": ""},

	{"type": "title", 										"text": N_("Klipper Hardware Configuration")},
	{"type": "combobox", 	"name": "reset", 				"label": N_("Configuration Reset"), "options": [N_("Update only (default)"), N_("Factory Reset (keep calibration)"), N_("Complete Factory Reset")], },
	{"type": "checkbox", 	"name": "model_attr", 			"text": N_("Fix Printer Model Settings"), "label": ""},

	{"type": "title", 										"text": N_("Gantry")},
	{"type": "combobox", 	"name": "stepper_z_current", 	"label": N_("Stepper Z Current"), "options": [N_("800mA"), N_("900mA")], },

	{"type": "title", 										"text": N_("Extruder")},
	{"type": "checkbox", 	"name": "extruder_accel", 		"text": N_("Limits Extruder Acceleration"), "label": ""},
	{"type": "combobox", 	"name": "extruder_current", 	"label": N_("Extruder Run Current"), "options": [N_("800mA (SW X4-Plus)"), N_("900mA (recommendation)"), N_("1000mA (SW X4-Pro)")], },
	
	{"type": "title", 										"text": N_("Z-Axis Distance Sensor")},
	{"type": "combobox",  	"name": "probe_offset", 		"label": N_("Offset"), "options": [N_("Do not change"), N_("Factory Mount (default)"), N_("180° Mount")], },
	{"type": "checkbox", 	"name": "probe_sampling", 		"text": N_("Improved Z-Offset Sampling"), "label": ""},
	{"type": "checkbox", 	"name": "probe_validation", 	"text": N_("Improved Z-Offset Error Margin"), "label": ""},


	{"column_break": True},  # Switch to the right column

	{"type": "title", 										"text": N_("Print Bed")},
	{"type": "checkbox", 	"name": "screws_tilt_adjust", 	"text": N_("Activate Manual Leveling Feature"), "label": ""},

	{"type": "title", 										"text": N_("Printer Fans")},
	{"type": "checkbox", 	"name": "fan_rename", 			"text": N_("Rename Fans"), "label": ""},
	{"type": "checkbox", 	"name": "mb_fan_fix", 			"text": N_("Improved Main-board Fan control"), "label": ""},
	{"type": "combobox",  	"name": "mb_fan_speed", 		"label": N_("Main-board Fan Speed"), "options": [N_("Max (default)"), N_("95%"), N_("90%"), N_("85%"), N_("80%"), N_("75%"), N_("70%")], },
	{"type": "combobox",  	"name": "hb_fan_speed", 		"label": N_("Heat-break Fan Speed"), "options": [N_("Max (default)"), N_("95%"), N_("90%"), N_("85%"), N_("80%"), N_("75%"), N_("70%")], },

	{"type": "title", 										"text": N_("Temperatures")},
	{"type": "checkbox", 	"name": "temp_mcu", 			"text": N_("Temperature Reading for Host and MCU"), "label": ""},

	{"type": "title", 										"text": N_("G-Code")},
	{"type": "combobox",  	"name": "nozzle_wipe", 			"label": N_("Nozzle Wipe"), "options": [N_("Do not Change"), N_("Legacy Version"), N_("New Version")], },
	{"type": "combobox",  	"name": "purge_line", 			"label": N_("Purge Line"), "options": [N_("Do not Change"), N_("Legacy Version"), N_("New Version")], },
	{"type": "checkbox", 	"name": "enable_m600",			"text": N_("M600: Filament Change Support"), "label": ""},
	{"type": "combobox",  	"name": "pause", 				"label": N_("Pause Macro"), "options": [N_("Do not Change"), N_("Legacy Version"), N_("New Version"), N_("Grumat Version")], },
]



if __name__ == "__main__":
	Info('Starting Application')
	SetupI18nAuto()
	uopts = UserOptions()
	uopts.LoadIni(GetIniFileName())
	dialog = SetupDialog(fields, title=N_("Artillery SideWinder X4 Unbrick Tool v0.2"), initial_values=uopts)
	dialog.Show()


