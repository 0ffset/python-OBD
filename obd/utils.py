import serial
import errno



class Unit:
	NONE       = None
	BITSTRING  = "Bit String"
	DTC        = "Diagnostic Trouble Code"
	PERCENT    = "Percent"
	VOLT       = "Volt"
	F          = "F"
	C          = "C"
	SEC        = "Second"
	MIN        = "Minute"
	KPA        = "kPa"
	PSI        = "PSI"
	KPH        = "KPH"
	MPH        = "MPH"
	DEGREES    = "Degrees"
	GRAM_P_SEC = "Grams per Second"


class Value():
	def __init__(self, value, unit):
		self.value = value
		self.unit = unit

	def __str__(self):
		return "%s %s" % (str(self.value), str(self.unit))


def unhex(_hex):
	return int(_hex, 16)

def unbin(_bin):
	return int(_bin, 2)

def bitstring(_hex):
	return bin(unhex(_hex))[2:]


def tryPort(portStr):
	"""returns boolean for port availability"""
	try:
		s = serial.Serial(portStr)
		s.close()   # explicit close 'cause of delayed GC in java
		return True

	except serial.SerialException:
		pass
	except OSError as e:
		if e.errno != errno.ENOENT: # permit "no such file or directory" errors
			raise e

	return False



def scanSerial():
	"""scan for available ports. return a list of serial names"""
	available = []

	# Enable Bluetooh connection
	for i in range(10):
		portStr = "/dev/rfcomm%d" % i
		if tryPort(portStr):
			available.append(portStr)

	# Enable USB connection
	for i in range(256):
		portStr = "/dev/ttyUSB%d" % i
		if tryPort(portStr):
			available.append(portStr)

	# Enable obdsim
	'''
	for i in range(256):
		portStr = "/dev/pts/%d" % i
		if tryPort(portStr):
			available.append(portStr)
	'''
	
	return available
