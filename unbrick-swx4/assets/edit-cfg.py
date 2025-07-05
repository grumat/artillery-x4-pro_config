#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# PLZ! No comments and keep it compact. Degrades perf on serial port

import sys
import os
import re
import bz2
import base64
import fnmatch

MODULE = sys.modules[__name__]
DF = r"D:\TEMP\yuntu\ref\artillery_X4_plus.000"
ARGS = sys.argv.copy()
CFG_FILE = None

NO_LOC = (-1,-1)
OK = ('.', "OK", NO_LOC)
MISSING_ARG = ('!', "ARG", NO_LOC)
INVALID_KEY = lambda loc : ('!', "INV", loc)
INV_FMT = ('!', "FMT", NO_LOC)
NO_SECTION = ('!', "SEC", NO_LOC)
MULT_SECTION = ('!', "SEC+", NO_LOC)
NO_KEY = lambda pos : ('!', "KEY", pos)
MULT_KEY = ('!', "KEY+", NO_LOC)

def GetArg() -> str:
	global ARGS
	if len(ARGS):
		v = ARGS[0]
		del ARGS[0]
		return v
	return None

def GetLines() -> list:
	global CFG_FILE
	f = GetArg()
	if not f:
		f = DF
	CFG_FILE = f
	if not os.path.exists(f):
		print("!FILE")
		sys.exit(1)
	with open(f, "rt", encoding="UTF-8") as fh:
		lines = fh.readlines()
	return lines

def WriteLines(lines : list) -> tuple:
	if not lines:
		return ('!', "EMPTY", NO_LOC)
	if not CFG_FILE:
		return ('!', "READ", NO_LOC)
	tpl, _ = os.path.splitext(CFG_FILE)
	idx = -1
	while True:
		idx += 1
		fn = f"{tpl}.{idx:03d}"
		if not os.path.exists(fn):
			break
	with open(fn, "wt", encoding="UTF-8", newline='\n') as fh:
		fh.writelines(lines)
	return OK

def MatchSection(sec : list[str], qry : list[str]):
	if qry[0] == '*':
		return True
	if len(sec) != len(qry):
		return False
	for i, s in enumerate(sec):
		if i:
			s = s.upper()
			m = qry[i].upper()
		else:
			m = qry[i]
		if not fnmatch.fnmatch(s, m):
			return False
	return True

def MkSection(l : str) -> list:
	r = []
	for k in l.split():
		r.append((r and (r[0] == "gcode_macro")) and k.strip().upper() or k.strip())
	return r

def CleanLine(l : str) -> str:
	l = l.rstrip()
	if l:
		pos = l.find('#')
		if pos < 0:
			pos = l.find(';')
		if pos >= 0:
			l = l[:pos].rstrip()
	return l

def EditLine(old : str, lcol : int, upt : str):
	rem = (len(old) > lcol) and old[lcol:] or ""
	return upt + rem

def EncodeMultiLine(ml : str) -> str:
	if isinstance(ml[0], MLine):
		ml = "".join([l.line for l in ml])
	elif isinstance(ml, list):
		ml = "".join(ml)
	pk = bz2.compress(ml.encode('utf-8'))
	enc = base64.b64encode(pk)
	return enc.decode('utf-8')

def DecodeMultiLine(b64 : str) -> list:
	ba = base64.b64decode(b64.encode('utf-8'))
	ml = bz2.decompress(ba).decode('utf-8')
	res = []
	t = ""
	for ch in ml:
		t += ch
		if ch == '\n':
			res.append(t)
			t = ""
	return res

class MLine(object):
	def __init__(self, line : str, lno : int):
		self.line = line
		self.lcol = len(line)
		self.idx = lno
	def GetPos(self):
		return (self.idx,None)

class Key(object):
	def __init__(self, label : str, lcol : int, lno : int, value):
		self.name = label.strip()
		self.lcol = lcol
		self.idx_0 = lno
		self.idx_n = lno
		self.value = value.strip()
		if not self.value:
			self.value = []
	def IsMultiLine(self):
		return isinstance(self.value, list)
	def GetPos(self):
		if self.IsMultiLine():
			return (self.idx_0,self.idx_n)
		else:
			return (self.idx_0,None)

