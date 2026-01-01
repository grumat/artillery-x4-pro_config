#
# -*- coding: UTF-8 -*-
#
# Spellchecker:: words klipper fluidd mainboard grumat

from i18n import N_


tt_ip_addr = N_(
	"""Printer IP Address

What to do: Enter the IP address displayed in your printer's network setup menu. This tool uses SSH to connect to your printer, using Artillery's default password.

Important Note: If you've changed the SSH password from the factory default, this tool won't be able to connect. You'll need to reset the password."""
)


tt_printer = N_(
	"""Select Your Printer Model

Why this matters: The Sidewinder X4 Pro and X4 Plus have different hardware. Choosing the wrong model can cause serious printing issues.

What to do:
- Double-check your printer model before selecting.
- If you make a mistake, simply run this tool again with the correct model.

Warning: Using the wrong setting may lead to failed prints or other problems. Always verify your selection!""")


tt_reset = N_(
	"""Reset Printer Configuration

What it does: This option lets you restore your printer's configuration file to factory defaults.

When to use it:
- Usually, you don't need this. The tool only adjusts specific settings, so a full reset is rarely required.
- Enable it only if the tool fails to fix your Klipper configuration issues.

Your choices:
- Reset settings only: Keeps your calibration data intact.
- Reset settings and calibration: Use this if your printer is behaving unpredictably.

Recommendation: Start with the default (no reset). Only use this option as a last resort."""
)


tt_optimize_disk_space = N_(
	"""Optimize Disk Space

What it does: This tool cleans up unnecessary files, such as:
- Old print files and thumbnails
- Leftover developer files that Artillery forgot to remove

Why use it? Your printer's 8GB eMMC disk has limited space. If the system runs out of space, your printer may fail to boot or function properly.

Recommendation: Enable this option regularly to free up space and keep your printer running smoothly."""
)


tt_file_permissions = N_(
	"""Fix File Permissions

What it does: Some files on your printer's factory installation may have incorrect permissions. While most of these issues are harmless, they can occasionally cause problems.

Why use this tool? This tool checks and corrects file permissions to ensure:
- The Klipper environment can access all necessary files.
- Your printer runs smoothly without permission-related errors.

When to use it: Run this tool if you notice unexpected errors or after a fresh installation. It's safe and won't make unnecessary changes."""
)


tt_resize_bug = N_(
	"""Fix Disk Resize Bug

What it does: The Artillery Sidewinder X4 Plus sometimes shows a warning in the system log about disk partition resizing. This is a known issue, but it's mostly harmless — it only affects performance slightly.

Why use this tool? This tool checks if the problem exists on your printer and applies a fix if needed. It's safe to run and won't make changes unless the issue is detected.

When to use it: Enable this tool if you see disk resize warnings in your logs or want to ensure optimal performance."""
)


tt_trim = N_(
	"""Trim eMMC Storage

What it does: Your printer uses an 8GB (or optional 32GB) eMMC to store the operating system, Klipper, and your print files. Over time, deleted files leave behind "garbage" data, which can slow down the system.

Why use this tool?
- eMMC memory doesn't automatically clean up deleted files right away.
- Running TRIM removes this leftover data, keeping your printer's storage fast and reliable.

When to use it: Run this tool occasionally to maintain performance, especially if your printer feels sluggish."""
)


tt_model_attr = N_(
	"""Fix Printer Model Settings

What it does: This tool checks your printer's current settings and automatically corrects any mismatches with the selected printer model (e.g., Sidewinder X4 Pro or X4 Plus).

Why use it?
It ensures that critical Klipper settings are properly configured for your specific printer model. This may include:
- Stepper motor settings
- Printer homing behavior
- Bed mesh configuration
- Custom macros

When to use it: Run this tool if you've changed your printer model in the control panel or if you suspect settings are incorrect."""
)


tt_exclude_object = N_(
	"""Enable Exclude Object

What it does: Turns on Klipper's "Exclude Object" feature, allowing you to cancel individual objects during a multi-object print.

How it works:
- Pause your print, select the object(s) to exclude, and resume — Klipper will skip them.

Important: This feature only works if your slicer is configured to support it. Check your slicer's settings for "Exclude Object" or "Cancel Objects" options."""
)


