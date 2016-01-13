"""
mbed SDK
Copyright (c) 2011-2015 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author: Przemyslaw Wirkus <Przemyslaw.Wirkus@arm.com>
"""

import os
import jnprog
from host_test_plugins import HostTestPluginBase


class HostTestPluginCopyMethod_JN51xx(HostTestPluginBase):

    # Plugin interface
    name = 'HostTestPluginCopyMethod_JN51xx'
    type = 'CopyMethod'
    capabilities = ['jn51xx']
    required_parameters = ['image_path', 'serial']

    def is_os_supported(self, os_name=None):
        """! In this implementation this plugin only is supporeted under Windows machines
        """
        # If no OS name provided use host OS name
        if not os_name:
            os_name = self.mbed_os_support()

        # This plugin only works on Windows
        if os_name and os_name.startswith('Windows'):
            return True
        return False

    def setup(self, *args, **kwargs):
        """! Configure plugin, this function should be called before plugin execute() method is used.
        """
        self.JN51XX_PROGRAMMER = 'JN51xxProgrammer.exe'
        return True

    def execute(self, capability, *args, **kwargs):
        """! Executes capability by name

        @param capability Capability name
        @param args Additional arguments
        @param kwargs Additional arguments

        @details Each capability e.g. may directly just call some command line program or execute building pythonic function

        @return Capability call return value
        """
        result = False
        if self.check_parameters(capability, *args, **kwargs) is True:
            image_path = os.path.normpath(kwargs['image_path'])
            serial_port = kwargs['serial']
            if capability == 'jn51xx':
                # Example:
                # JN51xxProgrammer.exe -s COM15 -f <file> -V0
                # cmd = [self.JN51XX_PROGRAMMER,
                       # '-s', serial_port,
                       # '-f', image_path,
                       # '-V0'
                      # ]
                # result = self.run_command(cmd)
                # print "My Programing"
                ctx = jnprog.Programmer()

                # Open connection at the bootloader default of 38400
                conn = jnprog.Connection(serial_port, jnprog.CONNECT_SERIAL)
                conn.details.serial.baud_rate = 38400
                ctx.connection_open(conn)

                # Retrieve the chip details
                ctx.chip_get_details()
                
                # Up the baudrate to 1M once connected
                conn.details.serial.baud_rate = 1000000;
                ctx.connection_update(conn)
                    
                # Load the received image data
                ctx.firmware_open(image_path)

                # print ctx.chip_details.chip_name
                
                #print "Programming device...",
                # Program the image
                ctx.flash_program()

                # Erase the eeprom
                ctx.eeprom_erase(jnprog.ERASE_EEPROM_ALL)
                
                # Close the connection without resetting the device
                ctx.flags.auto_program_reset = False;
                ctx.connection_close()

        return True


def load_plugin():
    """ Returns plugin available in this module
    """
    return HostTestPluginCopyMethod_JN51xx()
