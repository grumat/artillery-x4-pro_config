#
# -*- coding: UTF-8 -*-
#
# Spellchecker: words fname libtools

from .contents import AnyBuffer, Contents
from .libtools import EncodeB64, StringCRC

class Commands(object):
	def __init__(self, fname) -> None:
		self.fname = fname
		self.contents = Contents()
		self.contents.Load(fname)

	def GetLine(self, section : str, key : str) -> str|Exception:
		sec_buf = self.contents.FindSection(section)
		if sec_buf is None:
			return RuntimeError(f"Cannot find section {section}")
		data = sec_buf.FindValue(key)
		if data is None:
			return RuntimeError(f"Cannot find key {key} in section {section}")
		return data.value

	def GetSec(self, section : str) -> str|Exception:
		sec_buf = self.contents.FindSection(section)
		if sec_buf is None:
			return RuntimeError(f"Cannot find section {section}")
		return EncodeB64(sec_buf.lines)

	def GetSecCRC(self, section : str) -> str|Exception:
		sec_buf = self.contents.FindSection(section)
		if sec_buf is None:
			return RuntimeError(f"Cannot find section {section}")
		crc = StringCRC(sec_buf.GetLineEssence(), 0)
		return f"{crc:08X}"
	
	def GetKeyML(self, section : str, key : str) -> str|Exception:
		sec_buf = self.contents.FindSection(section)
		if sec_buf is None:
			return RuntimeError(f"Cannot find section {section}")
		data = sec_buf.GetMultiLine(key)
		if data is None:
			return RuntimeError(f"Cannot find key {key} in section {section}")
		return EncodeB64([l.raw_content for l in data])
	
	def GetKeyCRC(self, section : str, key : str) -> str|Exception:
		sec_buf = self.contents.FindSection(section)
		if sec_buf is None:
			return RuntimeError(f"Cannot find section {section}")
		data = sec_buf.GetMultiLine(key)
		if data is None:
			return RuntimeError(f"Cannot find key {key} in section {section}")
		data = '\n'.join([l.uncommented for l in AnyBuffer.GetCrucialLines(data)])
		crc = StringCRC(data, 0)
		return f"{crc:08X}"
	
	def GetSave(self) -> str:
		data = [l.raw_content for l in self.contents.persistence.lines]
		return EncodeB64(data)

