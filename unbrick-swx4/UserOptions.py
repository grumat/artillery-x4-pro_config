#
# -*- coding: UTF-8 -*-

import os
import configparser

class UserOptions(object):
	def __init__(self) -> None:
		# printer
		self.ip_addr = "192.168.0.171"
		self.printer = 0
		# linux
		self.optimize_disk_space = True
		self.file_permissions = True
		self.resize_bug = True
		self.trim = True
		# klipper
		self.reset = 0
		self.model_attr = True
		# gantry
		self.stepper_z_current = 0
		# extruder
		self.extruder_accel = True
		self.extruder_current = 1
		# probe
		self.probe_offset = 1
		self.probe_sampling = True
		self.probe_validation = False
		# bed
		self.screws_tilt_adjust = True
		# fans
		self.fan_rename = True
		self.mb_fan_fix = True
		self.hb_fan_speed = 0
		self.mb_fan_speed = 0
		# temperature
		self.temp_mcu = True
		# gcode
		self.nozzle_wipe = 2
		self.purge_line = 2
		self.enable_m600 = True
		self.pause = 3

	def SaveIni(self, filename):
		config = configparser.ConfigParser()
		config['printer'] = {
			'ip_addr': str(self.ip_addr),
			'printer': str(self.printer),
		}
		config['linux'] = {
			'optimize_disk_space': str(self.optimize_disk_space),
			'file_permissions': str(self.file_permissions),
			'resize_bug': str(self.resize_bug),
			'trim': str(self.trim),
		}
		config['klipper'] = {
			'reset': str(self.reset),
			'model_attr': str(self.model_attr),
		}
		config['gantry'] = {
			'stepper_z_current': str(self.stepper_z_current),
		}
		config['extruder'] = {
			'extruder_accel': str(self.extruder_accel),
			'extruder_current': str(self.extruder_current),
		}
		config['probe'] = {
			'probe_offset': str(self.probe_offset),
			'probe_sampling': str(self.probe_sampling),
			'probe_validation': str(self.probe_validation),
		}
		config['bed'] = {
			'screws_tilt_adjust': str(self.screws_tilt_adjust),
		}
		config['fans'] = {
			'fan_rename': str(self.fan_rename),
			'mb_fan_fix': str(self.mb_fan_fix),
			'hb_fan_speed': str(self.hb_fan_speed),
			'mb_fan_speed': str(self.mb_fan_speed),
		}
		config['temperature'] = {
			'temp_mcu': str(self.temp_mcu),
		}
		config['gcode'] = {
			'nozzle_wipe': str(self.nozzle_wipe),
			'purge_line': str(self.purge_line),
			'enable_m600': str(self.enable_m600),
			'pause': str(self.pause),
		}
		with open(filename, 'w') as configfile:
			config.write(configfile)

	def LoadIni(self, filename):
		if not os.path.isfile(filename):
			return 
		config = configparser.ConfigParser()
		config.read(filename)
		# Helper function to update attribute if key exists
		def update_attr(grp, key, default, converter):
			if grp not in config:
				return  # Silently return if section is missing
			options = config[grp]
			if key in options:
				setattr(self, key, converter(options[key]))
			# else: keep default (constructor) value

		update_attr('printer', 'ip_addr', 				self.ip_addr, str)
		update_attr('printer', 'printer', 				self.printer, int)

		update_attr('linux', 'optimize_disk_space', 	self.optimize_disk_space, lambda x: x.lower() == 'true')
		update_attr('linux', 'file_permissions', 		self.file_permissions, lambda x: x.lower() == 'true')
		update_attr('linux', 'resize_bug', 				self.resize_bug, lambda x: x.lower() == 'true')
		update_attr('linux', 'trim', 					self.trim, lambda x: x.lower() == 'true')

		update_attr('klipper', 'reset', 				self.reset, int)
		update_attr('klipper', 'model_attr', 			self.model_attr, lambda x: x.lower() == 'true')

		update_attr('gantry', 'stepper_z_current', 		self.stepper_z_current, int)

		update_attr('extruder', 'extruder_accel', 		self.extruder_accel, lambda x: x.lower() == 'true')
		update_attr('extruder', 'extruder_current', 	self.extruder_current, int)

		update_attr('probe', 'probe_offset', 		self.probe_offset, int)
		update_attr('probe', 'probe_sampling', 		self.probe_sampling, lambda x: x.lower() == 'true')
		update_attr('probe', 'probe_validation', 	self.probe_validation, lambda x: x.lower() == 'true')

		update_attr('bed', 'screws_tilt_adjust', 	self.screws_tilt_adjust, lambda x: x.lower() == 'true')

		update_attr('fans', 'fan_rename', 			self.fan_rename, lambda x: x.lower() == 'true')
		update_attr('fans', 'mb_fan_fix', 			self.mb_fan_fix, lambda x: x.lower() == 'true')
		update_attr('fans', 'hb_fan_speed', 		self.hb_fan_speed, int)
		update_attr('fans', 'mb_fan_speed', 		self.mb_fan_speed, int)

		update_attr('temperature', 'temp_mcu', 		self.temp_mcu, lambda x: x.lower() == 'true')

		update_attr('gcode', 'nozzle_wipe', 		self.nozzle_wipe, int)
		update_attr('gcode', 'purge_line', 			self.purge_line, int)
		update_attr('gcode', 'enable_m600', 		self.enable_m600, lambda x: x.lower() == 'true')
		update_attr('gcode', 'pause', 				self.pause, int)
