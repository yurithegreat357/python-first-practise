import time
import logging
from driver.agilent.wireless import ag4010a_bt
from os import path
log = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s', level=logging.INFO)
N4010A_sim_file=path.dirname(path.dirname(__file__))+'/sim/agn4010a_bt_sim.json'

# specify instrument resource name
resource_name = "TCPIP0::192.168.100.254::inst0::INSTR"

# Step 1: initialize
log.info("Step 1: Initialize the instrument")
instr = ag4010a_bt.Driver(resource_name, simulate=False, sim_file=N4010A_sim_file, reset=True, query_instr_status=True, opc_check=False, logging_flag=True)
log.info("Instrument ID: %s" % instr.id)

#Test setup
log.info('Step 2:Test plan act 11')
instr.activate_test_plan(plans=11)

log.info('Step 3:Initialize the machine')
instr.system_preset()

log.info('Step 4:Set up the test set Bluetooth address')
instr.set_bluetooth_address(address='#hABABABABABAB')

log.info('Step 5:Set up the frequecy reference')
instr.set_freq_ref(source='EXT')

log.info("Step 6:Set power level")
instr.set_link_tx_power_level(level=-40.0)

log.info("Step 7:Set power class")
instr.set_eut_power_class(pwr_class='PC1', limit_range=None, limit=0, occurrence=0)

log.info('Step 8:Set expected tx power class')
instr.set_link_rx_power_range(rang=25)

log.info('Step 9:Set up the EUT Bluetooth address')
instr.set_bluetooth_address(address='#hABABABABABAB')

log.info("Step 10:Set up operating mode")
instr.select_operating_mode(mode= 'RFA', freq=2441, bandwidth=1.31e6,power=5)

log.info("Step 11:Set loss compensation")
instr.set_loss_compensation(state=0)

log.info("Step 12:Set Compensation value")
instr.set_loss_para(val=0)
#RF Analyzer
log.info("Step 13:Set operating mode")
value = instr.set_operating_mode(mode='RFA')
log.info(value)

log.info("Step 14:Set frequency")
instr.set_frequency(freq=2441)

log.info("Step 15:Set Bandwidth")
instr.set_bwidth(bandwidth=1.31e6)

log.info("Step 16:Set power range")
instr.set_power_range(power=5)

log.info("Step 17:Set acquisition time")
instr.set_aqui_time(time=625e-6)
#RF Analyzer

#RF generator
log.info("Step 18:Set operation mode")
instr.set_operating_mode(mode='RFG')

log.info("Step 19:Set CW tone frequency")
instr.set_cw_fixed_freq(freq=2441)

log.info("Step 20:Set power level")
instr.set_power_level(level=-40)

log.info("Step 21:set power class")
instr.set_eut_power_class(pwr_class='PC1', limit_range=None, limit=0, occurrence=0)

log.info("Step 22:Set power range")
instr.set_power_range(power=5)

log.info("Step 23:Set Output state")
instr.set_output_state(state=1)
#RF generator

log.info('Step 24:Set link type')
instr.set_link_type(link_type='TEST')

#
#CVEBU BT EDR fast Test sequence
instr.system_preset()
log.info('Step 25:Test plan act 11')
instr.activate_test_plan(plans=1)
instr.run_current_sequence()

log.info('Step 26:Query the sequence status')
log.info('RPOW : {}'.format(instr.get_seq_status('RPOW')))
log.info('FSM : {}'.format(instr.get_seq_status('FSM')))
log.info('DPEN : {}'.format(instr.get_seq_status('DPEN')))
log.info('ESEN : {}'.format(instr.get_seq_status('ESEN')))

log.info("Step 27:Disconnect the DUT device")
instr.disconnect_test_set()

log.info("Step 28:Get bt address")
log.info('address is {}'.format(instr.query_bt_address()))

log.info("Step 29:Query bt test result")
log.info("Relative power result: {}".format(instr.get_relative_power_result()))
log.info("Frequency stability result: {}".format(instr.get_freq_stablity_result()))
log.info("Edr sensitivity result :{}".format(instr.get_edr_sensitivity_result()))
log.info("DPSK relative result : {}".format(instr.get_dpsk_relative_power_result()))
log.info("GFSK relative power result {}".format(instr.get_gfsk_relative_power()))
log.info("EDR relative power : {}".format(instr.get_edr_relative_power_result()))
log.info("Freq stability devm percent {}".format(instr.get_freq_stablity_devm_percent()))
log.info("DEVM peak :{}".format(instr.get_freq_stablity_devm_peak()))
log.info("DEVM rms :{}".format(instr.get_freq_stablity_devm_rms()))

#CVEBU BT