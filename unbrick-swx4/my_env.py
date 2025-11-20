#
# -*- coding: UTF-8 -*-

import sys
import os
import logging

__all__ = ["GetMainScriptPath", "GetAssetsFolder", "GetIniFileName", "GetLogFileName", "GetBackupFolder", "GetLocalePath", "Debug", "Info", "Warn", "Error"]


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

def GetLogFileName():
	return os.path.join(GetMainScriptPath(), 'unbrick-swx4.log')

def GetBackupFolder():
	return os.path.join(GetMainScriptPath(), 'backup')

def _GetStaticData():
	# If running as a PyInstaller bundle (frozen)
	# Defaults to running as a script
	base_path = os.path.dirname(os.path.abspath(__file__))
	if getattr(sys, 'frozen', False):
		# Return the path to the executable # spellchecker:disable-next-line
		base_path: str = getattr(sys, '_MEIPASS', base_path)  # type: ignore
	return base_path

def GetAssetsFolder():
	return os.path.join(_GetStaticData(), 'assets')

def GetLocalePath():
	return os.path.join(_GetStaticData(), 'locale')

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
