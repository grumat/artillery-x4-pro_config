��    f      L  �   |      �  $   �     �     �     �     	     	     	     	     	     -	     1	     5	     L	      P	  �  q	     :     W  )   s     �  �   �     &  	  =  2   G     z     �  �  �  &   l  "   �    �     �     �  z  �     ^     w     �     �     �     �     �          !     ?     E     N  �  c     =      U     v     �     �     �     �     �     �  O  �     4    M  �  g     ,     K     j  :  �  �  �     {!     �!  6  �!     �"  E  �"     B%     V%     d%     p%  p  |%     �&     �&     �&  "  '  �   &)  	    *     
*  
   *  I  "*     l+     ~+  �   �+     L,     a,     z,     �,     �,     �,     �,     -     !-  $   9-  �   ^-     ^.  �   k.     �.     /     /  �  //  $   -1     R1     i1     {1     �1     �1     �1     �1     �1     �1     �1     �1     �1      �1  �  �1     �3     �3  )   �3     )4  �   04     �4  	  �4  2   �5     6     6  �  16  &   �7  "   8    B8     S:     a:  z  o:     �;     <     <     ><     V<     i<     �<     �<     �<     �<     �<     �<  �  �<     �>      �>     ?     ?     .?     5?     <?     M?     \?  O  p?     �B    �B  �  �C     �F     �F     �F  :  G  �  LH     J     J  6  3J     jK  E  �K     �M     �M     �M     �M  p  N     yO     �O     �O  "  �O  �   �Q  	   �R     �R  
   �R  I  �R     �S     