tt_stepper_z_current = N_(
	"""Z-Axis Stepper Motor Hold Current

What it does: This setting determines how much power the Z-axis motors use to hold their position when the printer is idle.

Available options:
- 800mA (recommended for most users)
- 900mA (only if you notice the Z-axis slipping or losing position)

Factory defaults:
- X4-Plus: 800mA
- X4-Pro: 900mA

Note: The X4-Plus has more weight to hold, so the factory default of 800mA might seem low compared to the X4-Pro. However, 800mA is usually sufficient unless you experience issues."""
)


tt_extruder_accel = N_(
	"""Extruder Acceleration Limit

Why it matters: This setting controls how quickly the extruder motor speeds up or slows down. Older firmware versions used higher acceleration, but newer versions have reduced it.

What you need to know:
- Higher acceleration can cause the extruder motor to heat up more.
- Too much heat may soften the filament inside the extruder, increasing the risk of clogs.

Recommendation: Unless you're experiencing issues, stick with the default or lower acceleration setting to keep temperatures stable."""
)


tt_extruder_current = N_(
	"""Extruder Motor Current Settings

The Sidewinder X4-Plus and X4-Pro use the same extruder, but their factory settings for motor current differ. This inconsistency might be an oversight. Here's what you need to know:
- X4-Plus: 800mA (factory setting)
- Common recommendation: 900mA
- X4-Pro: 1000mA (factory setting)

What does this mean for you?

Higher current (e.g., 1000mA): The extruder motor runs hotter, which may increase the risk of clogs. Can improve filament flow for faster prints.

Lower current (e.g., 800mA): Motor stays cooler, reducing clog risk. May limit maximum print speed.

Recommendation: If you're unsure, start with 900mA — a balanced setting for most users. Adjust based on your printing needs and monitor for overheating or clogs."""
)


tt_probe_logic = N_(
	"""Input Pin Polarity

What it does: Adjusts the probe's input pin logic level.

Important Note: This feature is only intended to use if you replaced your inductive sensor to the professional grade "Panasonic GX-H12A".

Need help? My repository includes:
- Test procedures
- Step-by-step guides
- Links to the official data sheet"""
)


tt_probe_offset = N_(
	"""Distance Sensor Offset

What it does: Adjusts the probe offset to correct inconsistencies in the factory settings.

Important Note: Artillery mounts the sensor backwards compared to the manufacturer's recommendations. For best results, we recommend modifying the sensor's orientation to match the official data sheet.

If you've already done this mod: Select the "180° Mount" option.

Need help? My repository includes:
- Test procedures
- Step-by-step guides
- Links to the official data sheet"""
)


tt_probe_sampling = N_(
	"""Improve Z-Offset Sampling

What it does: Enhances the accuracy of your Z-offset by using:
- Slower sampling speeds
- More samples for better precision

Why use it? A more accurate Z-offset reduces errors and helps ensure a consistent first layer for your prints — regardless of your distance sensor's orientation."""
)


tt_probe_validation = N_(
	"""Improve Z-Offset Validation

What it does: Makes Z-offset calibration stricter by reducing the allowed error margin for sampled data. This ensures only the most precise measurements are accepted.

Result: More reliable Z-offset and bed mesh calibration, leading to better first layers.

Important: If your printer hasn't been modified, enabling this option may cause calibration errors or failures. Use only if your printer is properly tuned."""
)


tt_screws_tilt_adjust = N_(
	"""Enable Manual Bed Leveling

What it does: Activates Klipper's manual bed leveling tool, which helps you adjust your print bed screws for a perfectly level surface.

How it works:
- A "BED_SCREWS_ADJUST" button will appear in the Fluidd interface.
- Follow the on-screen instructions or check online guides for step-by-step help.

Note: If you disable this option later, any existing screw adjustment settings in your configuration will remain unchanged."""
)


tt_fan_rename = N_(
	"""Rename Fans for Clarity

What it does: Renames your printer's fans in the Fluidd interface for easier identification:
- "Fan 0" → "Heat Break Cooling Fan"
- "Fan 2" → "Mainboard Fan"

Why use it? Makes it simpler to control and monitor the right fan at a glance."""
)


