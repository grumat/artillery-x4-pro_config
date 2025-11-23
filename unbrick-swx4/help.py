#
# -*- coding: UTF-8 -*-
#
# Spellchecker:: words klipper fluidd mainboard grumat

from i18n import N_


tt_printer = N_(
	"""Please select the correct printer.
This parameter is very critical because hardware properties of both models are very different and incompatible.

If you fail to set the correct option, bad things will happen when you try to print something.

You can always repeat this tool with the correct option to fix a bad choice.""")


tt_reset = N_(
	"""Configuration Reset
This option controls if your printer configuration file will be initialized to factory default.
Usually, there is no need to reset your configuration completely, because the tool will modify only very specific settings.

So, leave the default value and only if the tool notices that your Klipper configuration is broken it will stop and suggests the reset option.
Then you have two options, with or without Klipper calibration data. If your printer behavior is absolutely weird, you should also reset calibration.""")


tt_optimize_disk_space = N_(
	"""Optimize Disk Space
This option erases old files, miniatures and also remove known developer files that "Artillery" just forgot to clear.

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
This type of memory technology suffers from one strong limitation: Memory clean costs too much time.

As a countermeasure OS uses a technique called garbage collection, which means, old data is actually not erased.
At some point, OS has to execute an operation called TRIM, that really erase the garbage.

This tool runs a TRIM operation to keep your eMMC fresh and speedy."""
)


tt_model_attr = N_(
	"""Fix Printer Model Settings
This option checks the various specific configurations for the selected printer model, and fixes elements that doesn't match your selection.

These tool checks very essential Klipper settings. This may affect the following settings: stepper motors, printer homing, bed mesh and macros.""")


tt_extruder_accel = N_(
	"""Limits Extruder Acceleration
This setting can help reduce extruder temperature.

Some older firmware have a higher extruder acceleration setting. But it has been reduced in recent configurations, probably to avoid higher temperatures on the extruder.

Too much temperature in the extruder stepper has the potential to soften your filament and cause clogs.""")


tt_stepper_z_current = N_(
	"""Stepper Z Current
For this option you can select between 800mA and 900mA. It is recommended to use the lower value except if you are experiencing Z-Axis movement issues.

Note: Factory default values for the X4-Plus model is 800mA, while the X4-Pro model uses 900mA. This seems inconsistent, since the Plus model has more mass to move.""")


tt_extruder_current = N_(
	"""Extruder Run Current
Comparing configurations of the X4-Plus and X4-Pro has an inconsistency on the extruder current. It does not make sense if both uses the same head and seems that the factory did not pay due attention to the point.
The following settings happens to exist:
\t- 800mA: SW X4-Plus
\t- 900mA: average recommendation
\t- 1000mA: SW X4=Pro

Please note that increasing the current will make your extruder stepper warmer and potentially more susceptible to clogging. On the other side, max filament flow could benefit of it, for faster prints.""")


tt_probe_offset = N_(
	"""Distance Sensor Offset
The offset value of the probe is slightly inconsistent on the factory settings. You can use this option to correct the offset values for the probe.

Note that Artillery mount this component on the opposite orientation of the data-sheet recommendation. So I strongly recommended a mod that reorient this sensor and follows the data-sheet mounting examples.
If your printer has this mod, then you have to select the "180° Mount" option.

My repository contains series of tests, procedures on how to do this and also links to the data-sheet.""")


tt_probe_sampling = N_(
	"""Improved Z-Offset sampling
Regardless of the orientation of your distance sensor, you can improve the Z-offset sampling by using lower approximation speeds and more samples.

By using a more accurate sampling method, the overall Z-offset errors are reduced and first layer of your prints should be more consistent.""")


tt_probe_validation = N_(
	"""Improved Z-Offset validation
Besides improving sampling conditions, you can reduce the acceptance threshold for the sampled data.
This means that after performing the samples, value differences have to fit a lower error margin to be accepted.

Note that error margins are on the limit. If you activate this option with an unmodified printer it may happen that you printer stops with errors during Z-offset calibration and also during bed-mesh calibration.""")


