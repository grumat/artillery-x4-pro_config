#
# -*- coding: UTF-8 -*-

import sys
import os
import logging

def GetMainScriptPath():
	# If running as a PyInstaller bundle (frozen)
	if getattr(sys, 'frozen', False):
		# Return the path to the executable
		return os.path.dirname(sys.executable)
	else:
		# Return the path to the script
		return os.path.dirname(os.path.abspath(__file__))

def GetAssetsFolder():
	# If running as a PyInstaller bundle (frozen)
	if getattr(sys, 'frozen', False):
		# Return the path to the executable
		base_path = sys._MEIPASS
	else:
		# Running as a script
		base_path = os.path.dirname(os.path.abspath(__file__))
	return os.path.join(base_path, 'assets')

def GetIniFileName():
	return os.path.join(GetMainScriptPath(), 'unbrick-swx4.ini')

def GetLogFileName():
	return os.path.join(GetMainScriptPath(), 'unbrick-swx4.log')

logger = logging.getLogger('unbrick-swx4')
logger.setLevel(logging.DEBUG)
# Create a file handler
_handler = logging.FileHandler(os.path.join(GetMainScriptPath(), 'unbrick-swx4.log'))
_handler.setLevel(logging.DEBUG)
# Create a formatter with timestamp
_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
_handler.setFormatter(_formatter)
# Add the handler to the logger
logger.addHandler(_handler)

def Debug(msg : str) -> None:
	logger.debug(msg)

def Info(msg : str) -> None:
	logger.info(msg)

def Warn(msg : str) -> None:
	logger.warning(msg)

def Error(msg : str) -> None:
	logger.error(msg)
