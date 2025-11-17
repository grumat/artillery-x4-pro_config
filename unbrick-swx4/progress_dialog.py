#
# -*- coding: UTF-8 -*-

import os
import queue
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import scrolledtext, font, StringVar
from my_workflow import Task, TaskState, Workflow, Message, MessageType
from i18n import _
from myenv import *


ATTR_COLUMNS = 2

class CtrlLinks:
	def __init__(self, row : int) -> None:
		self.row = row
		self.widget0 : tb.Label|None = None
		self.widget1 : tb.Label|None = None
		self.bootstyle0 = ""
		self.bootstyle1 = ""
		self.checkmark = StringVar(value="")


class ProgressDialog:
	def __init__(self, parent, workflow :Workflow,title="Progress"):
		self.parent = parent
		self.workflow = workflow
		self.dialog = tb.Toplevel(parent)
		self.dialog.title(_(title))
		self.dialog.transient(parent)  # Make it modal
		self.dialog.grab_set()  # Block interaction with parent
		self.dialog.iconbitmap(os.path.join(GetAssetsFolder(), 'unbrick-swx4.ico'))
		# Disable the close button
		self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)

		self.queue = queue.Queue()
		self.dialog.bind("<<UpdateUI>>", self.UpdateUI)

		self.controls : dict[Task, CtrlLinks] = {}

		# Cancel flag
		self.cancel_flag = False
		self.completed = False

		# Main frame for the grid
		self.main_frame = tb.Frame(self.dialog)
		self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

		# Example grid with 2 columns and 3 rows
		self._build_grid()

		# Scrollable text log
		self._build_log()

		# Progress bar and buttons
		self._build_footer()

		self._center_dialog()
		self._set_cursor_recursive(self.dialog, "watch")

	def _set_cursor_recursive(self, widget, cursor):
		if widget.winfo_name() != "always_action":
			widget.config(cursor=cursor)
			for child in widget.winfo_children():
				self._set_cursor_recursive(child, cursor)

	def _build_grid(self):
		"""Build a 2-column grid with example rows."""
		lines = (len(self.workflow.tasks) + (ATTR_COLUMNS-1))//ATTR_COLUMNS
		item = -1
		for task in self.workflow.tasks:
			item += 1
			row = item % lines
			col = (item // lines) * 2
			ctrl = CtrlLinks(row)
			ctrl.widget0 = tb.Label(self.main_frame, text=_(task.label), bootstyle="primary")
			ctrl.widget0.grid(row=row, column=col, sticky=W, padx=(15,3), pady=2)
			ctrl.widget1 = tb.Label(self.main_frame, textvariable=ctrl.checkmark, anchor="center", bootstyle="inverse-secondary")
			ctrl.widget1.grid(row=row, column=col + 1, sticky=EW, padx=(3,15), pady=2)
			self.controls[task] = ctrl
			self._update_logic(task)
			
		# Configure column weights
		for c in range(ATTR_COLUMNS):
			self.main_frame.columnconfigure(c*2, weight=1, uniform="group1")
			self.main_frame.columnconfigure(c*2+1, weight=0, minsize=120)

	def _update_logic(self, task : Task) -> None:
		if task not in self.controls:
			return
		ctrl = self.controls[task]
		bootstyle0 = ""
		bootstyle1 = ""
		if task.state == TaskState.DISABLED:
			ctrl.checkmark.set("disabled")
			bootstyle0 = "light"
			bootstyle1 = "inverse-light"
		elif task.state == TaskState.RUNNING:
			ctrl.checkmark.set("running")
			bootstyle1 = "inverse-primary"
		elif task.state == TaskState.DONE:
			ctrl.checkmark.set("success")
			bootstyle1 = "inverse-success"
		elif task.state == TaskState.FAIL:
			ctrl.checkmark.set("error")
			bootstyle1 = "inverse-danger"
		else:
			ctrl.checkmark.set("ready")
			bootstyle1 = "inverse-secondary"
		if bootstyle0 and (ctrl.bootstyle0 != bootstyle0):
			ctrl.bootstyle0 = bootstyle0
			ctrl.widget0.configure(bootstyle=bootstyle0)
		if bootstyle1 and (ctrl.bootstyle1 != bootstyle1):
			ctrl.bootstyle1 = bootstyle1
			ctrl.widget1.configure(bootstyle=bootstyle1)

	def _build_log(self):
		"""Add a scrollable text log for output."""
		log_frame = tb.Frame(self.dialog)
		log_frame.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

		# Scrollable text widget
		self.log = scrolledtext.ScrolledText(
			log_frame,
			wrap=tk.WORD,  # Use tk.WORD
			width=80,
			height=20,
			font=("Helvetica", 10),
			state="normal",
			bg="#f0f0f0",
			padx=5,
			pady=5
		)
		self.log.pack(fill=BOTH, expand=True)

		# Define tags for styling
		self.log.tag_config("bold", font=("Helvetica", 10, "bold"))
		self.log.tag_config("warning", foreground="orange")
		self.log.tag_config("error", foreground="red")

	def _log_insert(self, text, tag=None):
		"""Insert text into the log with optional styling."""
		self.log.configure(state="normal")
		self.log.insert(END, text, tag)
		self.log.see(END)  # Auto-scroll to the end
		self.log.configure(state="disabled")

	def _build_footer(self):
		"""Build the progress bar and buttons."""
		footer_frame = tb.Frame(self.dialog, name="always_action")
		footer_frame.pack(fill=X, padx=10, pady=10)

		# Progress bar
		self.progress = tb.Progressbar(
			footer_frame,
			bootstyle="striped-success",
			mode="determinate",
			maximum=100,
			value=0
		)
		self.progress.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))

		# Cancel/Close button
		self.action_button = tb.Button(
			footer_frame,
			text=_("Cancel"),
			bootstyle="danger-outline",
			command=self._on_action
		)
		self.action_button.pack(side=RIGHT, padx=(10, 0))

	def _set_progress(self, value):
		"""Update the progress bar (0-100)."""
		self.progress.configure(value=value)

	def _on_action(self):
		"""Handle Cancel/Close button clicks."""
		if not self.completed:
			self.cancel_flag = True
			self.action_button.configure(state="disabled", text=_("Cancelling..."))
			self.workflow.cancel_flag = True
		else:
			self.Close()

	def UpdateUI(self, event):
		try:
			while True:
				o : Message|Task|int|None = self.queue.get_nowait()
				if o is None:
					self._complete()
				if isinstance(o, int):
					self._set_progress(o)
				elif isinstance(o, Message):
					msg : Message = o
					self._log_insert(msg.msg, msg.type.value)
				elif isinstance(o, Task):
					self._update_logic(o)
		except queue.Empty:
			pass

	def _complete(self):
		"""Mark the process as completed and update the UI."""
		self._set_cursor_recursive(self.dialog, "")
		self.completed = True
		self.action_button.configure(
			text=_("Close"),
			bootstyle="success",
			state="normal"
		)
		Info("Process completed successfully.")
		self._log_insert(_("Process completed successfully.\n"), "bold")
		# Re-enable closing via the 'X' button
		self.dialog.protocol("WM_DELETE_WINDOW", self.Close)

	def _center_dialog(self):
		"""Center the dialog on the screen."""
		self.dialog.update_idletasks()  # Ensure the window is drawn

		# Get screen dimensions
		screen_width = self.dialog.winfo_screenwidth()
		screen_height = self.dialog.winfo_screenheight()

		# Get window dimensions
		window_width = self.dialog.winfo_width()
		window_height = self.dialog.winfo_height()

		# Calculate position to center the window
		x = (screen_width - window_width) // 2
		y = (screen_height - window_height) // 2

		# Set the window position
		self.dialog.geometry(f"+{x}+{y}")

	def Show(self):
		"""Show the dialog and wait for it to close."""
		self.dialog.wait_window()
		return not self.cancel_flag  # Return True if not cancelled

	def Close(self):
		"""Close the dialog."""
		self.dialog.grab_release()
		self.dialog.destroy()


if __name__ == "__main__":
	pass
