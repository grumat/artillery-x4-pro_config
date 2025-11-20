#
# -*- coding: UTF-8 -*-

import locale
from i18n import _

def TryParseInt(s, default=0) -> int:
	try:
		return int(s)
	except ValueError:
		return default

def FmtByteSize(num : int) -> str:
	if num > 1100000:
		num_f = float(num) / (1000.0 * 1000.0)
		sc = _("GBi")
	elif num > 1100:
		num_f = float(num) / 1000.0
		sc = _("MBi")
	else:
		num_f = float(num)
		sc = _("KBi")
	res = locale.format_string("%5.3f", num_f, grouping=True)
	return res + ' ' + sc
