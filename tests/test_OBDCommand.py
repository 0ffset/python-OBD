
from obd.commands import OBDCommand
from obd.decoders import noop


def test_basic_OBDCommand():
	#                 name       description        mode  cmd bytes decoder
	cmd = OBDCommand("Test", "example OBD command", "01", "23", 2, noop)
	assert cmd.name      == "Test"
	assert cmd.desc      == "example OBD command"
	assert cmd.mode      == "01"
	assert cmd.pid       == "23"
	assert cmd.bytes     == 2
	assert cmd.decode    == noop
	assert cmd.supported == False

	assert cmd.get_command()  == "0123"
	assert cmd.get_mode_int() == 1
	assert cmd.get_pid_int()  == 35

	cmd = OBDCommand("Test", "example OBD command", "01", "23", 2, noop, True)
	assert cmd.supported == True


def test_data_stripping():
	#                 name       description        mode  cmd bytes decoder
	cmd = OBDCommand("Test", "example OBD command", "01", "00", 2, noop)
	r = cmd.compute("41 00 01 01\r\n")
	assert not r.is_null()
	assert r.value == "0101"


def test_data_not_hex():
	#                 name       description        mode  cmd bytes decoder
	cmd = OBDCommand("Test", "example OBD command", "01", "00", 2, noop)
	r = cmd.compute("41 00 wx yz\r\n")
	assert r.is_null()
	

def test_data_length():
	#                 name       description        mode  cmd bytes decoder
	cmd = OBDCommand("Test", "example OBD command", "01", "00", 2, noop)
	r = cmd.compute("41 00 01 23 45\r\n")
	assert r.value == "0123"
	r = cmd.compute("41 00 01\r\n")
	assert r.value == "0100"
