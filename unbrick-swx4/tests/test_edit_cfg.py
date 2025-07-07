#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sys
import os
import shutil

# Get the directory of the current script
current_dir = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
# Construct the path to the 'assets' directory
assets_dir = os.path.normpath(os.path.join(current_dir, '..', 'assets'))

# Add the 'assets' directory to sys.path
sys.path.append(assets_dir)
# Now you can import helper_functions as if it were a module
import edit_cfg

test_file = os.path.join(current_dir, 'test.cfg')

def MkCfgClone():
	if os.path.exists(test_file):
		os.unlink(test_file)
	src_cfg = os.path.normpath(os.path.join(current_dir, '..', '..', 'backup', '20250701-printer.cfg'))
	shutil.copyfile(src_cfg, test_file)

def Write(fh, res : 'test_edit.Res') -> None:
	print(res)
	fh.write(f"{res}\n")


def BulkGet(fh):
	Write(fh, edit_cfg.main(['GetKey', 'stepper_x', 'enable_pin', test_file]))

def main():
	MkCfgClone()
	with open(os.path.join(current_dir, 'test_edit_cfg.log'), 'wt') as fh:
		BulkGet(fh)

if __name__ == "__main__":
	main()
