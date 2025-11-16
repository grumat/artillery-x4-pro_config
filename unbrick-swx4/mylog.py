#
# -*- coding: UTF-8 -*-

LOG = None

def Log(msg):
	"""
	This function writes a message to the log file. In the case the message is a byte stream, it 
	provides automatic conversion.
	It is expected that the `LOG` file instance exists.
	"""
	if LOG:
		# Converts non-string input to string
		if type(msg) != str:
			msg = str(msg, "utf-8", errors="replace")
		LOG.write(msg)
		LOG.flush()
