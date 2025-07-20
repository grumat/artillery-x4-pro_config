import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont


class Tooltip:
	def __init__(self, widget, text):
		self.widget = widget
		self.title_text, self.description_text = text.split('\n', 1)
		self.tip_window = None
		self.id = None
		self.x = 0
		self.y = 0

		# Define custom fonts for the tooltip
		self.bold_font = tkFont.Font(family="tahoma", size=8, weight="bold")
		self.normal_font = tkFont.Font(family="tahoma", size=8, weight="normal")

		# Bind events to the widget
		self.widget.bind("<Enter>", self.enter)
		self.widget.bind("<Leave>", self.leave)
		self.widget.bind("<ButtonPress>", self.leave) # Hide if clicked

	def enter(self, event=None):
		"Called when the mouse pointer enters the widget"
		self.schedule()

	def leave(self, event=None):
		"Called when the mouse pointer leaves the widget"
		self.unschedule()
		self.hide_tip()

	def schedule(self):
		"Schedules the tooltip to appear after a delay"
		self.unschedule() # Ensure no previous schedule
		self.id = self.widget.after(500, self.show_tip) # Show after 500ms

	def unschedule(self):
		"Cancels any scheduled tooltip appearance"
		if self.id:
			self.widget.after_cancel(self.id)
			self.id = None

	def show_tip(self, event=None):
		"Creates and displays the tooltip window"
		if self.tip_window or (not self.title_text and not self.description_text):
			return

		# Get the current position of the mouse relative to the screen
		x = self.widget.winfo_pointerx() + 10 # Offset slightly
		y = self.widget.winfo_pointery() + 10

		self.tip_window = tk.Toplevel(self.widget)
		self.tip_window.wm_overrideredirect(True) # Remove window decorations
		self.tip_window.wm_geometry(f"+{x}+{y}")

		# Create a Frame to hold the title and description labels
		# This frame will have the common tooltip background and border
		content_frame = ttk.Frame(self.tip_window,
									style="Tooltip.TFrame", # Use a themed style for consistency
									padding=(4, 2) # Internal padding for the whole tooltip content
									)
		content_frame.pack(fill="both", expand=True)

		# Configure a style for the frame if using ttk
		style = ttk.Style()
		style.configure("Tooltip.TFrame",
						background="#ffffe0", # Light yellow background
						relief=tk.SOLID,
						borderwidth=1
						)

		# --- Title Label (Bold) ---
		if self.title_text:
			title_label = tk.Label(content_frame,
									text=self.title_text,
									font=self.bold_font,
									background="#ffffe0", # Match frame background
									justify=tk.LEFT,
									padx=0, pady=0 # No extra padding as frame has it
									)
			title_label.pack(fill="x", padx=0, pady=0, anchor="w") # Pack to fill width, align left

		# --- Description Label (Normal, Multi-line, Word-Wrap) ---
		if self.description_text:
			# Add a small separator space if both title and description exist
			if self.title_text:
				ttk.Separator(content_frame, orient="horizontal").pack(fill="x", pady=1)

			desc_label = tk.Label(content_frame,
									text=self.description_text,
									font=self.normal_font,
									background="#ffffe0", # Match frame background
									justify=tk.LEFT,
									wraplength=300,        # Adjust this pixel width for wrapping
									padx=0, pady=0
									)
			desc_label.pack(fill="x", padx=0, pady=0, anchor="w")

	def hide_tip(self):
		"Destroys the tooltip window"
		if self.tip_window:
			self.tip_window.destroy()
			self.tip_window = None