class Section(object):
	def __init__(self, label : str, lcol : int, lno : int):
		self.name = MkSection(label)
		self.lcol = lcol
		self.idx_0 = lno
		self.idx_n = lno
		self.keys = []
	def GetPos(self):
		return (self.idx_0,self.idx_n)
	def GetLabel(self):
		return ' '.join(self.name)

def read_all_data_(lines) -> list:
	sections = []
	pat = re.compile(r"\[(.+)\]")
	sect = None
	key = None
	it = iter(lines)
	lno = -1
	rl = None
	l = None
	m = None
	def NextLine():
		nonlocal lno, rl, l, m, sect, key
		lno += 1
		rl = next(it)
		l = CleanLine(rl)
		m = (l and (l[0] == '[')) and pat.match(l) or None
		if sect:
			sect.idx_n = lno
		if key:
			key.idx_n = lno
	NextLine()
	while True:
		try:
			if not l:
				NextLine()
			elif m:
				sect = Section(m.group(1), len(l), lno)
				NextLine()
				while(True):
					if (not l) or l[0].isspace():
						NextLine()
					elif (not m) and (rl[0].isalnum() or (rl[0] == '_') and ':' in l):
						k, v = l.split(':', 1)
						key = Key(k, len(l), lno, v)
						NextLine()
						if key.IsMultiLine():
							while True:
								if rl:
									if rl[0].isspace():
										key.value.append(MLine(l, lno))
									else:
										break
								NextLine()
						sect.keys.append(key)
						key = None
					else:
						sections.append(sect)
						sect = None
						break
		except StopIteration:
			if sect:
				if key:
					sect.keys.append(key)
				sections.append(sect)
			break
	return sections

def read_key_(sections : list[Section], sec : list[str], k : str) -> tuple:
	sec = [s for s in sections if s.name == sec]
	if not sec:
		return NO_SECTION
	if len(sec) > 1:
		return MULT_SECTION
	sec : Section = sec[0]
	key = [i for i in sec.keys if i.name == k]
	if not key:
		return NO_KEY(sec.GetPos())
	if len(key) > 1:
		return MULT_KEY(sec.GetPos())
	key : Key = key[0]
	return ('k', key, key.GetPos())

def GetKey() -> tuple:
	sec = GetArg()
	if sec:
		k = GetArg()
		if k:
			lines = GetLines()
			sections = read_all_data_(lines)
			if not sections:
				return INV_FMT
			code, val, lno = read_key_(sections, MkSection(sec), k)
			if code == 'k':
				key : Key = val
				if key.IsMultiLine():
					code = '*'
					val = EncodeMultiLine(key.value)
				else:
					code = '='
					val = key.value
			return code, val, lno
	return MISSING_ARG

def EditKey() -> tuple:
	sec = GetArg()
	if sec:
		k = GetArg()
		if k:
			data = GetArg()
			if data:
				lines = GetLines()
				sections = read_all_data_(lines)
				if not sections:
					return INV_FMT
				code, val, lno = read_key_(sections, MkSection(sec), k)
				if code == 'k':
					val : Key
					if val.IsMultiLine():
						return INVALID_KEY(lno)
					if val.value == data:
						return OK
					lines[lno[0]] = EditLine(lines[lno[0]], val.lcol, f"{k}:{data}")
					return WriteLines(lines)
				return code, val, lno
	return MISSING_ARG

def ListSec() -> tuple:
	sec = GetArg()
	if sec:
		sec = MkSection(sec)
		lines = GetLines()
		sections = read_all_data_(lines)
		if not sections:
			return INV_FMT
		cnt = 0
		res = ""
		loc = None
		for s in sections:
			s : Section
			if MatchSection(s.name, sec):
				loc = s.GetPos()
				cnt += 1
				if res:
					res += '\n'
				res += s.GetLabel()
		if cnt > 1:
			print (res)
			return '*', EncodeMultiLine(res), NO_LOC
		if cnt == 1:
			return '=', res, loc
		return NO_SECTION

if __name__ == "__main__":
	code = '!'
	val = "ARG"
	range = NO_LOC
	try:
		_ = GetArg()
		fn = GetArg()
		if fn:
			if hasattr(MODULE, fn):
				code, val, range = getattr(MODULE, fn)()
			else:
				val = "FN"
	except Exception as e:
		val = "XCP"
		if 1:
			print(e)
	print(f"{code}{val}")
