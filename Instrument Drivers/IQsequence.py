import logging
import platform
from ctypes import *
import numpy as np
#import ctypes

log = logging.getLogger(__name__)


class Driver(object):
    def __init__(self,resource="192.168.106.19"):
        self.session = c_int(0)

        arch_info = platform.architecture()
        if "32bit" in arch_info:
            lib_name = "D:\\trunk\\driver\\IQMAX\\IQsequence.dll"

        else:
            lib_name = "D:/trunk/driver/IQMAX/IQsequence.dll"

        # for WIN 32bit, we should use CDLL to recall dll
        self.lib = CDLL(lib_name)
        # for WIN 64bit, we should use CDLL to recall dll

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
            raise Exception("IQmax return ERROR: func_name=%s, code=%d" % (func_name, status))
        return status

    def LP_MpsInit(self):
        """
        Initializes MPS.
        :return: return 0 if MPS was initialized OK; non-zero indicates MPS failed to initialize.
        """
        reading = c_int(0)
        self.call_func('LP_MpsInit', byref(reading))
        return reading.value

    def LP_MpsGetVersion(self, buff_size=2048):
        """
        Return IQsequence Version Info.
        :param buff_size:
        :return: return 0 if MPS was initialized OK; non-zero indicates MPS failed to initialize.
        """
        buffer = create_string_buffer(2048) #"IQMM0783"
        self.call_func('LP_MpsGetVersion', (buffer), c_int(buff_size))
        return buffer.value

    def LP_MptaGetSerialNumber(self, buffer_size=256):
        """
        Retrieve the Serial Number of MPTA connected.
        :param buffer_size:
        :return:
        """
        serial = create_string_buffer(256)
        self.call_func("LP_MptaGetSerialNumber", (serial), c_int(buffer_size))
        return serial.value

    def LP_MptaDirectCapture(self, sampling_time=1.2e-4, trigger_type=6, port_mask=1, ht40_mode=0, capture_count=5,
                             configure_mpta=1, ampdb=18.517,  trigger_level=-10):
        """
        Performs non-switch capture using MPTA.
        :param sampling_time: The capture duration in second for the capture on each port. <=1023us
        :param trigger_type: Trigger type used for capturing. Valid options are:
               - 1: free-run
               - 2: external trigger
               - 6: signal trigger
        :param port_mask: Bit mask determining one or more ports will be used:
                - Bit 0 is for DUT Port 1
                - Bit 1 is for DUT Port 2
                - Bit 2 is for DUT Port 3
                - Bit 3 is for DUT Port 4
        :param ht40_mode: Specifies if the capture is for HT40 mask (802.11n only)
               - 1: HT40 mask on
               - 0: HT40 mask off
        :param capture_count:
        :param configure_mpta:
        :param rfampl_db:
        :param trigger_level:
        :return:
        """
        self.call_func("LP_MptaDirectCapture",c_double(sampling_time), c_int(trigger_type), c_int(port_mask),
                       c_int(ht40_mode), c_int(capture_count), c_int(configure_mpta), c_double(ampdb),
                       c_double(trigger_level))

    def LP_MptaSelectCaptureIndex(self, capture_index=0):
        """
        Selects one of the captures done by LP_MptaDirectCapture for analysis
        :param capture_index: captureIndex The capture index to be selected for analysis
        :return:
        """
        self.call_func('LP_MptaSelectCaptureIndex', c_int(capture_index))

    def LP_MpsRxPer_MIMO(self, segment_index=[0], pwer_level_stop=[-42.65], power_level_start=[-42.65], step=[1, 1],
                     packet_count=[0, 510, 520, 0], port_mask_list=[15], array_size=1):
        """
        Runs RX PER using MPTA
        :param segment_index: An array each element of which specifies a segment index (0 based) of the
              multi-segment wavefile
        :param power_level_start: An array each element of which specifies the start of power level (dBm at DUT)
                for each corresponding segment
        :param power_level_stop: An array each element of which specifies the stop of power level (dBm at DUT ports)
                for each corresponding segment
        :param step: An array each element of which specifies the increment of power level (dB) for each
                corresponding segment. Minimum step is 0.5dB.
        :param packet_count:An array each element of which specifies the number of packets to be transmitted for each
                corresponding segment. Maximum number of packets is 32768.
        :param port_masklist:An array specifying the list of port masks which are used for RX PER testing.
        :param array_size:Number of elements in the array segmentIndex[], powerLevelStart[], powerLevelStop[], step[],
                 packetCount[], and portMaskList[].
        :return:
        """

        arr1 = (c_int * len(segment_index))(*segment_index)

        arr2 = (c_double * len(pwer_level_stop))(*pwer_level_stop)

        arr3 = (c_double * len(power_level_start))(*power_level_start)

        arr4 = (c_double * len(step))(*step)

        arr5 = (c_int * len(packet_count))(*packet_count)

        arr6 = (c_int * len(port_mask_list))(*port_mask_list)

        ret = self.call_func('LP_MpsRxPer_MIMO', arr1, arr2, arr3, arr4, arr5, arr6, c_int(array_size))
        return ret


    def arr_converter(self, list_name):
        arr = (c_float * len(list_name))(*list_name)
        return arr

    def LP_MptaDirectCapture(self, sampling_time=122.00e-6, trigger_type= 6, port_mask=1, ht40=0, trigger_db=-14.483,
                             config_mpta=1):
        """
        Performs non-switch capture using MPTA.
        :param sampling_time: The capture duration in second for the capture on each port. <=1023us
        :param trigger_type: Trigger type used for capturing. Valid options are:
               1: free-run
               2: external trigger
               6: signal trigger
        :param port_mask: Bit mask determining one or more ports will be used:
                Bit 0 is for DUT Port 1
                Bit 1 is for DUT Port 2
                Bit 2 is for DUT Port 3
                Bit 3 is for DUT Port 4
        :param ht40: Specifies if the capture is for HT40 mask (802.11n only)
                1: HT40 mask
                2: HT20 mask (Default)
        :param trigger_db:
        :param config_mpta:
        :return:
        """
        self.call_func('LP_MptaDirectCapture', c_double(sampling_time), c_int(trigger_type), c_int(port_mask), c_int(ht40),
                       c_double(trigger_db), c_int(config_mpta))

    def LP_MptaGetRxPerResults(self, step_index=0):
        """
        Retrieves RX PER results from last run of LP_MptaRxPer.
        :param step_index: Specifies the step number of total steps included in LP_MptaRxPer. 0 based.
        :return:
         actualPowerLevel:  Returns the actual power levels for each enabled port at each power level
         packetSent:  Returns packets sent at each power level
         ackReceived:  Returns ACKs received at each power level
         per:  Returns the PER result at each power level
         arraySize:  Specifies the array size, meaning number of power levels.

        """
        powerlevel_point = POINTER(c_double)
        powerlevel_data = np.array([0, 0, 0, 0, 0])
        powerlevel_data = powerlevel_data.astype(np.double)
        data_p=powerlevel_data.ctypes.data_as(powerlevel_point)

        packet_sent_point = POINTER(c_int)
        packet_sent_data = np.array([0, 0, 0, 0, 0])
        packet_sent_data = packet_sent_data.astype(np.double)
        packet_sent_input = packet_sent_data.ctypes.data_as(packet_sent_point)

        ack_received_point = POINTER(c_int)
        ack_received_data = np.array([0, 0, 0, 0, 0])
        ack_received_data = ack_received_data.astype(np.double)
        ack_received_input = ack_received_data.ctypes.data_as(ack_received_point)

        per_point = POINTER(c_double)
        per_data = np.array([0, 0, 0, 0, 0])
        per_data = per_data.astype(np.double)
        per_input = per_data.ctypes.data_as(per_point)

        array_size = c_int(0)
        status = self.call_func('LP_MptaGetRxPerResults', c_int(step_index), data_p, packet_sent_input,
                             ack_received_input, per_input, byref(array_size))
        return powerlevel_data, packet_sent_data, ack_received_data, per_data, array_size.value

    def create_array_buffer_float(self, size):
        buftype = c_float * size
        buf = buftype()
        return buf

    def create_array_buffer_int(self, size):
        buftype = c_int * size
        buf = buftype()
        return buf
