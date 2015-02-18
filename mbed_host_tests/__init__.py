"""
mbed SDK
Copyright (c) 2011-2013 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from optparse import OptionParser

from host_tests_registry import HostRegistry

# Host test supervisors
from host_tests.echo import EchoTest
from host_tests.rtc_auto import RTCTest
from host_tests.stdio_auto import StdioTest
from host_tests.hello_auto import HelloTest
from host_tests.detect_auto import DetectPlatformTest
from host_tests.wait_us_auto import WaitusTest
from host_tests.default_auto import DefaultAuto
from host_tests.dev_null_auto import DevNullTest
from host_tests.tcpecho_server_auto import TCPEchoServerTest
from host_tests.udpecho_server_auto import UDPEchoServerTest
from host_tests.tcpecho_client_auto import TCPEchoClientTest
from host_tests.udpecho_client_auto import UDPEchoClientTest

# Basic host test functionality
from host_tests_runner.host_test import DefaultTestSelectorBase

# Populate registry with supervising objects
HOSTREGISTRY = HostRegistry()
HOSTREGISTRY.register_host_test("echo", EchoTest())
HOSTREGISTRY.register_host_test("default", DefaultAuto())
HOSTREGISTRY.register_host_test("rtc_auto", RTCTest())
HOSTREGISTRY.register_host_test("hello_auto", HelloTest())
HOSTREGISTRY.register_host_test("stdio_auto", StdioTest())
HOSTREGISTRY.register_host_test("detect_auto", DetectPlatformTest())
HOSTREGISTRY.register_host_test("default_auto", DefaultAuto())
HOSTREGISTRY.register_host_test("wait_us_auto", WaitusTest())
HOSTREGISTRY.register_host_test("dev_null_auto", DevNullTest())
HOSTREGISTRY.register_host_test("tcpecho_server_auto", TCPEchoServerTest())
HOSTREGISTRY.register_host_test("udpecho_server_auto", UDPEchoServerTest())
HOSTREGISTRY.register_host_test("tcpecho_client_auto", TCPEchoClientTest())
HOSTREGISTRY.register_host_test("udpecho_client_auto", UDPEchoClientTest())

###############################################################################
# Functional interface for test supervisor registry
###############################################################################


def get_host_test(ht_name):
    """ Returns registered host test supervisor.
        If host test is not registered by name function returns None.
    """
    return HOSTREGISTRY.get_host_test(ht_name)

def is_host_test(ht_name):
    """ Checks if host test supervisor is registered in host test registry.
        If so return True otherwise False.
    """
    return HOSTREGISTRY.is_host_test(ht_name)

class DefaultTestSelector(DefaultTestSelectorBase):
    # Select default host_test supervision (replaced after autodetection)
    test_supervisor = get_host_test("default")

    def __init__(self, options=None):
        DefaultTestSelectorBase.__init__(self, options)

    def run(self):
        """ Test runner for host test. This function will start executing
            test and forward test result via serial port to test suite
        """
        # Copy image to device
        self.notify("HOST: Copy image onto target...")
        result = self.mbed.copy_image()
        if not result:
            self.print_result(self.RESULT_IOERR_COPY)

        # Initialize and open target's serial port (console)
        self.notify("HOST: Initialize serial port...")
        result = self.mbed.init_serial()
        if not result:
            self.print_result(self.RESULT_IO_SERIAL)

        # Reset device
        self.notify("HOST: Reset target...")
        result = self.mbed.reset()
        if not result:
            self.print_result(self.RESULT_IO_SERIAL)

        # Run test
        try:
            CONFIG = self.detect_test_config(verbose=True) # print CONFIG

            if "host_test_name" in CONFIG:
                if is_host_test(CONFIG["host_test_name"]):
                    self.test_supervisor = get_host_test(CONFIG["host_test_name"])
            result = self.test_supervisor.test(self)    #result = self.test()

            if result is not None:
                self.print_result(result)
            else:
                self.notify("HOST: Passive mode...")
        except Exception, e:
            print str(e)
            self.print_result(self.RESULT_ERROR)

def init_host_test_cli_params():
    """ Function creates parser object and returns populated options object.
        Options object later can be used to populate host test selector script.
    """
    parser = OptionParser()

    parser.add_option("-m", "--micro",
                      dest="micro",
                      help="The target microcontroller",
                      metavar="MICRO")

    parser.add_option("-p", "--port",
                      dest="port",
                      help="The serial port of the target mbed",
                      metavar="PORT")

    parser.add_option("-d", "--disk",
                      dest="disk",
                      help="The target disk path",
                      metavar="DISK_PATH")

    parser.add_option("-f", "--image-path",
                      dest="image_path",
                      help="Path with target's image",
                      metavar="IMAGE_PATH")

    parser.add_option("-c", "--copy",
                      dest="copy_method",
                      help="Copy method selector",
                      metavar="COPY_METHOD")

    parser.add_option("-C", "--program_cycle_s",
                      dest="program_cycle_s",
                      help="Program cycle sleep. Define how many seconds you want wait after copying bianry onto target",
                      type="float",
                      metavar="COPY_METHOD")

    parser.add_option("-t", "--timeout",
                      dest="timeout",
                      help="Timeout",
                      metavar="TIMEOUT")

    parser.add_option("-r", "--reset",
                      dest="forced_reset_type",
                      help="Forces different type of reset")

    parser.add_option("-R", "--reset-timeout",
                      dest="forced_reset_timeout",
                      metavar="NUMBER",
                      type="int",
                      help="When forcing a reset using option -r you can set up after reset timeout in seconds")

    (options, _) = parser.parse_args()
    return options