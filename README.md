# **My Own Custom Settings for Artillery Sidewinder X4 Pro**

This repository stores my tinkering findings on the Artillery Sidewinder X4 Pro, a 3D printer I own.

While Artillery produces very robust 3D printers, software support is very limited and good quality results requires a lot of experiencing. I replaced an "Ender" printer by this one, since the delivered mechanical parts are far superior for the same price tag when comparing to my initial printer.

The first impact I noticed, while the Ender "just" started to print without any initial tuning, the Artillery requires you a complete *Z-Offset ritual* before trying some prints.

Although not so complicated, manual adjustments require you to gain *mechanical feeling*, which comes with quite some try, fail and retry cycles.


# My Setup

The information provided here is based on the following versions:
- OrcaSlicer 2.3.0
- Artillery SW4-Pro firmware 1.5.3


## Orca Slicer

I switched all my experience to OrcaSlicer and I am not willing to try anything developed by hardware manufacturers. This is the same if you buy a Toyota with a Toyota navigation system. Although you can use it for street guidance it is never comparable to Google Maps, Microsoft Here We Go or Waze. And it just never will be. Up to the point that I gave up buying a Toyota in 2019 because the Media system did not support iPhone or Android integration.

> In contrast, the same POV happens with 3D printers, when one choose to pay premium price for a Bambu Lab.  
In my case, my tinkering nature, which does not apply to cars, drove me to choose a a good quality construct for a fair price.


## Artillery SW4-Pro firmware 1.5.3

There are lots of reports on the Internet regarding failures happening with these machines when using older firmware versions. Specially the hot end crashing into the build platform. From day 1, I upgrade my firmware to avoid any inconvenience and I recommend to the exactly the same, if you own this printer.


# Issues and Fixes

This section collects my improvements to the original printer configuration.


## Nozzle Wipe and Purge Line Fix

To fix the problem described above, you should edit the Artillery Machine Profile, on the **Machine G-Code** tab - **Machine start G-Code** and replace the third line `S{temperature_vitrification[0]}` by `S{nozzle_temperature_range_low[0]}`

Here is the complete contents (**for X4-Pro only!!!**):

```
M104 S140
M190 S[first_layer_bed_temperature]
M109 S{nozzle_temperature_range_low[0]}
G28;
G1 X180 Y247 Z10 F5000
SET_KINEMATIC_POSITION Y=0
G1 Y11 F4000
G1 X180 F4000
G1 Z-1 F600 
G1 X230 F4000
G1 Y15 F4000
G1 X180 F4000
G92 E0
G1 Z10 F1200
G1 Y0 F5000
G1 E-1 F3000
M400
SET_KINEMATIC_POSITION Y=247
G92 E-1
M140 S[first_layer_bed_temperature];
M104 S[first_layer_temperature];
G1 X0 Y0.8 Z0.8 F18000
G92 E0
G1 X0 Y0.8 Z0.3 E8 F600
G92 E0
G1 X170 Y0.8 Z0.3 F1800.0 E17.0;draw line
G92 E0
G1 X170 Y0 Z0.3 F1800.0 E0.08;draw line
G92 E0
G1 X70 Y0 Z0.3 F1800.0 E10.0;draw line
G92 E0
G1 X70 Y1.6 Z0.3 F1800.0 E0.16;draw line
G92 E0
G1 X150 Y1.6 Z0.3 F1800.0 E8;draw line
G92 E0
G1 X150 Y0 Z0.3 F1800.0 E0.16;draw line
G92 E0
G1 E-1 Z5 F18000
G92 E0
```

> I reviewed the `X4 Plus` configuration and the problem also exists there. In this case you should modify the 3rd line only. The complete contents listed here refer to the 240x240 bed size and will fail on a model with a bigger heat bed.


### Background

This is the original script provided by Orca Slicer:

```
M104 S140
M190 S[first_layer_bed_temperature]
M109 S{temperature_vitrification[0]}
G28;
G1 X180 Y247 Z10 F5000
SET_KINEMATIC_POSITION Y=0
G1 Y11 F4000
G1 X180 F4000
G1 Z-1 F600 
G1 X230 F4000
G1 Y15 F4000
G1 X180 F4000
G92 E0
G1 Z10 F1200
G1 Y0 F5000
G1 E-1 F3000
M400
SET_KINEMATIC_POSITION Y=247
G92 E-1
M140 S[first_layer_bed_temperature];
M104 S[first_layer_temperature];
G1 X0 Y0.8 Z0.8 F18000
G92 E0
G1 X0 Y0.8 Z0.3 E8 F600
G92 E0
G1 X170 Y0.8 Z0.3 F1800.0 E17.0;draw line
G92 E0
G1 X170 Y0 Z0.3 F1800.0 E0.08;draw line
G92 E0
G1 X70 Y0 Z0.3 F1800.0 E10.0;draw line
G92 E0
G1 X70 Y1.6 Z0.3 F1800.0 E0.16;draw line
G92 E0
G1 X150 Y1.6 Z0.3 F1800.0 E8;draw line
G92 E0
G1 X150 Y0 Z0.3 F1800.0 E0.16;draw line
G92 E0
G1 E-1 Z5 F18000
G92 E0
```

