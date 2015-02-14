
########################################################################
#                                                                      #
# python-OBD: A python OBD-II serial module derived from pyobd         #
#                                                                      #
# Copyright 2004 Donour Sizemore (donour@uchicago.edu)                 #
# Copyright 2009 Secons Ltd. (www.obdtester.com)                       #
# Copyright 2009 Peter J. Creath                                       #
# Copyright 2015 Brendan Whitfield (bcw7044@rit.edu)                   #
#                                                                      #
########################################################################
#                                                                      #
# OBDCommand.py                                                        #
#                                                                      #
# This file is part of python-OBD (a derivative of pyOBD)              #
#                                                                      #
# python-OBD is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 2 of the License, or    #
# (at your option) any later version.                                  #
#                                                                      #
# python-OBD is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# along with python-OBD.  If not, see <http://www.gnu.org/licenses/>.  #
#                                                                      #
########################################################################

import re
from utils import *
from debug import debug


class OBDCommand():
	def __init__(self, name, desc, mode, pid, returnBytes, decoder, supported=False):
		self.name       = name
		self.desc       = desc
		self.mode       = mode
		self.pid        = pid
		self.bytes      = returnBytes # number of bytes expected in return
		self.decode     = decoder
		self.supported  = supported

	def clone(self):
		return OBDCommand(self.name,
		                  self.desc,
		                  self.mode,
		                  self.pid,
		                  self.bytes,
		                  self.decode)

	def get_command(self):
		return self.mode + self.pid # the actual command transmitted to the port

	def get_mode_int(self):
		return unhex(self.mode)

	def get_pid_int(self):
		return unhex(self.pid)

	def compute(self, messages):

		_bytes = []

		if len(messages) == 1:
			_bytes = messages[0].data_bytes
		else:
			pass


		# create the response object with the raw data recieved
		r = Response(message)

		# combine the bytes back into a hex string, excluding the header + mode + pid, and trailing checksum
		_bytes = "".join(lines[0][5:-1])

		if ("NODATA" not in _data) and isHex(_data):

			# constrain number of bytes in response
			if (self.bytes > 0): # zero bytes means flexible response
				_data = constrainHex(_data, self.bytes)

			# decoded value into the response object
			r.set(self.decode(_data))

		else:
			# not a parseable response
			debug("return data could not be decoded")

		return r

	def __str__(self):
		return "%s%s: %s" % (self.mode, self.pid, self.desc)

	def __hash__(self):
		# needed for using commands as keys in a dict (see async.py)
		return hash((self.mode, self.pid))

	def __eq__(self, other):
		if isinstance(other, OBDCommand):
			return (self.mode, self.pid) == (other.mode, other.pid)
		else:
			return False
