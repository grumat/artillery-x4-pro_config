#
# -*- coding: UTF-8 -*-
#
# Spellchecker: words levelname USWX unbrick

import sys
import os
import logging
from typing import TYPE_CHECKING

__all__ = ["GetMainScriptPath", "GetAssetsFolder", "GetIniFileName", "GetLogFileName", "GetBackupFolder", "GetLocalePath", "Debug", "Info", "Warn", "Error"]


TEST_MODE = os.getenv("USWX4_TEST")

NORMAL = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"



def GetMainScriptPath():
	# If running as a PyInstaller bundle (frozen)
	if getattr(sys, 'frozen', False):
		# Return the path to the executable
		return os.path.dirname(sys.executable)
	elif TEST_MODE is None:
		# Return the path to the script
		return os.path.dirname(os.path.abspath(__file__))
	else:
		# Return the path to the script
		return os.path.dirname(os.path.abspath(sys.argv[0]))

def GetIniFileName():
	if TYPE_CHECKING or (TEST_MODE is None):
		return os.path.join(GetMainScriptPath(), 'unbrick-swx4.ini')
	else:
		return os.path.join(GetMainScriptPath(), f'{TEST_MODE}.ini')

def GetLogFileName():
	if TYPE_CHECKING or (TEST_MODE is None):
		return os.path.join(GetMainScriptPath(), 'unbrick-swx4.log')
	else:
		return os.path.join(GetMainScriptPath(), f'{TEST_MODE}.log')

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
_handler = logging.FileHandler(GetLogFileName())
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
