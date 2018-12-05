"""Agilent N8300A instrument driver as signal generator for Station Cal

:Reference Code: WNBU N8300A labview driver
:Copyright: 2017, Cisco Systems
:Author: Li Kevin
"""
import time
from ...scpi import scpibase


class Driver(scpibase.Driver):
    """Agilent N8300A instrument driver as signal generator for Station Cal."""

    # configuration for RF output
    def configure_port_num(self, port=1):
        """Configures port number to use.

        :param int port: specifies the port number to use, 1, 2, 3, 4
        :return: None
        """
        self.write(":SOUR:PORT:SEL PRIM;")
        self.write(":SOUR:PORT:PRIM RFIO%d" % int(port))

    def enable_CWT_output(self, frequency=2412, power=-10):
        """Enable CW tone output.

        :param int frequency: frequency in Mhz
        :param float power: specifies the power level of the generated RF signal in dBm
        :return: None
        """
        self.write(":SOUR:STOP")
        time.sleep(1)
        self.write(":SENS:FREQ:CENT %d MHz" % int(frequency))
        self.write(":SOUR:CWT %d , 0.0" % float(power))

    def disable_CWT_output(self):
        """disable CW tone output.

        :return: None
        """
        self.write(":SOUR:STOP")
        self.write(":SOUR:DEC OFF")
