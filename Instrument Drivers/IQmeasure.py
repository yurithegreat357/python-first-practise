"""National Instrument Switch module instrument driver.

Currently NI digital multimeter module library only supports on Windows, not on Linux. All the function names conform to
nidmm.h.

For 32-bit Windows
C:\Program Files (x86)\IVI Foundation\IVI\Include\nidmm.h
C:\Program Files (x86)\IVI Foundation\IVI\Bin\nidmm_32.dll

For 64-bit Windows
C:\Program Files\IVI Foundation\IVI\Include\nidmm.h
C:\Program Files\IVI Foundation\IVI\Bin\nidmm_64.dll

Supported Models:

- NI PXI-4022

:Copyright: 2018, Cisco Systems
:Author:
"""

import logging
import platform
from ctypes import *

log = logging.getLogger(__name__)


class Driver(object):
    """NI Digital Multi-meter (DMM) module instrument driver.

    :Supported Models: PXIe-408x, PXI-407x, PXI-4065, PCIe-4065, PCI-4065, PXI-4022
    """
    def __init__(self, resource="192.168.106.19"):
        self.session = c_int(0)

        arch_info = platform.architecture()
        if "32bit" in arch_info:
            lib_name = "D:\\trunk\\driver\\IQMAX\\IQmeasure.dll"

        else:
            lib_name = "D:/trunk/driver/IQMAX/IQmeasure.dll"

        # for WIN 32bit, we should use CDLL to recall dll
        self.lib = CDLL(lib_name)
        # for WIN 64bit, we should use CDLL to recall dll
        # self.lib = windll.LoadLibrary(lib_name)
        self.InitTester(resource)

    def call_func(self, func_name, *args):
        """A function wrapper to call the NI switch function and check if status is OK.

        If the function return status is not equal to 0, it will raise an exception with the detailed messages.
        :param str func_name: the function name
        :param args: function parameters
        :return: status (function call status)
        :rtype: int
        """
        func = getattr(self.lib, func_name)
        new_args = []
        for a in args:
            if isinstance(a, str):
                new_args.append(a.encode())
            else:
                new_args.append(a)
        status = func(*new_args)
        if status is not 0:
            self.close()
            raise Exception("NIDMM ERROR: func_name=%s, code=%d" % (func_name, status))

        return status

    def get_error(self, error_code):
        """It retrieves and then clears the IVI error information for the session or the current execution thread.

        If you specify a valid IVI session for the vi parameter, this function retrieves and then clears the error
        information for the session. If the user passes VI_NULL for the vi parameter, this function retrieves and then
        clears the error information for the current execution thread.

        :return: error description
        :rtype: str
        """
        msg = create_string_buffer(256)
        self.err_call('LP_GetErrorString', error_code, (msg))
        return msg.value

    def InitTester(self, resource="192.168.106.19"):
        """
        Establishes the connection between the PC and the tester,
        and initializes the connected tester, in a 1-tester mode.
        :param resource: The IP-address of the tester, as a text string.
        :return:
        """
        self.call_func("LP_Init")
        create_string_buffer(resource)
        ERR_OK = self.call_func("LP_InitTester",(resource))
        return ERR_OK

    def query_agc(self):
        """ Sets up the AGC (Automatic Gain Control)..

        :param value: outputs the level of the RF Amplitude (double)
        :return: None
        """
        reading = c_double(0)
        status = self.call_func('LP_Agc',  byref(reading))
        return reading.value

    def LP_GetVsaSettings(self):
        """
        Returns the settings of the analyzer.
        :return:
         freqHz:  VSA frequency (Hz) setting
         ampl:  VSA amplitude (dBm)
         port:  VSA port: PORT_OFF, PORT_LEFT, PORT_RIGHT, PORT_BB
         rfEnabled:  VSA RF state: 0-disalbed; 1-enabled
         triggerLevel:  VSA trigger level
        """
        freqHz = c_double(0)
        ampl = c_double(0)
        port = c_int(0)
        rfEnabled= c_int(0)
        triggerLevel = c_double(0)
        self.call_func('LP_GetVsaSettings',byref(freqHz), byref(ampl), byref(port), byref(rfEnabled),
                                byref(triggerLevel))
        return freqHz.value, ampl.value, port.value, rfEnabled.value, triggerLevel.value

    def get_version(self,  buff_size=256):
        """
        Retrieves the IQapi version number and date.
        :param buff_size: The size of the buffer, i.e. 44
        :return:
        """
        buffer = create_string_buffer(256)
        self.call_func('LP_GetVersion', (buffer), c_int(buff_size))
        return buffer.value

    def analysis_wave(self):
        """ Performs a Wave analysis of the signal captured by the VSA.
        """
        reading = c_double(0)
        ERR_OK = self.call_func('LP_AnalysisWave', byref(reading))
        return reading.value

    def LP_SetVsaBluetooth(self, rfFreqHz=2412e6, rfAmplDb=18, port=2,
                           triggerLevelDb=-25, triggerPreTime=10e-6):
        """
        Sets up VSA for Bluetooth data capturing.
        :param rfFreqHz: The center frequency of Bluetooth RF signal (Hz).
        :param rfAmplDb: rfAmplDb The amplitude of the peak power (dBm) of the signal.
        :param port: The port to which the VSG connects, with the following options:
                1: OFF
                2: Left RF port (RF1) (Default)
                3: Right RF port (RF2)
                4: Baseband
        :param triggerLevelDb: The trigger level (dBm) used for signal trigger.
        :param triggerPreTime: TriggerPreTime The pre-trigger time used for signal capture.
        :return:
        """
        self.call_func('LP_SetVsaBluetooth', c_double(rfFreqHz), c_double(rfAmplDb), c_int(port),
                       c_double(triggerLevelDb), c_double(triggerPreTime))

    def analyze_bluetooth(self, data_rate=2, analysis_type='All'):
        """
        Performs a Bluetooth analysis of the signal captured by the Vector Signal Analyzer (VSA).
        :param data_rate: Bit  rate 1, 2, or 3 Mbps (double)
        :param analysis_type: Specifies what type of analysis to perform. Default: 'All'. Valid values are as follows:
                 - PowerOnly
                 - 20dbBandwidthOnly
                 - PowerandFreq
                 - All  (This is the set default value)
                 - ACP  (only does the new ACP analysis)
                 - AllPlus  (performs all the analyses that are done by All?plus the ACP analysis)

        :return:
        """
        self.call_func('LP_AnalyzeBluetooth', c_double(data_rate), c_char(analysis_type))

    def close(self):
        """
        Terminates the connection between the PC and one or more testers.
        """
        return self.call_func("LP_ConClose")

    # error functions
    def get_error_message(self, error_code=0):
        """Convert an error code into a user-readable string.

        Note: to call this function, the session has to be valid.
        :param int error_code: error code
        :return: error_message
        :rtype: str
        """
        error_message = create_string_buffer(1024)
        self.lib.niDMM_GetErrorMessage(self.session, error_code, 1024, error_message)
        return error_message.value

    def LP_SetVsa(self, freq=2.412e9, rfamp_db=-44.597, port=3, extAttenDb=0, triggerLevelDb=-15, trigger_time = 10e-6):
        """
        Sets up the VSA.
        :param freq: The frequency of the VSA in Hz
        :param rfamp_db: The signal level of the VSA in dBm
        :param port: The port to which the VSA is connected:
            1: OFF
            2: Left RF port (default)
            3: Right RF port
            4: Baseband
        :param extAttenDb: The external attenuation on the VSA port
        :param triggerLevelDb: Sets the trigger level of the VSA in dB
        :param trigger_time: Time
        :return:
        """
        return self.call_func("LP_SetVsa",
                       c_double(freq),
                       c_double(rfamp_db),
                       c_double(port),
                       c_double(extAttenDb),
                       c_double(triggerLevelDb),
                       c_double(trigger_time))

    def LP_SetVsg(self, rfFreqHz = 2.412e9, rfGainDb=-50, port=3):
        """
        Sets up the VSG.
        :param rfFreqHz: The frequency of the VSG in Hz
        :param rfGainDb: The output gain level of the VSG in dBm
        :param port: The port to which the VSG is connected:
                        1: OFF
                        2: Left RF port (default)
                        3: Right RF port
                        4: Baseband
        :return:
        """
        self.call_func('LP_SetVsg', c_double(rfFreqHz),  c_int(port), c_double(rfGainDb),)

    def LP_SetVsgModulation_SetPlayCondition(self, modFileName = 'C:\Development\projects\WNBU\Antigua_WIN7'
                                                                        '\Antigua_PM3\Instruments\LitePoint_LV'
                                                                 '\6OFDM_BPSK_100B.mod', auto_play = 1):
        """
        Sets VSG to transmit a modulated signal.
        :param modFileName: Modulation file.
        :param auto_play: default 1
        :return:
        """
        buffer = create_string_buffer(modFileName)
        self.call_func('LP_SetVsgModulation_SetPlayCondition', (buffer), c_int(auto_play))
        return buffer.value

    def LP_SetVsaTriggerTimeout(self, trigger_time=0):
        """
        Trigger timeout.
        :param trigger_time: float
        :return:
        """

        self.call_func('LP_SetVsaTriggerTimeout', c_double(trigger_time))

    def LP_GetSampleData(self, vsa_num=0, buffer_real=-99999, buff_imag=-99999):
        """
        This function retrieves the sampled data from the VSA.
        :param vsa_num: The number of the VSA to retrieve data from ("0" if single box system)
        :param buffer_real: An initialized array of bufferLength size to store real values.
        :param buff_imag: An initialized array of bufferLength size to store imaginary values.
        :return:
        """
        self.call_func('LP_GetSampleData', c_int(vsa_num), c_double(buffer_real), c_double(buff_imag))

    def LP_AnalyzeMimo(self, type='EWC', mode='nxn', enable_phase_correct=1, system_timing_correct=1,
                       enable_amplitude=0, decode_psdu=0, enable_full_packet_channel=0, reference_file=""):
        """
        Perform an 802.11n (MIMO) analysis of the signal captured by the VSA.
        :param type: The type of packet to generate. Currently, only EWC is supported.
        :param mode: nxn or composite
        :param enable_phase_correct: Enable Phase Correction with the following options:
                0: Phase Correction is disabled
                1: Phase Correction is enabled
        :param system_timing_correct: The symbol clock correction mode with the following options:
                0: Symbol timing in disabled
                1: Symbol timing is enabled
        :param enable_amplitude: Enable Amplitude Tracking with the following options:
                0: Amplitude Tracking is disabled
                1: Amplitude Tracking is enabled
        :param decode_psdu: decode the PSDU with the following options:
                0: Do not perform full demodulation (faster)
                1: Perform full demodulation
        :param enable_full_packet_channel: Enable Full Packet Channel Estimation with the following options:
                0: Use default HT-LTF Channel Estimation
                1: Enable Channel Estimation using full packet
        :param reference_file: Reference file is required when mode is set to composite
        :return: type:  Type of packet to generate
                 mode:  Type of mode that is set
                 Reference:  file Reference file used
        """
        self.call_func('LP_AnalyzeMimo', (create_string_buffer(type)), (create_string_buffer(mode)), c_int(enable_phase_correct),
                       c_int(system_timing_correct), c_int(enable_amplitude), c_int(decode_psdu),
                       c_int(enable_full_packet_channel), (create_string_buffer(reference_file)))

    def LP_GetScalarMeasurement(self, measurement='evmAvgAll'):
        """
        Retrieves the results generated in the analysis functions in the form of a String value.
        :param measurement: Name (keyword) of the measurement to be retrieved. Please refer to String Measurements for
         all available measurement names
        :param index: index of the result (default "0")
        :return:
        """
        create_string_buffer(measurement)
        result = c_int(0)
        self.call_func('LP_GetScalarMeasurement', (measurement), byref(result))
        return result.value

    def LP_GetStringMeasurment(self, measurement='rateInfo_modulation', bufffer_length=30):
        """
        This function retrieves the sampled data from the VSA
        :param measurement: The number of the VSA to retrieve data from ("0" if single box system)
        :return:
        """
        func_input = create_string_buffer(measurement)
        result_real = create_string_buffer(256)
        self.call_func('LP_GetStringMeasurment', func_input, (result_real), c_int(bufffer_length))
        return result_real.value

    def LP_AnalyzePower(self, t_interval=3.2e-6, max_power_diff=15):
        """
        Performs an analysis of power of the signal captured by the VSA.
        :param t_interval: Specify the interval that is used to determine if power is present (sec).
        :param max_power_diff: Specify the maximum power difference between packets that are expected to be detected.
        :return:
        """
        self.call_func('LP_AnalyzePower', c_double(t_interval), c_double(max_power_diff))

    def LP_Analyze80211ag(self, phase_correction=3, channel_est=3, symbol_timing_correction=2, freq_sync=2,
                          amp_tracking_mode=2):
        """
        Performs 802.11 a/g Analysis on current capture.
        :param phase_correction: Phase Correction Mode with the following valid options:
        1: Phase correction off
        2: Symbol-by-symbol correction (Default)
        3: Moving avg. correction (10 symbols)
        :param channel_est: Channel Estimate with the following options:
        1: Raw Channel Estimate (based on long training symbols) (Default)
        2: 2nd Order Polyfit
        3: Full packet estimate
        :param symbol_timing_correction: Symbol Timing Correction with the following options:
        1: Symbol Timing Correction Off
        2: Symbol Timing Correction ON (Default)
        :param freq_sync: Frequency Sync. Mode with the following options:
        1: Short Training Symbol
        2: Long Training Symbol (Default)
        3: Full Data Packet
        :param amp_tracking_mode: Amplitude Tracking with the following options:
        1: Amplitude tracking off (Default)
        2: Amplitude tracking on
        :return:
        """
        self.call_func('LP_Analyze80211ag', c_int(phase_correction), c_int(channel_est),
                       c_int(symbol_timing_correction),
                       c_int(freq_sync), c_int(amp_tracking_mode))