I reformatted and commented it below:

```sh
# Sets extruder temperature target to 140, but does not wait
M104 S140
# Sets the the Heat Bed Temperature to the "Bed Temperature - First Layer" value 
# provided in the filament settings dialog
M190 S[first_layer_bed_temperature]
# Sets the extruder to the "Softening Temperature" provided in the filament settings 
# dialog and wait
M109 S{temperature_vitrification[0]}
# Moves kinematics to the origin position (moves to the center of the head bed and 
# performs the Z distance calibration)
G28
# Moves to the back of the bed level, where the nozzle cleaner is mounted
G1 X180 Y247 Z10 F5000
# Set current position as the origin for axis Z (this is because the commands coming 
# below are relative moves)
SET_KINEMATIC_POSITION Y=0
# Moves heat bed
G1 Y11 F4000
# Repeats X coordinate, which makes sure the X motion has happened (a motion on an 
# axis can start when the previous has completed)
G1 X180 F4000
# Gantry down
G1 Z-1 F600 
# Wipe to the right
G1 X230 F4000
# Move table again to use other portion of the wipe area
G1 Y15 F4000
# Wipe to the left
G1 X180 F4000
# Dummy extruder
G92 E0
# Gantry up
G1 Z10 F1200
# Move table back before starting to wipe
G1 Y0 F5000
# Retract
G1 E-1 F3000
# Wait for current moves to finish
M400
# Removes the Y offset established before
SET_KINEMATIC_POSITION Y=247
# Retract
G92 E-1
# Sets the Bed temperature (redundant?)
M140 S[first_layer_bed_temperature];
# Sets extruder to the temperature found in "Nozzle - First Layer" value provided 
# in the filament settings dialog
M104 S[first_layer_temperature];
# Move to test area on the left/bottom of the PEI sheet
# The following line moves will do the following pattern:
#                        />>>>>>>>>>>>>>>>>>>>>>>>>>>\              [third line]
# >>>>>>>>>>>>>>>>>>>>>>>:>>>>>>>>>>>>>>>>>>>>>>>>>>>:>>>>>\        [first line]
#                        \<<<<<<<<<<<<<<<<<<<<<<<<<<<:<<<<</        [second line]
#                                               [fourth line]
G1 X0 Y0.8 Z0.8 F18000
# Stop Extruder
G92 E0
# Wipe to the right, while extruding material and moving slightly down
G1 X0 Y0.8 Z0.3 E8 F600
# Wait for extruder motion to complete
G92 E0
# Wipe to the right, while extruding material
G1 X170 Y0.8 Z0.3 F1800.0 E17.0;draw line
# Wait for extruder motion to complete
G92 E0
# Move bed so that new line does not overlaps
G1 X170 Y0 Z0.3 F1800.0 E0.08;draw line
# Wait for motion to complete
G92 E0
# Move to the left, a shorter line
G1 X70 Y0 Z0.3 F1800.0 E10.0;draw line
# Wait for motion to complete
G92 E0
# Move bed, now to the other side of the initial line
G1 X70 Y1.6 Z0.3 F1800.0 E0.16;draw line
# Wait for motion to complete
G92 E0
# Move to the left, still short line
G1 X150 Y1.6 Z0.3 F1800.0 E8;draw line
# Wait for motion to complete
G92 E0
# Trace a short line to Y origin
G1 X150 Y0 Z0.3 F1800.0 E0.16;draw line
# Wait for motion to complete
G92 E0
# Retract and gantry up
G1 E-1 Z5 F18000
# Wait for motion to complete
G92 E0
```

