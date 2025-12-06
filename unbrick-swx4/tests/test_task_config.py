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

#from my_env import Info
if TYPE_CHECKING:
	from ..user_options import UserOptions
	from ..my_workflow import Workflow
	from .test_utils import *
else:
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
	wf = Workflow(opts)
	opts.model_attr = True
	wf.Test()

def step_002(opts : UserOptions):
	opts.printer = SWX4PRO + START_WITH_PLUS_UPG	# Artillery pro target with Artillery plus config
	opts.model_attr = True
	wf = Workflow(opts)
	wf.Test()

def step_003(opts : UserOptions):
	opts.printer = SWX4PRO + START_WITH_PRO_UPG
	opts.model_attr = False
	opts.stepper_z_current = 1
	opts.extruder_accel = 1
	opts.extruder_current = 1
	opts.probe_offset = 1
	opts.probe_sampling = 2
	opts.probe_validation = 1
	opts.screws_tilt_adjust = 1
	wf = Workflow(opts)
	wf.Test()

def step_004(opts : UserOptions):
	opts.printer = SWX4PRO + START_WITH_PRO_UPG
	opts.model_attr = False
	opts.stepper_z_current = 2
	opts.extruder_accel = 2
	opts.extruder_current = 2
	opts.probe_offset = 2
	opts.probe_sampling = 1
	opts.probe_validation = 2
	opts.screws_tilt_adjust = 2
	wf = Workflow(opts)
	wf.Test()

def step_005(opts : UserOptions):
	opts.printer = SWX4PRO + START_WITH_PRO_GRUMAT
	opts.model_attr = True
	opts.stepper_z_current = 0
	opts.extruder_accel = 3
	opts.extruder_current = 3
	opts.probe_offset = 0
	opts.probe_sampling = 0
	opts.probe_validation = 0
	opts.screws_tilt_adjust = 1
	wf = Workflow(opts)
	wf.Test()

def main():
	opts = UserOptions()
	opts.model_attr = True
	opts.stepper_z_current = 0
	opts.extruder_accel = 0
	opts.extruder_current = 0
	opts.probe_offset = 0
	opts.probe_sampling = 0
	opts.probe_validation = 0
	opts.screws_tilt_adjust = 0
	opts.fan_rename = False
	opts.mb_fan_fix = True
	opts.hb_fan_speed = 0
	opts.mb_fan_speed = 0
	opts.temp_mcu = False
	opts.nozzle_wipe = 0
	opts.purge_line = 0
	opts.enable_m600 = False
	opts.pause = 0
	test = 0
	success = 0
	left = os.path.join(current_dir, 'backup', 'printer.cfg')
	while True:
		test += 1
		method = f'step_{test:03d}'
		if hasattr(sys.modules[__name__], method):
			print("\033[1m" + f"Starting Test {test}" + NORMAL)
			getattr(sys.modules[__name__], method)(opts)
			right = os.path.join(current_dir, 'results', f'printer-{test:03d}.cfg')
			res = files_equal(left, right)
			success += res
			if res:
				print(GREEN + f"Test {test} PASSED" + NORMAL)
			else:
				print('\033[31m' + f"Test {test} FAILED" + NORMAL)
		else:
			break
	test -= 1
	if test == success:
		print(GREEN + f"Result: {success} of {test} have passed." + NORMAL)
	else:
		print(RED + f"Result: {success} of {test} have failed." + NORMAL)


if __name__ == "__main__":
	main()
