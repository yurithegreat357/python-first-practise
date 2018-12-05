"""Agilent N4010A instrument driver for WLAN measurement

:Reference Code: Agilent N4010A WLAN test set up manual
:Copyright: 2018, Cisco Systems
:Author: Yuri Du
:remarks: None
"""


from driver.scpi import scpibase
import matplotlib.pyplot as plt
import ctypes
import pyvisa
import string

class Driver(scpibase.Driver):
    def __init__(self, *args, **kwargs):
        super(Driver, self).__init__(*args, **kwargs)
        self.data_dict={'freq':2412000000, 'equ_type':'Normal', 'expected_sig_bwdith':'Bandwidth_20MHz',
                        'power_range':20, 'max_packet':0.00259, 'trig_style':'MagLevel', 'trige_level': 0.02,
                        'max_sym':61, 'reference_level':999}

    def set_wlan_test_stats(self, freq=2412000000, equalization_type='Normal',
                            expected_signal_bwidth='Bandwidth_20MHz', power_range=20, max_packet_length= 0.000259,
                            trigger_style='MagLevel', trigger_level=0.02, max_symbols_used=61):
        """
        This is a set up function for WLAN test. All of the parameters are included. Please call this function before
        performing the test.
        :param freq: output frequency.
        :param equalization_type: keyword['Normal', 'Enhanced']
        :param expected_signal_bwidth: keyword['Bandwidth_20MHz', 'Bandwidth_40MHz']
        :param power_range: input/output power range.
        :param max_packet_length:
        :param trigger_style: keywords['FreeRun', 'MagLevel', 'External']
        :param trigger_level:
        :param max_symbols_used:
        :return:
        """
        new_dict = {'freq':freq, 'equ_type':equalization_type, 'expected_sig_bwdith':expected_signal_bwidth,
                    'power_range':power_range, 'max_packet':max_packet_length, 'trig_style':trigger_style,
                    'trige_level':trigger_level, 'max_sym':max_symbols_used}
        self.data_dict = new_dict

    def wlan_test_initiate(self, wave_form_file='WFM1:RAMP_TEST_WFM'):
        """
        This instruction is for instrument set up.
        :param freq: Input control frequency
        :return:
        """
        self.write("DIAG:HW:BAND 40.0e6")
        self.query('DIAG:HW:BAND?')
        self.query('DIAG:HW:SCAR:PRES?')
        self.write('*CLS')
        self.write('SENS:ROSC:SOUR INTernal')
        self.write(':SOURce:RADio:ARB:WAVEform \"{}\"'.format(wave_form_file))
        self.write('SOUR:RAD:ARB:STAT ON')
        self.write('*CLS')
        self.write(':SOUR:RAD:ARB:TRIG:TYPE SING')
        self.write(':DIAG:HW:FEA:ALIG:RSC 1400,3800,10,20')
        self.write(':SOUR:RAD:ARB:TRIG BUS')
        self.query('MMEMory:CATalog? "WFM1"')
        self.query('MMEMory:CATalog? "NVWFM"')
        self.query('MMEMory:CATalog? "SEQ"')
        self.write('*RST')
        self.write(':SOURce:RADio:ARB:WAVEform \"{}\"'.format(wave_form_file))
        self.write('SOUR:RAD:ARB:STAT ON')
        self.write('*CLS')
        self.write(':SOUR:RAD:ARB:TRIG:TYPE SING')
        self.write(':DIAG:HW:FEA:ALIG:RSC 1400,3800,10,20')
        self.write(':SOUR:RAD:ARB:TRIG BUS')
        self.write('*CLS')
        self.write('*CLS')
        self.write('DIAG:HW:BAND 22.0e6')
        self.write('DIAG:HW:DAP:DEC 1')
        self.write('DIAG:HW:FEA:RANG 25')
        self.write(':DIAG:HW:DAP:ACQ:TIME 0.0097')
        self.write(':DIAG:HW:DAP:TRIG:SOUR IMM')
        self.write(':DIAG:HW:DAP:TRIG:LEV -23.9791')
        self.write(':DIAG:HW:DAP:TRIG:DEL 0')
        self.write(':DIAG:HW:DAP:TRIG:IDLE 10E-06')
        self.write(':DIAG:HW:DAP:MODE generic,off')
        self.write(':DIAG:FORM:BORD NORM')
        self.write('DIAG:HW:DAP:DEC 10')
        self.write(':DIAG:HW:DAP:MEAS:RESULTS 0,0')
        self.query(':DIAG:HW:DAP:ACQ:ADC:OVER?')
        self.write('DIAG:HW:DAP:DEC 1')
        self.write('*CLS')
        self.query('STAT:QUES:INT:COND?')
        self.query('STAT:QUES:FREQ:COND?')
        self.write('*CLS')

    def set_wlan_mode(self, freq= 2412000000, wave_form_file='WFM1:RAMP_TEST_WFM'):
        self.write('*CLS')
        self.write(':SOURce:RADio:ARB:WAVEform \"{}\"'.format(wave_form_file))
        self.write('SOUR:RAD:ARB:STAT ON')
        self.write('*CLS')
        self.write(':SOUR:RAD:ARB:TRIG:TYPE SING')
        self.write(':DIAG:HW:FEA:ALIG:RSC 1400,3800,10,20')
        self.write(':SOUR:RAD:ARB:TRIG BUS')
        self.write('*CLS')
        self.write('DIAG:HW:FEA:FREQ {}'.format(freq))

    def set_loss_compensation_analyzer(self):
        self.write('SENSe:CORR:LCOM FIXed')
        self.write('SENSe:CORR:LCOM:FIXed 0')


    def set_wlan_80211a(self, max_packet_length=0.0002559):
        """
        Set up test environments for WLAN802.11a testing.
        :return:
        """
        self.write('DIAG:HW:BAND 22.0e6')
        self.write('DIAG:HW:DAP:DEC 1')
        self.write('DIAG:HW:FEA:RANG 20')
        self.write(':DIAG:HW:DAP:ACQ:TIME {}'.format(max_packet_length))
        self.write(':DIAG:HW:DAP:TRIG:SOUR BURS')
        self.write(':DIAG:HW:DAP:TRIG:SLOP POS')
        self.write(':DIAG:HW:DAP:TRIG:LEV -23.9791001300806')
        self.write(':DIAG:HW:DAP:TRIG:DEL -2E-06')
        self.write(':DIAG:HW:DAP:TRIG:IDLE 1E-06')
        self.write('*CLS')
        self.write('DIAG:HW:DAP:MODE WLAN,OFDM')
        self.write('DIAG:HW:DAP:MEAS:WLAN:OFDM:OPT 0,1,1,0,1,1')
        self.write('*CLS')
        self.write('DIAG:HW:DAP:MEAS:WLAN:OFDM:DEM 0,62,61,0,312500,1E+08,-3.125,1,0,0,0,1,0,2,0')
        self.write('DIAG:HW:DAP:MEAS:RES 0,0')
        self.query('DIAG:HW:DAP:READ:WLAN:OFDM:SCAL?')
        # self.query('DIAG:HW:DAP:FETCH:WLAN:OFDM:VECT:FLAT?') ASCII CODE error
        self.query(':DIAG:HW:DAP:ACQ:ADC:OVER?')

    def measure_average_power(self):
        """
        Measure average & peak power value
        :return: average power, peak power
        """
        self.write('*CLS')
        self.write('DIAG:HW:BAND 22.0e6')
        self.write('DIAG:HW:DAP:DEC 1')
        self.write('DIAG:HW:FEA:RANG 20')
        self.write('DIAG:HW:DAP:ACQ:TIME 0.0002559')
        self.write('DIAG:HW:DAP:TRIG:SOUR BURS')
        self.write('DIAG:HW:DAP:TRIG:SLOP POS')
        self.write('DIAG:HW:DAP:TRIG:LEV -23.9791001300806')
        self.write('DIAG:HW:DAP:TRIG:DEL 0')
        self.write('DIAG:HW:DAP:TRIG:IDLE 1E-06')
        self.write('DIAG:HW:DAP:MEAS:RESULTS 0,0')
        self.write('DIAG:HW:DAP:MODE generic,off')
        self.write('DIAG:HW:DAP:MEAS:RESULTS 1,1')
        self.write('DIAG:HW:DAP:MEAS:RESULTS 65537,1')
        average_power= self.query('DIAG:HW:DAP:READ:MISC:APOW? 1')
        peak_power = self.query('DIAG:HW:DAP:READ:MISC:PPOW? 1')
        self.write('DIAG:HW:DAP:MEAS:RESULTS 1,1')
        self.query('DIAG:HW:DAP:ACQ:ADC:OVER?')
        return average_power, peak_power

    def measure_spectral_mask(self, freq=2412000000):
        self.write('*CLS')
        self.write('DIAG:HW:BAND 22.0e6')
        self.write('DIAG:HW:DAP:DEC 1')
        self.write('DIAG:HW:FEA:RANG 20')
        self.write(':DIAG:HW:DAP:ACQ:TIME 0.0002559')
        self.write(':DIAG:HW:DAP:TRIG:SOUR BURS')
        self.write(':DIAG:HW:DAP:TRIG:SLOP POS')
        self.write(':DIAG:HW:DAP:TRIG:LEV -23.9791001300806')
        self.write(':DIAG:HW:DAP:TRIG:DEL 0')
        self.write(':DIAG:HW:DAP:TRIG:IDLE 1E-06')
        self.write('*CLS')
        self.query('DIAG:HW:BAND?')
        self.write('*CLS')
        self.write(':DIAG:HW:DAP:MODE generic,off')
        self.write(':DIAG:FORM:BORD NORM')
        self.write(':DIAG:HW:DAP:MEAS:RESULTS 0,0')
        self.write('DIAG:HW:DAP:MEAS:RESULTS 32832,1')
        self.write('DIAG:HW:DAP:MEAS:MISC:SPEC {},66000000,'
                   '100000,2,7,1,14,23.47,999,0,0'.format(freq))
        # a=self.query('DIAG:HW:DAP:READ:MISC:SPEC?')
        raw_data = self.query_raw('DIAG:HW:DAP:READ:MISC:SPECtrum?', )
        reference_points, data = self.data_processing(raw_data)
        self.query('DIAG:HW:DAP:FETCH:MISC:PK1M?')
        self.write(':DIAG:HW:DAP:MEAS:RESULTS 0,0')
        return raw_data , reference_points, data

    def measure_freq_error(self):
        self.write('*CLS')
        self.write('DIAG:HW:BAND 22.0e6')
        self.write('DIAG:HW:DAP:DEC 1')
        self.write('DIAG:HW:FEA:RANG 20')
        self.write(':DIAG:HW:DAP:ACQ:TIME 0.000305')
        self.write(':DIAG:HW:DAP:TRIG:SOUR BURS')
        self.write(':DIAG:HW:DAP:TRIG:SLOP POS')
        self.write(':DIAG:HW:DAP:TRIG:LEV -23.9791001300806')
        self.write(':DIAG:HW:DAP:TRIG:DEL -2E-06')
        self.write(':DIAG:HW:DAP:TRIG:IDLE 1E-06')
        self.write(':DIAG:HW:DAP:ACQ:TIME 0.000305')
        self.write('*CLS')
        self.write('DIAG:HW:DAP:MODE WLAN,OFDM')
        self.write('DIAG:HW:DAP:MEAS:WLAN:OFDM:OPT 0,1,1,0,1,1')
        self.write('*CLS')
        self.write('DIAG:HW:DAP:MEAS:WLAN:OFDM:DEM 0,62,61,0,312500,1E+08,-3.125,1,0,0,0,1,0,2,0')
        self.write('DIAG:HW:DAP:MEAS:RES 0,0')
        res = self.query('DIAG:HW:DAP:READ:WLAN:OFDM:SCAL?')
        res_list = res.split(',')
        raw_data = self.query_raw('DIAG:HW:DAP:FETCh:WLAN:OFDM:VECT:FLAT?')
        # self.data_processing(raw_data)
        self.query(':DIAG:HW:DAP:ACQ:ADC:OVER?')
        return res_list[0], raw_data

    def measure_demod11a(self):
        """
        Perform a demodualtion test
        :return: symbol_clock_frequency_error
                 IQ_quad_error
                 Frequency_error
                 RMS_EVM
        """
        self.write('*CLS')
        self.write('DIAG:HW:BAND 22.0e6')
        self.write('DIAG:HW:DAP:DEC 1')
        self.write('DIAG:HW:FEA:RANG 20')
        self.write(':DIAG:HW:DAP:ACQ:TIME 0.0002559')
        self.write(':DIAG:HW:DAP:TRIG:SOUR BURS')
        self.write(':DIAG:HW:DAP:TRIG:SLOP POS')
        self.write(':DIAG:HW:DAP:TRIG:LEV -23.9791001300806')
        self.write(':DIAG:HW:DAP:TRIG:DEL -2E-06')
        self.write(':DIAG:HW:DAP:TRIG:IDLE 1E-06')
        self.write(':DIAG:HW:DAP:ACQ:TIME 0.000305')
        self.write('*CLS')
        self.write('DIAG:HW:DAP:MODE WLAN,OFDM')
        self.write('DIAG:HW:DAP:MEAS:WLAN:OFDM:OPT 0,1,1,0,1,1')
        self.write('*CLS')
        self.write('DIAG:HW:DAP:MEAS:WLAN:OFDM:DEM 0,62,61,0,312500,1E+08,-3.125,1,0,0,0,1,0,2,0')
        self.write('DIAG:HW:DAP:MEAS:RES 0,0')
        res = self.query('DIAG:HW:DAP:READ:WLAN:OFDM:SCAL?')
        res_list = res.split(',')
        raw_data = self.query_raw('DIAG:HW:DAP:FETCh:WLAN:OFDM:VECT:FLAT?')
        # reference_points, trace_data = self.data_processing(raw_data)
        self.query(':DIAG:HW:DAP:ACQ:ADC:OVER?')
        return res_list[0], res_list[1], res_list[2], res_list[3], raw_data

    def data_processing(self, data):
        if str(data) == '0':
           return '0', ['0','0.25','1.5','2','3.5','4','4','4','4','3.5','2','1.5','0.25','0']
        else:
            data_digits = int(data[1])
            base_offset = 2 + data_digits
            byte_len = int(data[2:base_offset])
            points = byte_len/4
            offset = base_offset
            trace_data = []
            f= open('log.txt', 'a')
            for index in range(0, points):
                data_bin = data[offset: offset+4]
                data_hex = data_bin.encode('hex')
                data_int = int(data_hex, 16)
                trace_data.append(data_int)
                f.writelines([str(data_int), ' '])
                offset += 4
        return points, trace_data


    def awg_run_sequence(self, file_name='6OFDM_BPSK_1000B.SEQ',
                         custom_clock=40e+6, select_mode='OFDM'):
        """
        Make AWG kick start a waveform pattern by selecting a preset sequence file.
        :param file_name: A lots of sequence files. I tried my best to cover all of it.
        keywords['60FDM_BPSK_100B.SEQ', '90FDM_BPSK_100B.SEQ', '11DSS_CCK_1024B.SEQ', '12OFDM_QPSK_1000B.SEQ',
        '18OFDM_QPSK_1000B.SEQ', '24OFDM_16QAM_1000B.SEQ', '36OFDM_16QAM_1000B.SEQ', '48OFDM_64QAM_1000B.SEQ',
        '54OFDM_64QAM_1000B.SEQ']
        :param custom_clock:
        :param select_mode: keywords['OFDM', 'DSSS', 'CUSTOM']
        :return:
        """
        self.utility_range_check(data_type=type('str'), value=select_mode, list_option=['OFDM', 'DSSS', 'CUSTOM'])
        self.utility_range_check(data_type=type('str'), value=file_name, list_option=['6OFDM_BPSK_1000B.SEQ',
                                                                                      '9OFDM_BPSK_1000B.SEQ',
                                                                                      '11DSS_CCK_1024B.SEQ',
                                                                                      '12OFDM_QPSK_1000B.SEQ',
        '18OFDM_QPSK_1000B.SEQ', '24OFDM_16QAM_1000B.SEQ', '36OFDM_16QAM_1000B.SEQ', '48OFDM_64QAM_1000B.SEQ',
        '54OFDM_64QAM_1000B.SEQ'])
        if select_mode is 'CUSTOM':
            self.write('*CLS')
            self.write(':SOUR:POW:LEV:IMM:AMPL -50')
            self.write(':SOUR:RAD:ARB:CLOCK:SRAT {}'.format(custom_clock))
        else:
            self.write('*CLS')
            self.write(':SOURce:RADio:ARB:WAVEform \"SEQ:{}\"'.format(file_name))
            self.write(':SOUR:POW:LEV:IMM:AMPL -50')
            if select_mode is 'OFDM':
                self.write(':SOUR:RAD:ARB:CLOCK:SRAT 40000000')
            elif select_mode is 'DSSS':
                self.write(':SOUR:RAD:ARB:CLOCK:SRAT 44000000')
            self.write(':OUTPut ON')

    def awg_run_waveform_file(self, file_name='11DSSS_CCK_1024B.WF1',
                         custom_clock=40e+6, select_mode='OFDM'):
        """
        AWG send out waveforms in accordance with waveform files.
        :param file_name: keywords['11DSSS_CCK_1024B.WF1', 12OFDM_QPSK_1000B.WF1, 18OFDM_QPSK_1000B.WF1,
        24OFDM_16QAM_1000B.WF1, 36OFDM_16QAM_1000B.WF1, 48OFDM_16QAM_1000B.WF1, 54OFDM_64QAM_1000B.WF1, 6OFDM_BPSK_1000B.WF1,
        9OFDM_BPSK_1000B.WF1]
        :param custom_clock:
        :param select_mode:
        :return:
        """
        self.utility_range_check(data_type=type('str'), value=select_mode, list_option=['OFDM', 'DSSS', 'CUSTOM'])
        self.utility_range_check(data_type=type('str'), value=file_name, list_option=['11DSSS_CCK_1024B.WF1', '12OFDM_QPSK_1000B.WF1', '18OFDM_QPSK_1000B.WF1',
        '24OFDM_16QAM_1000B.WF1', '36OFDM_16QAM_1000B.WF1', '48OFDM_16QAM_1000B.WF1', '54OFDM_64QAM_1000B.WF1', '6OFDM_BPSK_1000B.WF1',
        '9OFDM_BPSK_1000B.WF1'])
        if select_mode is 'CUSTOM':
            self.write('*CLS')
            self.write(':SOUR:POW:LEV:IMM:AMPL -50')
            self.write(':SOUR:RAD:ARB:CLOCK:SRAT {}'.format(custom_clock))
        else:
            self.write('*CLS')
            self.write(':SOURce:RADio:ARB:WAVEform \"WFM1:{}\"'.format(file_name))
            self.write(':SOUR:POW:LEV:IMM:AMPL -50')
            if select_mode is 'OFDM':
                self.write(':SOUR:RAD:ARB:CLOCK:SRAT 40000000')
            elif select_mode is 'DSSS':
                self.write(':SOUR:RAD:ARB:CLOCK:SRAT 44000000')
            self.write(':OUTPut ON')

    def halt_awg_operation(self):
        """
        This command is used to stop the AWG process.
        :return:
        """
        self.write('*CLS')
        self.write(':OUTPut OFF')
        self.write(':SOUR:POW:LEV:IMM:AMPL -70')

    def awg_cw_tone(self, freq=2412000000):
        """
        AWG sending CW tone wave.
        :param freq: Frequency that the instrument generates.
        :return:
        """
        self.write('*CLS')
        self.write(':SOUR:RAD:ARB:STAT OFF')
        self.write(':SOUR:POW:LEV:IMM:AMPL -50')
        self.write(':SOUR:FREQ:FIX {}'.format(freq))
        self.write(':OUTPut ON')

