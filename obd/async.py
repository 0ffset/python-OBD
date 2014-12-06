
########################################################################
#                                                                      #
# python-OBD: A python OBD-II serial module derived from pyobd         #
#                                                                      #
# Copyright 2004 Donour Sizemore (donour@uchicago.edu)                 #
# Copyright 2009 Secons Ltd. (www.obdtester.com)                       #
# Copyright 2014 Brendan Whitfield (bcw7044@rit.edu)                   #
#                                                                      #
########################################################################
#                                                                      #
# async.py                                                             #
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

import obd
import time
import threading
from utils import Response
from commands import OBDCommand
from debug import debug



class Async(obd.Obd):
	""" subclass representing an OBD-II connection """

	def __init__(self, portstr=None):
		super(Async, self).__init__(portstr)
		self.commands  = {} # key = OBDCommand, value = Response
		self.callbacks = {} # key = OBDCommand, value = Callback
		self.thread    = None
		self.running   = False


	def start(self):
		if self.is_connected():
			debug("Starting async thread")
			self.running = True
			self.thread = threading.Thread(target=self.run)
			self.thread.daemon = True
			self.thread.start()
		else:
			debug("Async thread not started because no connection was made")


	def stop(self):
		if self.thread is not None:
			debug("Stopping async thread...")
			self.running = False
			self.thread.join()
			self.thread = None
			debug("Async thread stopped")


	def close(self):
		self.stop()
		super(Async, self).close()


	def watch(self, c, callback=None, force=False):

		if not (self.has_command(c) or force):
			debug("'%s' is not supported" % str(c), True)
			return

		# if running, the daemon thread must be stopped before altering the command dict
		was_running = self.running
		if self.running:
			self.stop()

		# store the command
		if not self.commands.has_key(c):
			debug("Watching command: %s" % str(c))
			self.commands[c] = Response() # give it an initial value

		# store the callback 
		if hasattr(callback, "__call__") and (not self.callbacks.has_key(c)):
			debug("subscribing callback for command: %s" % str(c))
			self.callbacks[c] = callback

		# start if neccessary
		if was_running:
			self.start()


	def unwatch(self, c):

		# if running, the daemon thread must be stopped before altering the command dict
		was_running = self.running
		if self.running:
			self.stop()

		debug("Unwatching command: %s" % str(c))
		self.commands.pop(c, None)
		self.callbacks.pop(c, None)

		# start if neccessary
		if was_running:
			self.start()


	def unwatch_all(self):
		commands = self.commands.keys()

		for c in commands:
			self.unwatch(c)


	def query(self, c):
		if self.commands.has_key(c):
			return self.commands[c]
		else:
			return Response()


	def run(self):
		""" Daemon thread """

		# loop until the stop signal is recieved
		while self.running:

			if len(self.commands) > 0:
				# loop over the requested commands, send, and collect the response
				for c in self.commands:
					r = self.send(c)

					# store the response
					self.commands[c] = r

					# fire the callback, if we have one
					if c in self.callbacks:
						self.callbacks[c](r)

			else:
				time.sleep(1) # idle until the user calls stop() or watch()
