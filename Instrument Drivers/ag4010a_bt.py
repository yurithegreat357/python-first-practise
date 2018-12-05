"""Agilent N4010A instrument driver for Bluetooth measurement

:Reference Code: Agilent N4010A Bluetooth set up manual
:Copyright: 2018, Cisco Systems
:Author: Yuri Du
:remarks:
RF analyzer set up sequences:
1:Set operating mode (RFA)
2:set frequency
3:set bandwidth
4:set input power
5:Set aquisition time

RF generator set up sequences
1:Set operation mode(RFG)
2:Set frequency
3:Set output power
4:Set output state
5:Set reference

Test set set up sequences:
1.Reset the machine
2.Set up Bluetooth address
3:Set the 10MHz frequency reference source
4:Set the test transmit power level.
5:Set the EUT power class.
6:Set the security level
7:Set Page scan repetition mode
8:Set expected input power
9:Set EUT's Bluetooth address
10:Set the test set Operation mode
"""
from driver.scpi import scpibase


class Driver(scpibase.Driver):
    def __init__(self, *args, **kwargs):
        super(Driver, self).__init__(*args, **kwargs)
        self.system_preset()
    def system_preset(self):
        """
        This command performs a full preset of the Test Set. This is the remote equivalent of pressing the Preset key
        on the front panel of the Test Set. All parameters are set to their default values and any sequence running is
        aborted and the link is disconnected and returned to idle.
        :return:
        """
        self.write('*RST')
        self.write('SYST:PRES')

    def sequence_loop_set(self, loop_mode='SING'):
        """
        Use this command to specify the repetition conditions of the test sequence.
        :param loop_mode: SINGle: the sequence runs once before stopping.
                          CONTinuous: the sequence runs continuously until a stop condition is reached.
                          An example of a stop condition if you send the ABORt command.
                          FIXed: the sequence runs a fixed number of times as specified by
                          the SEQuence:LOOP:NUMBer command.
        :return: The current setting.
        """
        self.setup_sequence(command='SEQuence:LOOP ', val=loop_mode, list_val=['SING', 'CONT', 'FIX'])
        return self.query('SEQuence:LOOP?')

    def sequence_abort(self):
        """
        Use this command to halt the sequence process.
        :return:
        """
        self.write('ABOR')

    def activate_test_plan(self, plans=1):
        """
        Use this command to activate a test plan sequence.
        The Test Plans are sets of parallel tests chosen and structured to optimize test time.
        :param plans:range[1, 8]
        1: Single-Slot Sensitivity, Output Power ,ICFT
        2: Multi-Slot Sensitivity, Output Power, ICFT
        3: Single-Slot Sensitivity, Output Power
        4: Multi-Slot Sensitivity, Output Power
        5: Multi-Slot Sensitivity, ICFT
        6: Mod Char, Carrier Drift, Single-Slot Sensitivity, Output Power, ICFT
        7: Mod Char, Carrier Drift1, Multi-Slot Sensitivity, Output Power, ICFT
        8: Mod Char1, Single-Slot Sensitivity, Output Power, ICFT
        :return: the current active test plan sequence.
        """
        self.setup_sequence(command='SEQ:TEST:ACT ', val=plans, datatype='int', lowlimit=1, highlimit=12)
        return self.query('SEQ:TEST:ACT?')

    def run_current_sequence(self):
        """
        Use this command to run the current test sequence.
        The currently active test sequence is specified by the *RCL command.
        :return:
        """
        self.write('INIT')

    def select_operating_mode(self, mode='RFA', freq=2441, bandwidth=1.31e6, power=5, level=None, time=625e-6,
                              power_class=None, limit_range=None, limit_val=None, occurance=None, state=None,
                              link_mode=None):
        """
        This is a node function for setting up the test sequence
        :param mode: "LINK"- Bluetooth Test mode, and Normal mode SCO and ACL links supported.
                     "RFA" -RF Analyzer - use the Test Set as a tuned receiver to measure frequency and amplitude.
                     "RFG" - RF Generator - use the Test Set to generate a CW signal of specified frequency and
                     amplitude.
        :param freq: frequency of the RF Analyzer.[2401, 2480] MHz
                     frequency of RF Generator range[2402, 2480] MHz
        :param bandwidth:(Available in RFA mode) Use this command to set the RF Analyzer Bandwidth. range[1.3MHz, 5MHz]
        :param power: Use this command to set the power range. Set in intervals of 5 dBm. range[-60dBm, 25dBm]
        :param level: (Available in RFG mode)Use this command to specify the power level required. range[-95, 0]dBm
        :param time: (Available in RFA mode)Use this command to set the Acquisition Time in seconds.range[100us, 5.24ms]
        :param power_class: (Available in RFG mode)Use this command to determine the power class of the EUT.
                            Limit is available if class is set to PC1. keywords['PC1', 'PC2', PC3']
        :param limit_range: (Available in RFG mode) keywords['lower', 'higher']
        :param limit_val: (Available in RFG mode)range [-100, 100]dBm Defines the average power lower limit for the
                            output power test
        :param occurance: (Available in RFG mode) range[0, 10] Since multiple occurrences of a test can appear in a
        sequence this optional parameter allows you to define which occurrence of the test you are specifying
        :param state: (Available in RFG mode) keyword[1\ON 0\OFF]This command switches the RF Output State in
                       the RF Generator on and off.
        :param link_mode: (Available in LINK mode)the type of connection to use when in Link mode.
                           keywords['ACL', 'SCO', 'TEST]

        :return:
        """
        self.set_operating_mode(mode=mode)
        if mode is 'RFA':
            self.set_frequency(freq=freq)
            self.set_bwidth(bandwidth=bandwidth)
            self.set_power_range(power=power)
            self.set_aqui_time(time=time)
        if mode is 'RFG':
            self.set_cw_fixed_freq(freq=freq)
            self.set_power_level(level=level)
            self.set_eut_power_class(pwr_class=power_class, limit_range=limit_range, limit=limit_val,
                                     occurrence=occurance)
            self.set_power_range(power=power)
            self.set_output_state(state=state)
        if mode is 'LINK':
            self.set_link_type(link_type=link_mode)

    def set_link_type(self, link_type='TEST'):
        """
        Use this command to specify the type of connection to use when in Link mode.
        :param link_type: ACL: asynchronous connectionless method. Used for data communication.
                     SCO: synchronous connection oriented method. User for voice/audio communication.
                     TESTmode: provides access to the tests defined in the Bluetooth RF test specification.


        :return: Your current setting
        """
        self.setup_sequence(command='LINK:TYPE ', val=link_type, list_val=['ACL', 'SCO', 'TEST'])
        return self.query('LINK:TYPE?')

    def toggle_test_limit(self, state=0):
        """
        Use this command to enable or disable limit testing for all tests in the current test sequence. The command
        overrides any previously specified settings for individual tests. If required, specific test limit tests must
        be enabled or disabled after issuing this command. The current test sequence is specified by
        the MMEM:LOAD:SEQuence command.
        :param state: 0 | OFF: limit testing is disabled.
                      1 | ON: limit testing is enabled.
        :return:
        """
        self.setup_sequence(command='CALC:SEQ:LIM:STAT ', val=state, list_val=[0, 1, 'ON', 'OFF'])

    def clear_sequence(self):
        result = self.query('LINK:TYPE?')
        if result == 'TEST':
            self.write('SEQ:CLE')
        else:
            raise Exception('The result is {}, Plze use set_link_type to change it to Test mode'.format(result))

    def set_bluetooth_address(self, address='#hABABABABABAB'):
        """
        Use this command to set the Test Set's Bluetooth device address, in hexadecimal.
        The numeric value parameter can accept non-decimal numeric program data and is
        not restricted to hexadecimal. However, the query response format is hexadecimal.
        :param address: Sets the Test Set's Bluetooth device address in hex.
        :return: Returns the current value.
        """
        self.write('LINK:STE:BDAD {}'.format(address))
        return self.query('LINK:STE:BDAD?')

    def get_board_bluetooth_address(self):
        """
        Returns the board current bluetooth address.
        :return:
        """
        return self.query('LINK:STE:BDAD?')

    def get_total_bt_device(self):
        """
        Use this query only command to
        return the total number of Bluetooth device addresses that have responded to the inquiry procedure.
        :return:
        """
        return self.query('LINK:INQ:BDAD:COUN?')

    def find_bt_address(self):
        """
        use this command to find existing bluetooth address. Use select_bt_address to use the preferred one
        :return: Returns a list of Bluetooth device addresses that responded to the inquiry procedure.
                 For example, #H00AB2C11EF87,#H00BDBD437254AC.
        """
        self.write('LINK:CONT:INQ:IMM')
        return self.query('LINK:INQ:BDAD:RESP?')

    def select_bt_address(self, addr='#hABABABABABAB'):
        """
        Use this command to set the EUT Bluetooth device address of the device to be tested.
        The value can also be obtained from the EUT during the inquiry procedure.
        Specifying the EUT to be tested using this command is quicker than obtaining it from an inquiry.
        :param addr: hex bluetooth address
        :return:
        """
        self.write('LINK:EUT:BDAD {}'.format(addr))

    def query_bt_address(self):
        """
        Return the bt address that is being set
        :return:
        """
        return self.query('LINK:EUT:BDAD?')
    # CVEBU

    def get_seq_status(self, seq='RPOW'):
        """
        Use this query only command to return the count of the number of times the test has completed.
        :param seq: keywords:CFDRift: Carrier Frequency Drift test
                             ICFT: Initial Carrier Frequency Tolerance test
                             MCHar: Modulation Characteristics test
                             MILevel: Maximum input Level test
                             MSENsitivity: Sensitivity test
                             OPOWer: Output Power test
                             PCONtrol: Power Control test
                             PER: Packet Error Rate test
                             SSENsitivity: Sensitivity test
                             BFPerform: EDR BER Floor Performance test
                             DPENcoding: EDR Differential Phase Encoding test
                             EMILevel: EDR Maximum Input Level test
                             ESENsitivity: EDR Sensitivity test
                             FSMaccuracy: EDR Frequency Stability and Modulation Accuracy test
                             GTIMe: EDR Guard Time test
                             RPOWer: EDR Relative Transmit Power test
        :return: 0: the test has not yet run, or is not part of the current test sequence.
                 1 or greater: the number of times the test completed.

        """
        self.utility_range_check(data_type=type('str'), value=seq, list_option=["CFDR", "ICFT", "MCH", "MIL", "MSEN",
                                                                                "OPOW", "PCON", "PER", "SSEN", "BFP",
                                                                                "DPEN", "EMIL", "ESEN", "FSM", "GTIM",
                                                                                "RPOW"])
        return self.query('SEQ:DONE? {}'.format(seq))

    def set_fix_corr_loss(self, value=20):
        """
        Use this command to specify a fixed loss compensation value.
        The parameter may include a unit terminator otherwise the units default to dB.
        :param value: range[-50, 40]dB
        :return: the current setting
        """
        self.setup_sequence(command='SENS:CORR:LOSS:FIX ', val=value, datatype='int', lowlimit=-50, highlimit=40)
        return self.query('SENS:CORR:LOSS:FIX?')

    def disconnect_test_set(self):
        """
        Use this command to disconnect the Test Set from the EUT. The command only applies when a link has been
        established between the Test Set and EUT. A status bit is used to indicate the status of the link.
        :return:
        """
        self.write('LINK:CONT:DISC:IMM')

    def get_relative_power_result(self):
        """
        Use this query-only command to determine the pass/fail status of the Relative Power test.
        :return: 0 or 1 (PASS/FAIL)
        """
        return self.query('CALC:RPOW:LIM:FAIL?')

    def get_freq_stablity_result(self):
        """
        Use this query-only command to determine the pass/fail status of
        the Frequency Stability and Modulation Accuracy test.
        :return: 0 or 1 (PASS/FAIL)
        """
        return self.query('CALC:FSM:LIM:FAIL?')

    def get_edr_sensitivity_result(self):
        """
        Use this query-only command to determine the pass/fail status of the EDR Sensitivity test.
        :return: 0 or 1 (PASS/FAIL)
        """
        return self.query('CALC:ESEN:LIM:FAIL?')

    def get_dpsk_relative_power_result(self):
        """
        Use this query to obtain the high EDR DPSK relative power test results.
        :return:
        """
        return self.query('FETC:RPOW:HIGH:DPSK?')

    def get_gfsk_relative_power(self):
        """
        Use this query to obtain the low EDR GFSK relative power test results.
        :return:
        """
        return self.query('FETC:RPOW:HIGH:GFSK?', delay=2)

    def get_edr_relative_power_result(self):
        """
        Use this query to obtain the high EDR relative power test results
        :return:
        """
        return self.query('FETC:RPOW:HIGH:REL?')

    def get_freq_stablity_devm_percent(self):
        """
        Use this query to obtain the result of the Frequency Stability and Modulation Accuracy Percentile DEVM test.
        :return:
        """
        return self.query('FETC:FSM:DEVM:NNP?')

    def get_freq_stablity_devm_peak(self):
        """
        Use this query to obtain the result of the Frequency Stability and Modulation Accuracy Peak DEVM test.
        :return:
        """
        return self.query('FETC:FSM:DEVM:PEAK?')

    def get_freq_stablity_devm_rms(self):
        """
        Use this query to obtain the result of the Frequency Stability and Modulation Accuracy RMS DEVM test.
        :return:
        """
        return self.query('FETC:FSM:DEVM:RMS?')

    def get_freq_stablity_block_freq_error(self):
        """
        Use this query to obtain the result of the Frequency Stability and Modulation Accuracy
        Block Frequency Error test.
        :return:
        """
        return self.query('FETC:FSM:FERR:BLOC?')

    def get_freq_stablity_initial_freq_error(self):
        """
        Use this query to obtain the result of the Frequency Stability and Modulation
        Accuracy Initial Frequency Error test.
        :return:
        """
        return self.query('FETC:FSM:FERR:INIT?')

    def get_freq_stablity_freq_total(self):
        """
        Use this query to obtain the result of the Frequency Stability and Modulation Accuracy Initial Frequency
        Error plus Block Frequency Error test.
        :return:
        """
        return self.query('FETC:FSM:FERR:TOT?')

    def get_ber_sensitivity_error_rate(self):
        """
        Use this query to obtain the result of the EDR Sensitivity bit error rate test.
        :return:
        """
        return self.query('FETC:ESEN:BER?')

    def get_edr_error_bit(self):
        """
        Use this query to obtain the number of error bits for the EDR Sensitivity test.
        :return:
        """
        return self.query('FETC:ESEN:EBIT?')

    def get_edr_error_pack(self):
        """
        Use this query to obtain the number of error packets for the EDR Sensitivity test.
        :return:
        """
        return self.query('FETC:ESEN:EPAC?')

    def get_der_miss_packet(self):
        """
        Use this query to obtain the number of missing packets for the EDR Sensitivity test.
        :return:
        """
        return self.query('FETC:ESEN:MPAC?')
    # CVEBU

    def set_operating_mode(self, mode="LINK"):
        """
        Use this command to specify the operating mode. Firmware version A.02.00.11 or later is required to
        support this command.
        :param mode:
              "LINK"- Bluetooth Test mode, and Normal mode SCO and ACL links supported.
              "RFA" -RF Analyzer - use the Test Set as a tuned receiver to measure frequency and amplitude.
              "RFG" - RF Generator - use the Test Set to generate a CW signal of specified frequency and amplitude.
        :return: 'LINK', RFA' or 'RFG' (Depend on the mode you set)
        """
        self.utility_range_check(data_type=type('str'), value=mode, list_option=['LINK', 'RFA', 'RFG'])
        self.write('INST:SEL \"{}\"'.format(mode))
        return self.query('INST?')

    def set_frequency(self, freq=2441):
        """
        Use this command to change the frequency of the RF Analyzer.
        :param freq: range[2401, 2480] MHz
        :return: +0,"No error" if pass
        """
        self.setup_sequence(command='SENS:FREQ:CENT ', val=freq, datatype='int',
                            lowlimit=2402, highlimit=2480)
        return self.system_error()

    def set_link_tx_power_level(self, level=-40.0):
        """
        Use this command to set the Test Set's transmit power level for the default transmit power used for inquiry
        and page procedures, and when maintaining the link when no sequence is running.
        :param level: range [-90, 0] dBm
        :return: your current setting
        """
        self.setup_sequence(command='LINK:TX:POW:LEV ', val=level, datatype='float', lowlimit=-90.0, highlimit=0.0)
        return self.query('LINK:TX:POW:LEV?')

    def set_bwidth(self, bandwidth=1.31e6):
        """
        Use this command to set the RF Analyzer Bandwidth.
        :param bandwidth: range[1.3MHz, 5MHz]
        :return: +0,"No error" if pass
        """
        self.setup_sequence(command='SENS:BWID ', datatype='float', val=bandwidth,
                            lowlimit=1.3e6, highlimit=5e6)
        return self.system_error()

    def set_power_range(self, power=5):
        """
        Use this command to set the power range. Set in intervals of 5 dBm.
        :param power: range[-60dBm, 25dBm]
        :return: +0,"No error" if pass
        """
        self.setup_sequence(command='SENS:POW:RANG ', val=power, datatype='int',
                            lowlimit=-60, highlimit=25)
        return self.system_error()

    def set_aqui_time(self, time=625e-6):
        """
        Use this command to set the Acquisition Time of the RF Analyzer. Time is entered in seconds.
        :param time:  range[100us, 5.24ms] second(s)
        :return: +0,"No error" if pass
        """
        self.setup_sequence(command='SENS:SWE:TIME ', val=time, datatype='float',
                            lowlimit=100e-6, highlimit=5.24e-3)
        return self.system_error()

    def set_cw_fixed_freq(self, freq=2441):
        """
        Use this command to specify the frequency required. This command is used when in RF Generator mode
        :param freq: range[2402, 2480] MHz
        :return: +0,"No error" if pass
        """
        self.setup_sequence(command='SOURce2:FREQuency:CW ', val=freq, datatype='int',
                            lowlimit=2402, highlimit=2480)

    def set_link_rx_power_range(self, rang=25):
        """
        Use this command to set the expected input power.  This is the expected power when the link is first established
        before any tests are started, and in general when no particular test is being performed.
        :param rang: range[-70, 25]dBm
        :return: your current setting
        """
        self.setup_sequence(command='LINK:RX:POW:RANG ', val=rang, datatype='int', lowlimit=-70, highlimit=25)
        return self.query('LINK:RX:POW:RANG?')

    def set_power_level(self, level=-40):
        """
        Use this command to specify the power level required. This command is used when in RF Generator mode.
        :param level: range[-95, 0]dBm
        :return:
        """
        self.setup_sequence(command='SOUR:POW:LEV ', val=level, datatype='int', lowlimit=-95, highlimit=0)

    def set_output_state(self, state=1):
        """
        This command switches the RF Output State in the RF Generator on and off.
        :param state: 1\ON 0\OFF
        :return:
        """
        self.setup_sequence(command='OUTP:STAT ', val=state, list_val=[0, 1, 'ON', 'OFF'])

    def set_freq_ref(self, source='INT'):
        """
        Use this command to set the frequency reference source.
        :param source: INTernal\INT, EXTernal\EXT
        :return: the current setting(EXT, INT)
        """
        self.setup_sequence(command='SENS:ROSC:SOUR ', val=source, list_val=['INT', 'EXT', 'EXTernal', 'INTernal'])
        return self.query('SENS:ROSC:SOUR?')

    def set_repition_mode(self, mode='R1'):
        """
        Use this to set a Page Scan Repetition Mode for the Test Set that is appropriate for the EUTs you are testing.
        This helps ensure consistent and repeatable connection to the EUTs during test.
        :param mode: R0: Mode zero
                     R1: Mode one
                     R2: Mode two
        :return: The current setting
        """
        self.setup_sequence(command='LINK:EUT:PRSM ', val=mode, list_val=['R0', 'R1', 'R2'])
        return self.query('LINK:EUT:PRSM?')

    def set_eut_power_class(self, pwr_class='PC1', limit_range='lower', limit=1, occurrence=1):
        """
        Use this command to determine the power class of the EUT.
        Limit is available if class is set to PC1
        :param pwr_class: ['PC1', 'PC2', PC3']
        remark:Changing the EUT's Power Class, while in Testmode,
        changes the Input Power level of any added test sequence after the power class is changed.
        Previous tests in the sequence remain at their original power level
        PC1: changes the Input Power level to 25 dBm.
        PC2: changes the Input Power level to 10 dBm.
        PC3: changes the Input Power level to 5 dBm.
        :param limit_range: ['lower', 'higher']
        :param limit: range [-100, 100]dBm
        Defines the average power lower limit for the output power test.
        This parameter may include a unit terminator otherwise the units default to dBm.
        :param occurrence: range[0, 10]Since multiple occurrences of a test can appear in a sequence this optional
        parameter allows you to define which occurrence of the test you are specifying the limit for
        :return:
        """
        self.setup_sequence(command='LINK:EUT:PCL ', val=pwr_class, list_val=['PC1', 'PC2', 'PC3'])
        if pwr_class is 'PC1' and limit_range is 'lower':
            if occurrence is 0:
                self.setup_sequence(command='CALC:OPOW:LIM:AVER:LOW ', val=limit, datatype='int',
                                    lowlimit=-100, highlimit=100)
                return self.query('CALC:OPOW:LIM:AVER:LOW?')
            else:
                self.utility_range_check(data_type=type(6), value=limit, low_limit=-100, high_limit=100)
                self.write('CALC:OPOW:LIM:AVER:LOW {0},{1}'.format(limit, occurrence))
                return self.query('CALC:OPOW:LIM:AVER:LOW? {}'.format(occurrence))
        elif pwr_class is 'PC1' and limit_range is 'higher':
            if occurrence is 0:
                self.setup_sequence(command='CALC:PCON:LIM:AVER:UPP ', val=limit, datatype='int',
                                    lowlimit=-100, highlimit=100)
                return self.query('CALC:OPOW:LIM:AVER:UP?')
            else:
                self.utility_range_check(data_type=type(6), value=limit, low_limit=-100, high_limit=100)
                self.write('CALC:OPOW:LIM:AVER:UP {0},{1}'.format(limit, occurrence))
                return self.query('CALC:OPOW:LIM:AVER:UP? {}'.format(occurrence))
        else:
            return self.query('LINK:EUT:PCL?')

    def set_loss_compensation(self, state=0):
        """
        Use this command to set loss compensation on or off. When set on, loss values are applied
        to the current test sequence.
        :param state: ['0', '1' , 'ON', 'OFF']
        :return: 0 or 1 (0 ----OFF, 1-----ON)
        """
        self.setup_sequence(command='SENS:CORR:LOSS ', val=state, list_val=[0, 1, 'ON', 'OFF'])
        return self.query('SENS:CORR:LOSS?')

    def set_loss_para(self, val=0):
        """
        Use this command to specify a fixed loss compensation value. The parameter may include
        a unit terminator otherwise the units default to dB.
        :param val: range[-50 , 40] dB
        :return: the current setting
        """
        self.setup_sequence(command='SENS:CORR:LOSS:FIX ', datatype='int', val=val, lowlimit=-40, highlimit=50)
        return self.query('SENS:CORR:LOSS:FIX?')

    def setup_sequence(self, command, val, datatype=None, list_val=None, lowlimit=None, highlimit=None):
        """
        A quick set up function for instrument setup.
        :param command: The command that being sent to machine
        :param val: The value following in the command
        :param datatype: 'int', 'float' or blank(if it's a str type)
        :param list_val: if the value range is a list, put the list into it.
        :param lowlimit: The lower limit of the value
        :param highlimit: The highest value that is allowed.
        :return:
        """
        if lowlimit and datatype is 'int':
            self.utility_range_check(value=val, data_type=type(6), low_limit=lowlimit, high_limit=highlimit)
            self.write(command+str(val))
        elif lowlimit and datatype is 'float':
            self.utility_range_check(value=val, data_type=type(0.1), low_limit=lowlimit, high_limit=highlimit)
            self.write(command+str(val))
        elif list_val:
            self.utility_range_check(value=val, data_type=type(str), list_option=list_val)
            self.write(command+str(val))
        else:
            self.write(command+str(val))

    def set_link_config_default(self):
        """
        Use this command to reset all the LINK:CONFigure parameters for the currently active test
        to their default values.
        :return:
        """
        self.write('LINK:CONF:DEF')

    def get_catalog(self):
        """
        This command is used to query the available Test Set operating modes. Firmware version A.02.00.11 or later is
        required to support this command.
        :return: Returns the available operating modes
        """
        self.query('INST:CAT?')

    def system_error(self):
        """
        Detect whether the input value or syntax is legal.
        :return: return error code and reason if detects anomaly.
        """
        check = self.query('SYST:ERR?')
        if check is not '+0,"No error"':
            return check
        else:
            return check
