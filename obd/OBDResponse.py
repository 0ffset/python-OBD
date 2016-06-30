
########################################################################
#                                                                      #
# python-OBD: A python OBD-II serial module derived from pyobd         #
#                                                                      #
# Copyright 2004 Donour Sizemore (donour@uchicago.edu)                 #
# Copyright 2009 Secons Ltd. (www.obdtester.com)                       #
# Copyright 2009 Peter J. Creath                                       #
# Copyright 2016 Brendan Whitfield (brendan-w.com)                     #
#                                                                      #
########################################################################
#                                                                      #
# OBDResponse.py                                                       #
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


import time
from .codes import *


class OBDResponse():
    """ Standard response object for any OBDCommand """

    def __init__(self, command=None, messages=None):
        self.command  = command
        self.messages = messages if messages else []
        self.value    = None
        self.time     = time.time()

    @property
    def unit(self):
        # for backwards compatibility
        if isinstance(self.value, Unit.Quantity):
            return str(self.value.u)
        elif self.value == None:
            return None
        else:
            return str(type(self.value))

    def is_null(self):
        return (not self.messages) or (self.value == None)

    def __str__(self):
        return str(self.value)



"""
    Special value types used in OBDResponses
    instantiated in decoders.py
"""


class Status():
    def __init__(self):
        self.MIL           = False
        self.DTC_count     = 0
        self.ignition_type = ""
        self.tests         = []


class Test():
    def __init__(self, name, available, incomplete):
        self.name       = name
        self.available  = available
        self.incomplete = incomplete

    def __str__(self):
        a = "Available" if self.available else "Unavailable"
        c = "Incomplete" if self.incomplete else "Complete"
        return "Test %s: %s, %s" % (self.name, a, c)


class Monitor():
    def __init__(self):
        self.tests = []

        # make all TID tests available as properties
        for tid in TEST_IDS:
            name = TEST_IDS[tid][0]
            test = MonitorTest()
            self.__dict__[name] = test
            self.tests.append(test)

    def __str__(self):
        valid_tests = [str(test) for test in tests if not test.is_null()]
        return "\n".join(valid_tests)


class MonitorTest():
    def __init__(self):
        self.tid = None
        self.desc = None
        self.value = None
        self.min = None
        self.max = None

    @property
    def passed(self):
        return (self.value >= self.min) and (self.value <= self.max)

    def is_null(self):
        return self.tid is None or self.value is None

    def __str__(self):
        return "%s : %s [%s]" % (self.desc,
                                 str(self.value),
                                 "PASSED" if self.passed else "FAILED")