T  �   T     �T     �T     U     !U     AU     YU     rU     �U     �U  $   �U  �   �U     �V  �   �V     {W     �W     �W     3   N   2              %           ,      0         1   
          (               L      #       F       f   >   I                   S       "   Q   `   )      '   G       ?   +   5   O   .   V      \       e   C   M          c   *      X      U   H   $   !   ]   	      K   ;   a   b   W   Z   P   @       6   D       E   /      &      T   R                         4   7   A       Y   =              <       :                   -   [   8   _   B   J         ^                        9       d                      	Available Disk Space After Cleanup: 	Available Disk Space: 	Total Disk Size: 1000mA (SW X4-Pro) 180° Mount 70% 75% 80% 800mA (SW X4-Plus) 85% 90% 900mA (recommendation) 95% Activate Manual Leveling Feature Activate Manual Leveling Feature
Klipper offers you a tool that helps adjusting the screws of your print bed. This option install the necessary configuration.

When activating this option the 'fluidd' interface will show an new "BED_SCREWS_ADJUST" button to perform the calibration. Please check guides on the web on how to use this command.

If you uncheck this option and your configuration already contains screws information, it will be left untouched. Artillery SideWinder X4 Plus Artillery SideWinder X4 Pro Artillery SideWinder X4 Unbrick Tool v0.2 Cancel Cannot find the serial port!
Please make sure that the cable is connected to the USB-C port of the printer and the printer is on. Check Model Attributes Check Model Attributes
This option checks the various model specific configurations for the selected printer model, and fixes elements that doesn't match the factory settings.

This may affect the following settings: stepper motors, printer homing, bed mesh, macros Check if Artillery Sidewinder X4 Printer Connected Complete Factory Reset Configuration Reset Configuration Reset
This option controls if your printer configuration file will be initialized to factory default.
Usually, there is no need to reset your configuration completely (leave default).

If the tool notices that your Klipper configuration is broken it will stop and suggests the reset option.
Then you have two options, with or without Klipper calibration data. If your printer behavior is absolutely weird, you should also reset calibration. Connection is not an artillery printer Detecting Serial Port of OS system Distance Sensor Offset
The offset value of the probe is slightly inconsistent on the factory settings. You can use this option to correct the offset values for the probe.

Note that Artillery mount this component on the opposite orientation of the data-sheet indication. One recommended mod is to reorient this sensor and follow the data-sheet.
If your printer has this mod, then you have to select the "180° Mount" option.

My repository contains series of tests, procedures on how to do this and also links to the data-sheet. Do not Change Do not change Enable M600
This option adds the new published macros to support the M600 filament change feature.

The following changes will be done:
	- Configuration support for beeper
	- M300 g-code (Play Tone)
	- M600 g-code (Filament Change)
	- T600 g-code (Artillery custom: Resume Print)
	
Note that if these settings are already installed the tool will not modify, neither remove them. Enabling Klipper Service Enabling Moonraker Service Enabling User Interface Service Enabling WebCam Service Erase .gcode files Erase Artillery clutter files Erase log files Erase miniature files Erase old configuration files Error Extruder Extruder Run Current Extruder Run Current
Comparing configurations of the X4-Plus and X4-Pro has an inconsistency on the extruder current, even using the same parts.
The following settings happens to exist:
	 - 800mA: SW X4-Plus
	 - 900mA: average recommendation
	 - 1000mA: SW X4=Pro

Please note that increasing the current will make your extruder stepper warmer and may cause filament softening and potential clogs. On the other side, max filament flow could benefit of it, for faster print. Factory Mount (default) Factory Reset (keep calibration) Fix file permission Fix for card resize bug G-Code Gantry General Settings Grumat Version Heatbreak Fan Speed Heatbreak Fan Speed
This option allows you to reduce the speed of the heatbreak fan. This should reduce the noise levels.

You should consider the following: the main function of this fan is to protect the filament smoothing near the entry of the hot-end, which would easily deform when the extruder pushes. As a consequence you increase the chance of causing clogs if you reduce the cooling fan.

But notice that this was designed for very high temperatures. If your max temperature never goes above 250°C you can reduce this value. This is my case and I use 90%, which already does a good job in noise levels.

Speculative Note: Artillery launched recently a new hot-end, which seems to have less heatsink mass, probably because less weight reduces vibration. On the other side, this could indicate that the old hot-end heatsink is an overkill. Higher Stepper Z Current Higher Stepper Z Current
Usually the X4-Plus model runs with 800mA stepper current for the gantry and the X4-Pro model with 900mA, which seems inconsistent, since the Plus model has more weight.

This could fix issues with Z-Axis movement, but the steppers will consume more power. Improve Mainboard Fan
On the original configuration main-board fan is only activated by the print nozzle. This configuration is OK if you are doing only printing.

But it's main function is to cool stepper motor drivers. This means that, if you activate steppers but keep the nozzle off, then perform lots of motion operations, you will overheat your stepper drivers and get errors.

By applying this option, your main-board fan will turn on as soon as any of the following elements are active: heat bed, print nozzle or any of your stepper drivers. So, I strongly recommend you set this option.

In the case you already have this modification the routine will not modify it, regardless if its 'on' or 'off'. Improved Mainboard Fan control Improved Z-Offset Error Margin Improved Z-Offset Sampling Improved Z-Offset sampling
Regardless of the orientation of your distance sensor, you can improve the Z-offset sampling by using lower approximation speeds and more samples.

By using a more accurate sampling method, the overall Z-offset errors are reduced and first layer of your prints should be more consistent. Improved Z-Offset validation
Besides improving sampling conditions you can reduce the acceptance margin of the sampled data.
This means that after performing the samples all values have to fit a lower error margin to be accepted.

Note that error margins are on the limit. If you activate this option with an unmodified printer it may happen that you printer stops with errors during Z-offset calibration and also during bed-mesh calibration. Legacy Version Limits Extruder Acceleration Limits Extruder Acceleration
Some printers have a higher extruder acceleration, that has been reduced in recent configurations, probably to avoid higher temperatures on the extruder.
This setting can help reduce extruder temperature and avoid a potential softening of your filament, and clogs as a consequence. M600: Filament Change Support Main-board Fan Speed
This option allows you to reduce the speed of the main-board fan. The main goal is to lower noise levels.

You should note that the main function of this fan is to cool down the stepper motor drivers, which may get hot depending on the intensity of acceleration and speed values. If cooling is insufficient a thermal protection of the stepper driver may occur and the motion for the affected axis stops.

In my repository I suggest the mount of a 'fan duct' that concentrates more air flow to the steppers drivers and allows you to safely reduce the fan speed. Mainboard Fan Speed Max (default) New Version Nozzle Wipe Nozzle Wipe
This macro controls how the nozzle will be cleaned and "Artillery" published two different versions of it.
The use of this g-code macro depends on your slicer software configuration.

The legacy version wipes the nozzle many times at a slower speed, but it tends to wear the wipe pad prematurely out. The new version wipes less times but at a faster speed. Offset Ok Pause Macro Pause Macro
The pause macro controls the behavior your printer when you press the pause button on the control panel.

The following options are offered:
	- Do Not Change: will not modify it
	- Legacy: Use legacy Artillery code
	- New: Use newer Artillery code
	- Grumat: My custom version.

The new version of Artillery adds support for control parameters used by the M600 command.
My custom version evaluates the filament sensor and docks the print head when filament runs out, which helps not to generate plastic purge over your printed object. Please select the correct printer.
This parameter is very critical because hardware properties of both models are very different and incompatible.

Please if you fail to set the correct option, bad things will happen! Print Bed Printer Fans Purge Line Purge Line
This macro controls how the purge line is drawn and Artillery published two different versions of it.
The use of this g-code macro depends on your slicer software configuration.

The legacy version draws lines in layers and because it causes more adhesion a newer version was developed that is very easy to be removed. Rebooting Printer Rename Fans Rename Fans
This option renames printer fans to nice names. This is used on the 'fluidd' interface.

The 'Fan 0' is renamed to 'Heatbreak Cooling Fan';
The 'Fan 2' is renamed to 'Mainboard Fan' Select Printer Model Starting Klipper Service Starting Moonraker Service Starting User Interface Service Starting WebCam Service Stopping Klipper Service Stopping Moonraker Service Stopping User Interface Service Stopping WebCam Service Temperature Reading for Host and MCU Temperature Reading for Host and MCU
If you se the 'fluidd' interface you will like this option. It activates the temperature sensors for the Host and the motion MCU.

Note that this option does not modify your settings if this sensors are already active. Temperatures There are too many compatible serial port!
Disconnect all serial port cables except for the printer that you want to apply the fix. Trimming eMMC disk Update only (default) Z-Axis Distance Sensor Project-Id-Version: unbrick-swx4
PO-Revision-Date: 2025-07-22 19:13+0200
Last-Translator: 
Language-Team: 
Language: en_US
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
X-Generator: Poedit 2.4.2
X-Poedit-Basepath: ../../..
Plural-Forms: nplurals=2; plural=(n != 1);
X-Poedit-KeywordsList: _;N_
X-Poedit-SourceCharset: UTF-8
X-Poedit-SearchPath-0: .
X-Poedit-SearchPathExcluded-0: assets
X-Poedit-SearchPathExcluded-1: mk-assets
X-Poedit-SearchPathExcluded-2: tests
 	Available Disk Space After Cleanup: 	Available Disk Space: 	Total Disk Size: 1000mA (SW X4-Pro) 180° Mount 70% 75% 80% 800mA (SW X4-Plus) 85% 90% 900mA (recommendation) 95% Activate Manual Leveling Feature Activate Manual Leveling Feature
Klipper offers you a tool that helps adjusting the screws of your print bed. This option install the necessary configuration.

When activating this option the 'fluidd' interface will show an new "BED_SCREWS_ADJUST" button to perform the calibration. Please check guides on the web on how to use this command.

If you uncheck this option and your configuration already contains screws information, it will be left untouched. Artillery SideWinder X4 Plus Artillery SideWinder X4 Pro Artillery SideWinder X4 Unbrick Tool v0.2 Cancel Cannot find the serial port!
Please make sure that the cable is connected to the USB-C port of the printer and the printer is on. Check Model Attributes Check Model Attributes
This option checks the various model specific configurations for the selected printer model, and fixes elements that doesn't match the factory settings.

This may affect the following settings: stepper motors, printer homing, bed mesh, macros Check if Artillery Sidewinder X4 Printer Connected Complete Factory Reset Configuration Reset Configuration Reset
This option controls if your printer configuration file will be initialized to factory default.
Usually, there is no need to reset your configuration completely (leave default).

If the tool notices that your Klipper configuration is broken it will stop and suggests the reset option.
Then you have two options, with or without Klipper calibration data. If your printer behavior is absolutely weird, you should also reset calibration. Connection is not an artillery printer Detecting Serial Port of OS system Distance Sensor Offset
The offset value of the probe is slightly inconsistent on the factory settings. You can use this option to correct the offset values for the probe.

Note that Artillery mount this component on the opposite orientation of the data-sheet indication. One recommended mod is to reorient this sensor and follow the data-sheet.
If your printer has this mod, then you have to select the "180° Mount" option.

My repository contains series of tests, procedures on how to do this and also links to the data-sheet. Do not Change Do not change Enable M600
This option adds the new published macros to support the M600 filament change feature.

The following changes will be done:
	- Configuration support for beeper
	- M300 g-code (Play Tone)
	- M600 g-code (Filament Change)
	- T600 g-code (Artillery custom: Resume Print)
	
Note that if these settings are already installed the tool will not modify, neither remove them. Enabling Klipper Service Enabling Moonraker Service Enabling User Interface Service Enabling WebCam Service Erase .gcode files Erase Artillery clutter files Erase log files Erase miniature files Erase old configuration files Error Extruder Extruder Run Current Extruder Run Current
Comparing configurations of the X4-Plus and X4-Pro has an inconsistency on the extruder current, even using the same parts.
The following settings happens to exist:
	 - 800mA: SW X4-Plus
	 - 900mA: average recommendation
	 - 1000mA: SW X4=Pro

Please note that increasing the current will make your extruder stepper warmer and may cause filament softening and potential clogs. On the other side, max filament flow could benefit of it, for faster print. Factory Mount (default) Factory Reset (keep calibration) Fix file permission Fix for card resize bug G-Code Gantry General Settings Grumat Version Heatbreak Fan Speed Heatbreak Fan Speed
This option allows you to reduce the speed of the heatbreak fan. This should reduce the noise levels.

You should consider the following: the main function of this fan is to protect the filament smoothing near the entry of the hot-end, which would easily deform when the extruder pushes. As a consequence you increase the chance of causing clogs if you reduce the cooling fan.

But notice that this was designed for very high temperatures. If your max temperature never goes above 250°C you can reduce this value. This is my case and I use 90%, which already does a good job in noise levels.

Speculative Note: Artillery launched recently a new hot-end, which seems to have less heatsink mass, probably because less weight reduces vibration. On the other side, this could indicate that the old hot-end heatsink is an overkill. Higher Stepper Z Current Higher Stepper Z Current
Usually the X4-Plus model runs with 800mA stepper current for the gantry and the X4-Pro model with 900mA, which seems inconsistent, since the Plus model has more weight.

This could fix issues with Z-Axis movement, but the steppers will consume more power. Improve Mainboard Fan
On the original configuration main-board fan is only activated by the print nozzle. This configuration is OK if you are doing only printing.

But it's main function is to cool stepper motor drivers. This means that, if you activate steppers but keep the nozzle off, then perform lots of motion operations, you will overheat your stepper drivers and get errors.

By applying this option, your main-board fan will turn on as soon as any of the following elements are active: heat bed, print nozzle or any of your stepper drivers. So, I strongly recommend you set this option.

In the case you already have this modification the routine will not modify it, regardless if its 'on' or 'off'. Improved Mainboard Fan control Improved Z-Offset Error Margin Improved Z-Offset Sampling Improved Z-Offset sampling
Regardless of the orientation of your distance sensor, you can improve the Z-offset sampling by using lower approximation speeds and more samples.

By using a more accurate sampling method, the overall Z-offset errors are reduced and first layer of your prints should be more consistent. Improved Z-Offset validation
Besides improving sampling conditions you can reduce the acceptance margin of the sampled data.
This means that after performing the samples all values have to fit a lower error margin to be accepted.

Note that error margins are on the limit. If you activate this option with an unmodified printer it may happen that you printer stops with errors during Z-offset calibration and also during bed-mesh calibration. Legacy Version Limits Extruder Acceleration Limits Extruder Acceleration
Some printers have a higher extruder acceleration, that has been reduced in recent configurations, probably to avoid higher temperatures on the extruder.
This setting can help reduce extruder temperature and avoid a potential softening of your filament, and clogs as a consequence. M600: Filament Change Support Main-board Fan Speed
This option allows you to reduce the speed of the main-board fan. The main goal is to lower noise levels.

You should note that the main function of this fan is to cool down the stepper motor drivers, which may get hot depending on the intensity of acceleration and speed values. If cooling is insufficient a thermal protection of the stepper driver may occur and the motion for the affected axis stops.

In my repository I suggest the mount of a 'fan duct' that concentrates more air flow to the steppers drivers and allows you to safely reduce the fan speed. Mainboard Fan Speed Max (default) New Version Nozzle Wipe Nozzle Wipe
This macro controls how the nozzle will be cleaned and "Artillery" published two different versions of it.
The use of this g-code macro depends on your slicer software configuration.

The legacy version wipes the nozzle many times at a slower speed, but it tends to wear the wipe pad prematurely out. The new version wipes less times but at a faster speed. Offset Ok Pause Macro Pause Macro
The pause macro controls the behavior your printer when you press the pause button on the control panel.

The following options are offered:
	- Do Not Change: will not modify it
	- Legacy: Use legacy Artillery code
	- New: Use newer Artillery code
	- Grumat: My custom version.

The new version of Artillery adds support for control parameters used by the M600 command.
My custom version evaluates the filament sensor and docks the print head when filament runs out, which helps not to generate plastic purge over your printed object. Please select the correct printer.
This parameter is very critical because hardware properties of both models are very different and incompatible.

Please if you fail to set the correct option, bad things will happen! Print Bed Printer Fans Purge Line Purge Line
This macro controls how the purge line is drawn and Artillery published two different versions of it.
The use of this g-code macro depends on your slicer software configuration.

The legacy version draws lines in layers and because it causes more adhesion a newer version was developed that is very easy to be removed. Rebooting Printer Rename Fans Rename Fans
This option renames printer fans to nice names. This is used on the 'fluidd' interface.

The 'Fan 0' is renamed to 'Heatbreak Cooling Fan';
The 'Fan 2' is renamed to 'Mainboard Fan' Select Printer Model Starting Klipper Service Starting Moonraker Service Starting User Interface Service Starting WebCam Service Stopping Klipper Service Stopping Moonraker Service Stopping User Interface Service Stopping WebCam Service Temperature Reading for Host and MCU Temperature Reading for Host and MCU
If you se the 'fluidd' interface you will like this option. It activates the temperature sensors for the Host and the motion MCU.

Note that this option does not modify your settings if this sensors are already active. Temperatures There are too many compatible serial port!
Disconnect all serial port cables except for the printer that you want to apply the fix. Trimming eMMC disk Update only (default) Z-Axis Distance Sensor 