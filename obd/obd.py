#!/usr/bin/env python

import time

from port import OBDPort, State
from commands import commands
from utils import scanSerial, Response



class OBD():
	""" class representing an OBD-II connection with it's assorted sensors """

	def __init__(self, portstr=None):
		self.port = None
		self.supportedCommands = []

		# initialize by connecting and loading sensors
		if self.connect(portstr):
			self.load_commands()


	def connect(self, portstr=None):
		""" attempts to instantiate an OBDPort object. Return boolean for success/failure"""

		if portstr is None:
			portnames = scanSerial()

			for port in portnames:

				self.port = OBDPort(port)

				if(self.port.state == State.Connected):
					# success! stop searching for serial
					break
		else:
			self.port = OBDPort(portstr)

		return self.is_connected()


	def is_connected(self):
		return (self.port is not None) and (self.port.state == State.Connected)


	def get_port_name(self):
		return self.port.get_port_name()


	def load_commands(self):
		""" queries for available PIDs, sets their support status, and compiles a list of command objects """

		self.supportedCommands = []

		pid_getters = commands.pid_getters()

		for get in pid_getters:
			# GET commands should sequentialy turn themselves on (become marked as supported)
			# MODE 1 PID 0 is marked supported by default 
			if not self.has_command(get):
				continue

			response = self.query(get) # ask nicely

			if response.isEmpty():
				continue
			
			supported = response.value # string of binary 01010101010101

			# loop through PIDs binary
			for i in range(len(supported)):
				if supported[i] == "1":

					mode = get.getModeInt()
					pid  = get.getPidInt() + i + 1

					c = commands[mode][pid]
					c.supported = True
					self.supportedCommands.append(c)


	def print_commands(self):
		for c in self.supportedCommands:
			print str(c)

	def has_command(self, c):
		return c.supported

	def query(self, command):
		print "TX: " + str(command)
		if self.has_command(command):
			return self.port.get_sensor_value(command)
		else:
			print "'%s' is not supported" % str(command)
			return Response() # return empty response




if __name__ == "__main__":

	o = OBD()
	time.sleep(3)
	if not o.is_connected():
		print "Not connected"
	else:
		print "Connected to " + o.get_port_name()
		o.print_commands()