tt_screws_tilt_adjust = N_(
	"""Activate Manual Leveling Feature
Klipper offers you a tool that helps adjusting the screws of your print bed. This option installs the necessary configuration.

When activating this option the 'fluidd' interface will show a new "BED_SCREWS_ADJUST" button to perform the calibration. There are various guides on the web on how to use this command.

If you uncheck this option and your configuration already contains screws information, it will be left untouched.""")


tt_fan_rename = N_(
	"""Rename Fans
This option renames printer fans to nice names. This is used on the 'fluidd' interface.

The 'Fan 0' is renamed to 'Heat break Cooling Fan';
The 'Fan 2' is renamed to 'Mainboard Fan'.""")


tt_mb_fan_fix = N_(
	"""Improved Mainboard Fan
On the original configuration main-board fan is only activated by the print nozzle. This configuration is OK if you are doing only printing.

But it's main function is to keep stepper motor drivers cool. This means that, if you activate steppers but keep the nozzle off, then perform lots of motion operations, you will overheat your stepper drivers and get errors.

By applying this option, your main-board fan will turn on as soon as any of the following elements are active: heat bed, print nozzle or any of your stepper drivers. So, I strongly recommend you set this option.

In the case you already have this modification the routine will not modify it, regardless if its 'on' or 'off'.""")


tt_mb_fan_speed = N_(
	"""Main-board Fan Speed
This option allows you to reduce the speed of the main-board fan. The main goal is to lower noise levels.

You should note that the main function of this fan is to cool the stepper motor drivers down, which may get hot depending on the intensity of acceleration and speed values. If cooling is insufficient a thermal protection may occur on one of the stepper drivers and the motion for the affected axis stops.

In my repository I suggest the mount of a 'fan duct' that concentrates more air flow to the steppers drivers and allows you to safely reduce the fan speed.""")


tt_hb_fan_speed = N_(
	"""  Fan Speed
This option allows you to reduce the speed of the heat break fan. This should reduce the noise levels.

Please consider the following: the main function of this fan is to protect the filament smoothing near the entry of the hot-end, which could deform when the extruder pushes. If you reduce the cooling fan too much you may experience clogs on the cold end.

But notice that this setup was designed for very high temperatures. If your max temperature never goes above 250°C you can reduce this value. This is my case and I use 90%, which already does a good job in noise levels.

Speculative Note: Artillery launched recently a new print head, which seems to have less heat sink mass, which reduces inertia. On the other hand, this indicates that the old heat sink is over dimensioned.""")


tt_temp_mcu = N_(
	"""Temperature Reading for Host and MCU
If you use the 'fluidd' interface you will like this option: It activates the temperature sensors for the Host CPU and the drivers MCU.

Note that this option does not modify your settings if this sensors are already active.""")


tt_nozzle_wipe = N_(
	"""Nozzle Wipe
This macro controls how the nozzle will be cleaned. But, "Artillery" published two different versions of it.

The legacy version wipes the nozzle many times at a slower speed, but it tends to wear the wipe pad prematurely out. The new version wipes less times but at a faster speed.

Note that updating this setting may not change anything for you, since it's use depends on your slicer software configuration.""")


tt_purge_line = N_(
	"""Purge Line
This macro controls how the purge line is drawn and "Artillery" published two different versions of it.

The legacy version draws multiple lines in a stack. Because this pattern causes more adhesion a newer version was developed that is very easy to be removed.

Note that updating this setting may not change anything for you, since it's use depends on your slicer software configuration.""")


tt_enable_m600 = N_(
	"""Enable M600
This option adds the new published macros to support the M600 filament change feature.

The following changes will be done:
	- Configuration support for beeper
	- M300 g-code macro (Play Tone)
	- M600 g-code macro (Filament Change)
	- T600 g-code macro (Artillery custom: Resume Print)

Note that if these settings are already installed this tool will not modify, neither remove them.""")


tt_pause = N_(
	"""Pause Macro
The pause macro controls the behavior of your printer, if for any reason, the printer has to pause the print job.

The following options are offered:
	- Do Not Change: will not modify it
	- Legacy: Use legacy "Artillery" code
	- New: Use newer "Artillery" code
	- Grumat: My custom version.

The new version of "Artillery" adds support for control parameters used by the M600 (filament change) command.

My custom version is based on the new "Artillery" macro and evaluates the filament sensor. In the case the filament runs out, it homes the print head and moves the printed object away.
This avoids purging filament right over your printed object.""")