There are of couple of comments and issues in respect of this script:
- First two commands are OK, which puts the nozzle still on a low temperature, but high enough to start the heating and wait for the lengthy bed temperature.
- The third command `M109` is completely wrong:
  - IMHO, this parameter is completely wrong.
  - According to Orca Slicer source code, the associated tooltip is:
    > The material softens at this temperature, so when the bed temperature is equal to or greater than it, it's highly recommended to open the front door and/or remove the upper glass to avoid clogging.
  - So, this is also known as *vitrification temperature* of the plastic. When choosing the softening temperature for the extruder, the plastic is still in a *quasi-solid state*, which is not adequate for the nozzle cleanup that comes next.
  - When looking for the temperature graph you will notice that the nozzle cools down, since the `G28` takes time enough to cause it.
- Right after `G28`, there comes the nozzle wipe, but with too lower temperature, meaning, this has barely an effect
- After wiping the nozzle it sets the correct temperature and starts to draw a purge line, which cannot work, because nozzle is not hot enough. I fear that this also forces filament, which will get *milled* by the extruder and possibly cause initial flow variations.


## Improved Beb Mesh Calibration

In the current firmware, calibration settings is adjusted to a 36 point matrix. This is what you get when using the control panel on the printer.

Some of the marketing sheets talk about 9x9 mesh and probably an overkill for this bed size. But if you want to use a finer grained bed mesh you can change a simple line to activate the feature.

### Procedure

To Change this option do the following:
- Open the *fluidd* web interface 
- Select the edit file configuration
- Select and edit the `printer.cfg` file
- Search the `[bed_mesh]` section
- A couple of lines below, the modify the value of the `probe_count` key to 9,9
- Reboot Klipper

The file should look like this:
```ini
[bed_mesh]
speed:120
horizontal_move_z:10
mesh_min:20,20
mesh_max:220,220
probe_count:9,9
algorithm:bicubic
bicubic_tension:0.2
mesh_pps: 2, 2
```

## X Homing For pause

When filament runs out, printer runs the `PAUSE` macro. The problem is that it just raises the gantry a bit (Z-axis). Ideally, it should move the X axis to the purge area, since we don't want to load filament and throw purged plastic over the printed object.

To accomplish this, modify the `[gcode_macro PAUSE]` section of your `printer.cfg` file and add the line `G1 X-5 F6000` after the line `G90`.

It should look like this:

```ini
[gcode_macro PAUSE]
rename_existing: BASE_PAUSE
gcode: 
    {% set z = params.Z|default(20)|int %}                                                   
    {% set e = params.E|default(2.5) %} 
    SET_GCODE_VARIABLE MACRO=RESUME VARIABLE=zhop VALUE={z}                             
    SET_GCODE_VARIABLE MACRO=RESUME VARIABLE=etemp VALUE={printer['extruder'].target}                                              
    SAVE_GCODE_STATE NAME=PAUSE                                                                  
    M25                                                                              
    {% if (printer.gcode_move.position.z + z) < printer.toolhead.axis_maximum.z %}       
      G91
	    M83
	    G1 E-{e} F2100
      G1 Z{z} F900                                                                     
    {% else %}
      SET_GCODE_VARIABLE MACRO=RESUME VARIABLE=zhop VALUE=0
    {% endif %}
    SAVE_GCODE_STATE NAME=PAUSEPARK
    G90
    G1 X-5 F6000
    #G1 X0 Y0 F6000
	  #G1 E{e} F2100	
    SET_IDLE_TIMEOUT TIMEOUT=43200                                                       
```

# Filament Tips

These are key filament settings for my printer.


## SunLu PLA Meta Blue

| Parameter            | Value     |
|----------------------|-----------|
| Flow Ratio           | 0.98      |
| Pressure Advance     | 0.044     |
| Nozzle Temps         | 220 / 215 |
| Bed Temps            | 55 / 50   |
| Max Volumetric Speed | 26        |


## SunLu PLA Meta Magenta

| Parameter            | Value     |
|----------------------|-----------|
| Flow Ratio           | 0.98      |
| Pressure Advance     | 0.054     |
| Nozzle Temps         | 220 / 215 |
| Bed Temps            | 55 / 50   |
| Max Volumetric Speed | 21        |


## SunLu PETG Grey

| Parameter            | Value     |
|----------------------|-----------|
| Flow Ratio           | 0.95      |
| Pressure Advance     | 0.055     |
| Nozzle Temps         | 250 / 245 |
| Bed Temps            | 70 / 70   |
| Max Volumetric Speed | 21        |


## SunLu PETG Black

| Parameter            | Value     |
|----------------------|-----------|
| Flow Ratio           | 0.95      |
| Pressure Advance     | 0.055     |
| Nozzle Temps         | 250 / 245 |
| Bed Temps            | 70 / 70   |
| Max Volumetric Speed | 21        |


