#
# -*- coding: UTF-8 -*-
#
# Spellchecker: words USWX GRUMAT

import os
import sys
from typing import TYPE_CHECKING

# Enable test environment
os.environ["USWX4_TEST"] = "test_task_config"


# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the 'assets' directory
project_dir = os.path.normpath(os.path.join(current_dir, '..'))

# Add the 'project_dir' directory to sys.path
sys.path.append(project_dir)

if TYPE_CHECKING:
	from ..my_env import Error, Info, Warn
	from ..user_options import UserOptions
	from ..my_workflow import Workflow
	from .test_utils import *
else:
	from my_env import Error, Info, Warn
	from user_options import UserOptions
	from my_workflow import Workflow
	from test_utils import *

SWX4PRO = 0
SWX4PLUS = 1

START_WITH_PRO_DEF = 0
START_WITH_PRO_UPG = 1 << 16
START_WITH_PRO_GRUMAT = 2 << 16
START_WITH_PLUS_DEF = 3 << 16
START_WITH_PLUS_UPG = 4 << 16
START_WITH_PLUS_GRUMAT = 5 << 16


def step_001(opts : UserOptions):
	opts.printer = SWX4PLUS + START_WITH_PRO_UPG	# Artillery plus target with Artillery pro config
	opts.model_attr = True
	wf = Workflow(opts)
	wf.Test('step_001')

def step_002(opts : UserOptions):
	opts.printer = SWX4PRO + START_WITH_PLUS_UPG	# Artillery pro target with Artillery plus config
	opts.model_attr = True
	opts.exclude_object = True
	opts.mb_fan_speed = 1
	opts.hb_fan_speed = 1
	opts.nozzle_wipe = 0
	opts.purge_line = 0
	wf = Workflow(opts)
	wf.Test('step_002')

def step_003(opts : UserOptions):
	opts.printer = SWX4PRO + START_WITH_PRO_UPG
	opts.model_attr = False
	opts.exclude_object = False
	opts.stepper_z_current = 1
	opts.extruder_accel = 1
	opts.extruder_current = 1
	opts.probe_offset = 1
	opts.probe_sampling = 2
	opts.probe_validation = 1
	opts.screws_tilt_adjust = 1
	opts.fan_rename = True
	opts.mb_fan_fix = True
	opts.mb_fan_speed = 2
	opts.hb_fan_speed = 2
	opts.nozzle_wipe = 0
	opts.purge_line = 0
	opts.pause = 1
	wf = Workflow(opts)
	wf.Test('step_003')

def step_004(opts : UserOptions):
	opts.printer = SWX4PRO + START_WITH_PRO_UPG
	opts.model_attr = False
	opts.exclude_object = False
	opts.stepper_z_current = 2
	opts.extruder_accel = 2
	opts.extruder_current = 2
	opts.probe_offset = 2
	opts.probe_sampling = 1
	opts.probe_validation = 2
	opts.screws_tilt_adjust = 2
	opts.fan_rename = False
	opts.mb_fan_fix = False
	opts.mb_fan_speed = 3
	opts.hb_fan_speed = 3
	opts.nozzle_wipe = 1
	opts.purge_line = 1
	opts.enable_m600 = 2
	opts.pause = 3
	wf = Workflow(opts)
	wf.Test('step_004')

def step_005(opts : UserOptions):
	opts.printer = SWX4PRO + START_WITH_PRO_GRUMAT
	opts.model_attr = True
	opts.exclude_object = False
	opts.stepper_z_current = 0
	opts.extruder_accel = 3
	opts.extruder_current = 3
	opts.probe_offset = 0
	opts.probe_sampling = 0
	opts.probe_validation = 0
	opts.screws_tilt_adjust = 1
	opts.fan_rename = False
	opts.mb_fan_fix = False
	opts.mb_fan_speed = 5
	opts.hb_fan_speed = 5
	opts.temp_mcu = True
	opts.nozzle_wipe = 2
	opts.purge_line = 2
	opts.enable_m600 = 1
	opts.pause = 2
	wf = Workflow(opts)
	wf.Test('step_005')

def step_006(opts : UserOptions):
	opts.printer = SWX4PLUS + START_WITH_PLUS_DEF
	opts.model_attr = True
	opts.exclude_object = True
	opts.stepper_z_current = 1
	opts.extruder_accel = 1
	opts.extruder_current = 2
	opts.probe_offset = 2
	opts.probe_sampling = 2
	opts.probe_validation = 2
	opts.screws_tilt_adjust = 2
	opts.fan_rename = True
	opts.mb_fan_fix = True
	opts.mb_fan_speed = 6
	opts.hb_fan_speed = 4
	opts.temp_mcu = True
	opts.nozzle_wipe = 2
	opts.purge_line = 3
	opts.enable_m600 = 2
	opts.pause = 3
	wf = Workflow(opts)
	wf.Test('step_006')

def main():
	opts = UserOptions()
	opts.reset = 0
	opts.model_attr = True
	opts.exclude_object = False
	opts.stepper_z_current = 0
	opts.extruder_accel = 0
	opts.extruder_current = 0
	opts.probe_offset = 0
	opts.probe_sampling = 0
	opts.probe_validation = 0
	opts.screws_tilt_adjust = 0
	opts.fan_rename = False
	opts.mb_fan_fix = False
	opts.mb_fan_speed = 0
	opts.hb_fan_speed = 0
	opts.temp_mcu = False
	opts.nozzle_wipe = 0
	opts.purge_line = 0
	opts.enable_m600 = 0
	opts.pause = 0
	test = 0
	success = 0
	left = os.path.join(current_dir, 'backup', 'printer.cfg')
	while True:
		test += 1
		method = f'step_{test:03d}'
		if hasattr(sys.modules[__name__], method):
			msg = f"Starting Test {test}"
			print(BOLD + msg + NORMAL)
			Info(msg)
			getattr(sys.modules[__name__], method)(opts)
			right = os.path.join(current_dir, 'results', f'printer-{test:03d}.cfg')
			res = files_equal(left, right)
			success += res
			if res:
				msg = f"Test {test} PASSED"
				print(GREEN + msg + NORMAL)
				Info(msg)
			else:
				msg = f"Test {test} FAILED"
				print(RED + msg + NORMAL)
				Error(msg)
				msg = f"Files '{left}' and '{right}' didn't match"
				print(YELLOW + msg + NORMAL)
				Warn(msg)
		else:
			break
	test -= 1
	if test == success:
		msg = f"Result: {success} of {test} have passed."
		print(GREEN + msg + NORMAL)
		Info(msg)
	else:
		msg = f"Result: {test-success} of {test} have failed."
		print(RED + msg + NORMAL)
		Error(msg)


if __name__ == "__main__":
	main()
