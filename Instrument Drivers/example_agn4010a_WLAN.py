import time
import matplotlib.pyplot as plt
import logging
from driver.agilent.wireless import ag4010a_wlan
from os import path
log = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s', level=logging.INFO)

# specify instrument resource name
resource_name = "TCPIP0::192.168.100.254::inst0::INSTR"
N4010A_sim_file=path.dirname(path.dirname(__file__))+'/sim/agn4010a_wlan_sim.json'
# Step 1: initialize
log.info("Step 1: Initialize the instrument")
instr = ag4010a_wlan.Driver(resource_name, simulate=False, sim_file=N4010A_sim_file, reset=True, query_instr_status=True, opc_check=False, logging_flag=True)

log.info("Instrument ID: %s" % instr.id)
log.info('Initiating instrument')
instr.wlan_test_initiate()
log.info('Step 2:Setting up loss compensation')
instr.set_loss_compensation_analyzer()
log.info('Step 3:Seting wlan mode')
instr.set_wlan_mode()
log.info('Step 4:Setting up 802.11a')
instr.set_wlan_80211a()
log.info('Step 5:Measuring average power')
aver_pow, peak_pwr = instr.measure_average_power()
log.info('The average power is {0}, Peak power is {1}'.format(aver_pow, peak_pwr))
log.info('Step 6:Measuring spectral mask')
a, b, c= instr.measure_spectral_mask()
log.info('The spectral points is {0}, the max data is {1}, min is {2}'.format(a, b, c))
plt.plot(c)
plt.show()

log.info("Step 7: Measure frequency error, EVM")
freq_error , raw = instr.measure_freq_error()
log.info('The frequency error is {0}, the raw data is {1}'.format(freq_error, raw))
symbol_clock_frequency_error, IQ_quad_error, Frequency_error, RMS_EVM, raw_data = instr.measure_demod11a()
log.info(symbol_clock_frequency_error)
log.info(IQ_quad_error)
log.info(Frequency_error)
log.info(RMS_EVM)
log.info(raw_data)

log.info('Step 8:AWG run sequence file')
instr.awg_run_sequence()
instr.halt_awg_operation()
log.info('Step 9:AWG run CW tone')
instr.awg_cw_tone()
instr.halt_awg_operation()
log.info('Step 10:AWG run wavefrom file')
instr.awg_run_waveform_file()
instr.halt_awg_operation()