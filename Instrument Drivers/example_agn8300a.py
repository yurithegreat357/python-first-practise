"""This is an example of how to use Agilent N8300A to generate a CW signal and make frequency sweep

The example uses the driver level functions to init, configure, measure and cleanup.

- Step 1: Initialize the instrument
- Step 2: Configure channel parameters (voltage, current and so on)
- Step 3: Measure output voltage and current
- Step 4: Cleanup and turn off output

:Copyright: 2017, Cisco Systems
:Author: Li Kevin
"""
import time
import logging
from apollo.libs.te_libs.instrument.trunk.driver.agilent.wireless import ag8300

log = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s', level=logging.INFO)

# specify instrument resource name
resource_name = "TCPIP0::10.1.1.8::inst0::INSTR"

# Step 1: initialize
log.info("Step 1: Initialize the instrument")
instr = ag8300.Driver(resource_name, reset=True, query_instr_status=True, opc_check=True, logging_flag=True)
log.info("Instrument ID: %s" % instr.id)


log.info("Step 2: Generate a CW RF signal with frequency 2412MHz and power -10dBm")
instr.disable_CWT_output()
instr.configure_port_num(port=1)
instr.enable_CWT_output(frequency=2412, power=-10)
time.sleep(30)

log.info("Step 3: Cleanup and Close")
instr.disable_CWT_output()
instr.close()

