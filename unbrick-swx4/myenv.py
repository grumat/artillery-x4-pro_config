#
# -*- coding: UTF-8 -*-

import sys
import os

def GetMainScriptPath():
	# If running as a PyInstaller bundle (frozen)
	if getattr(sys, 'frozen', False):
		# Return the path to the executable
		return os.path.dirname(sys.executable)
	else:
		# Return the path to the script
		return os.path.dirname(os.path.abspath(__file__))

def GetIniFileName():
	return os.path.join(GetMainScriptPath(), 'unbrick-swx4.ini')