tt_mb_fan_fix = N_(
	"""Enhanced Mainboard Fan Control

What's the issue? The factory setting only turns on the mainboard fan when the print nozzle is active. While this works for basic printing, it ignores the fan's real purpose: cooling the stepper motor drivers.

Why is this a problem? If you move the printer a lot (e.g., homing, manual moves) without heating the nozzle, the stepper drivers can overheat, causing errors or shutdowns.

What this option does: The fan will now activate whenever any of these are active:
- Heat bed
- Print nozzle
- Stepper drivers (most critical!)

Recommendation: Enable this option to prevent overheating and improve reliability.

Note: If you've already customized this setting, the tool won't override your changes."""
)


tt_mb_fan_speed = N_(
	"""Adjust Mainboard Fan Speed

What it does: Lets you reduce the speed of the mainboard fan to lower noise levels.

Important Note: The mainboard fan's primary job is to cool the stepper motor drivers, which can heat up during fast or intense movements. If cooling is insufficient, a driver may overheat, triggering thermal protection and stopping the affected axis.

Recommendation:
- If you want to reduce fan noise, consider installing a fan duct (available in my repository). This focuses airflow directly on the stepper drivers, allowing you to safely lower the fan speed.
- Only reduce fan speed if you've not speeding your printer to the limits."""
)


tt_hb_fan_speed = N_(
	"""Adjust Heat-Break Fan Speed

What it does: Lets you reduce the speed of the heat-break fan to lower noise levels.

Key Considerations:
- The heat-break fan prevents filament from softening near the hot-end entry, which can cause clogs if cooling is insufficient.
- The default speed is designed for high-temperature printing (above 250°C).

Recommendation:
- If you rarely print above 250°C, you can safely reduce the fan speed (e.g., to 90%), which noticeably lowers noise without risking clogs.
- Monitor your prints after adjusting — if clogs occur, increase the fan speed.

Note: Artillery's newer print heads use a smaller heat sink, suggesting the original design may be overbuilt. This further supports reducing fan speed for most users."""
)


tt_temp_mcu = N_(
	"""Enable Host & MCU Temperature Monitoring

What it does: Activates temperature sensors for:
- Host CPU (your printer's main processor)
- MCU drivers (stepper motor controllers)

Why use it? If you use the Fluidd interface, this lets you monitor temperatures in real time — helping you spot overheating issues early.

Note: If these sensors are already enabled, this option won't change your existing settings."""
)


tt_nozzle_wipe = N_(
	"""Nozzle Wipe Settings

What it does: Controls how the nozzle is cleaned between prints. Artillery offers two versions of this macro:
- Legacy version: Multiple slow wipes — can wear out the wipe pad faster.
- New version: Fewer, faster wipes — reduces pad wear but cleans efficiently.

Note: Changing this setting only affects prints if your slicer is configured to use the nozzle wipe feature. If your slicer doesn't trigger it, you won't see a difference."""
)


tt_purge_line = N_(
	"""Purge Line Settings

What it does: Controls how the purge line is printed before your model starts. Artillery offers two versions, plus an improved option:
- Legacy version: Prints stacked lines — can stick too well to the bed.
- New version: Prints a single, easy-to-remove line.
- "Grumat" version: Adjusts for retraction to prevent under-extrusion at the start of your print.

Note: This setting only applies if your slicer is configured to use a purge line. If your slicer doesn't trigger it, you won't see any changes."""
)


tt_enable_m600 = N_(
	"""Enable Filament Change (M600 Support)

What it does: Adds support for the M600 filament change feature, including:
- Beeper configuration (for audio alerts)
- M300 macro (Play Tone)
- M600 macro (Filament Change)
- T600 macro (Artillery's custom "Resume Print" command)

Why use it? Lets you pause prints, swap filament, and resume seamlessly — ideal for multi-color or multi-material prints.

Note: The "Grumat" version includes the same functionality but follows best practices for cleaner, more maintainable code."""
)


tt_pause = N_(
	"""Pause Macro Settings

What it does: Controls how your printer behaves when a print job is paused — whether manually or due to an issue (e.g., filament change or power loss).

Available Options:
- Do Not Change: Keeps your current pause macro.
- Legacy: Uses Artillery's original pause macro.
- New: Uses Artillery's updated pause macro, with support for M600 filament change parameters.
- Grumat (Custom): Based on Artillery's new macro, but adds filament sensor support. If filament runs out, it:
   - Homes the print head.
   - Moves the printed object away to avoid purging filament over it.

Recommendation: Choose "Grumat" for the most reliable pause behavior, especially if you use a filament sensor or frequently change filament mid-print."""
)
