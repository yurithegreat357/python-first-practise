import logging
import errno
import os
import re
import signal
import re
import json
from socket import *
from functools import wraps
from ....libs.error import AccessPointError
from ....utils.win_com import WindowsConnect

logger = logging.getLogger(__name__)
__author__ = 'Yuri'

STATION_CONFIG_PATH = 'C:\pm2_config\station_param\\'
STATION_CAL_STEP_PARAM = 'C:\pm2_config\station_cal_step_param\\'
AOA_STEP_PARAM='C:\pm2_config\AOA_cal_step_param\\'
PRODUCT_DEF_PARAM = 'C:\pm2_config\product_def\\'
PM2_STEP_PARAM = 'C:\pm2_config\pm2_step_param\\'
DLL_PATH = r'C:\Development\projects\WNBU\Barbados_3K\Barbados_Station_Cal\Barbados_Station_Cal_DLL\builds\Barbados_Station_Cal.dll'
GLOBAL_PATH = r'C:\pm2_config\global\\'

class TimeoutError(Exception):
    pass


class WindowsError(AccessPointError):
    pass


def dll_timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    """
    Time out decorator for Apollo request. Put it on every single-line xmlrpc function to raise
    time out if time out is reached.
    :param seconds:
    :param error_message:
    :return:
    """
    def decorator(func):
        def _handle_timeout():
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


class WinConnectPM2(WindowsConnect):
    """
    This Class is used to send and receive command from Windows machine via TCP/IP. Using Thread method to
    send command & receive feedback simultaneously. The example is shown in main() function
    """
    def __init__(self, port, win_addr):
        super(WinConnectPM2, self).__init__(port=port, win_addr=win_addr)
        json_data = open('/opt/cisco/te/scripts/projects/wnbu/trunk/product_group_1/barbados/'
                         'config/pm2_station_cal_limits.json')
        self.jdata = json.load(json_data)
        self.cal_power = self.jdata['CAL_POWER'][0]


    @dll_timeout(120, 'Apollo request time out')
    def run_dll(self, object_name, path=DLL_PATH):
        """
        Call & executing dlls at Windows machine.

        :param object_name: The invoke name of dll, read docstring for invoke name.
        :param path: the dll path at Windows machine. Usually configure in (test name)_step_param.py
        :return:test_status, test_message (If no measure are performed)
                test_status, test_message, measure_data(if measure performed)

        example1(raw_data(from windows) = 'FAIL|Open vi Fail!') :
        windows = WinConnectPM2(address, port)
        test_status, test_message= windows.run_dll(path = xxxxx, object_name = xxxxx)
        if 'FAIL' in raw_data:
            test_status, fail_message = instrument.data_deconstruct(raw_data)
            return lib.FAIL, '{}, {}'.format(test_status, fail_message)

        example2(raw_data(from windows) = 'PASS|Measure complete|string|Apollo test'):
        instrument = WinConnectPM2(address, port)
        test_status, test_message, data = windows.run_dll(path = xxxxx, object_name = xxxxx)
        """
        data = self.proxy.run_dll(object_name, path)
        if '|' in data:
            new = data.split('|')
            test_status = new[0]
            test_message = new[1]
            data_value = new[2]
            logger.info(test_status)
            if data_value:
                return test_status, test_message, eval(data_value)
            else:
                return test_status, test_message
        else:
            return data

    @staticmethod
    def split_data_for_idn(data):
        """
        :param data: Raw test message from idn dll.
        :return:
        """
        _, esg_name, _, esg_version, _, pwr_sensor_name, _, power_sensor_ver = data.split(',')
        return esg_name, esg_version, pwr_sensor_name, power_sensor_ver

    @staticmethod
    def data_deconstruct(data):
        """
        This function is used to filter out the raw string flow sent from LabView vi(dll),
        The string flow format is:
        'PASS/FAIL/Measure(Test status)|Test message(Fail source message directly from LabView Vi)|data_value(The
        test data value, the return type is depend on the Data Type parameter)
        :param data: Raw string flow that comes from fet_labview_data
        :return: test_status, test_message (If no measure are performed)
                test_status, test_message, measure_data(if measure performed)

        example1(raw_data(from windows) = 'FAIL|Open vi Fail!') :
        instrument = WinConnectPM2(address, port)
        raw_data = instrument.fet_labview_data()
        if 'FAIL' in raw_data:
            test_status, fail_message = instrument.data_deconstruct(raw_data)
            return lib.FAIL, '{}, {}'.format(test_status, fail_message)

        example2(raw_data(from windows) = 'PASS|Measure complete|string|Apollo test'):
        instrument = WinConnectPM2(address, port)
        raw_data = instrument.fet_labview_data()
        test_status, test_message, data = instrument.data_deconstruct(raw_data)
        """
        if '|' in data:
            new = data.split('|')
            test_status = new[0]
            test_message = new[1]
            data_value = new[2]
            if data_value:
                return test_status, test_message, eval(data_value)
            else:
                return test_status, test_message
        else:
            return data

    @staticmethod
    def process_data(val):
        """
        Parse the number in return flow(For station cal use only)
        the data format is: "Station cal Measure @ 5905 MHz Cable power -60.998"
        :param val:
        :return:
        """
        index_result = [i for i, item in enumerate(val) if item.endswith('PASS')]
        logger.info('Totally {} paths'.format(index_result[0]))
        buff = []
        for i in range(0, index_result[0]):
            str_buf = val[i]
            result = re.findall(r"[-+]?\d*\.\d+|\d+|\d+", str_buf)
            buff.append(result)
        return buff

    def verify_value(self, path=None, input_list=None):
        """
        This function is used for station cal value verify. It will comapre the measure values with
        json configure file(imported from /opt/cisco/te/scripts/projects/wnbu/trunk/product_group_1/barbados/foc
        /libs/station_cal_limits.json'
        :param path: int 1 - 8
        :param input_list: list format [ ['2400', '-27.5']] the first one is frequency,
        the second one is measured raw data
        :return: If value pass
        """
        pathkey = 'PATH' + str(path)
        s = self.jdata[pathkey]
        buff = ''
        log_buff = ''
        fail_list = []
        for i in range(len(input_list)):
            processed = abs(float(input_list[i][1])) - abs(self.cal_power)
            if s[input_list[i][0]][0] < processed < s[input_list[i][0]][1]:
                logger.info(input_list[i][0]+' PASS')
                buff += (input_list[i][0] + ' PASS')
                log_buff += input_list[i][0] + ' ' + str(processed) + ' PASS' + '\n'
            else:
                logger.info(input_list[i][0] + ' ' + str(processed) + ' FAIL')
                buff += (input_list[i][0] + ' ' + str(processed) + ' FAIL')
                log_buff += input_list[i][0] + ' ' + str(processed) + ' FAIL' + '\n'
                fail_list.append(input_list[i][0] + ' ' + str(processed) + ' FAIL')
        if 'FAIL' in buff:
            raise WindowsError('Cal value out of limit!! Fail freq is {}'.format(fail_list))
        else:
            return True

    def config_station_cal(self, path=None, step_name=None):
        """
        config station cal frequency & cal power for ESG
        :param path: 1 - 8
        :param step_name: Windows machine will create a series folders by test steps
        which contain the parameters that will be used during test.
        :return:
        """
        sorted_list = self.get_json_freq(path=path)
        cal_power = self.jdata['CAL_POWER']
        self.config_windows_limits(limits_list=[str(path)], name='path', tst_area='station_config')
        self.config_windows_limits(limits_list=sorted_list, name='frequency', tst_area='station_config')
        self.config_windows_limits(limits_list=sorted_list, name='frequency',
                                   step=step_name, tst_area='station_cal')
        self.config_windows_limits(limits_list=cal_power, name='cal_power', tst_area='station_config')
        self.config_windows_limits(limits_list=cal_power, name='cal_power', step=step_name, tst_area='station_cal')

    def get_json_freq(self, path=None):
        """
        Read json file and return the frequency value in order
        :param path: range 1-8
        :return: sorted frequency (in orderly fashion)
        """
        pathkey = 'PATH' + str(path)
        s = self.jdata[pathkey]
        sort_value = sorted(s)
        return sort_value

    def create_product_def_folder(self, pid):
        pid_folder = PRODUCT_DEF_PARAM + '{}'.format(pid)
        self.proxy.build_directory(pid_folder)

    def build_product_def(self, pid, limits_name, limit_value):
        """
        Building config file under C:/pm2_config/product_def folder.
        :param pid: Product pid
        :param limits_name: Name of the limit
        :param limit_value: Limits value
        :return:
        """
        pid_folder = PRODUCT_DEF_PARAM + '{}'.format(pid)
        if isinstance(limit_value, (list,)):
            self.proxy.build_config_txt(pid_folder+'\\', None, limit_value, limits_name)
        else:
            self.proxy.build_config_txt(pid_folder + '\\', None, [limit_value], limits_name)

    def check_win_dll(self, step_dict):
        """
        Compare Windows dll with local dll file. Raise error if dll files missing.
        :param step_dict: import the dict that contain the dll name and md5 variables
        :return:
        """
        input_dict = self.proxy.check_dll()
        for key, value in step_dict.items():
            try:
                if input_dict[key] == step_dict[key]:
                    pass
                else:
                    raise WindowsError('dll file md5 not matched, Cannot perform test.The error file is {}'.format(key))
            except KeyError:
                raise WindowsError('dll file lost, Cannot perform test.The lost file is {}'.format(key))

    def windows_version_ctrl(self, md5_golden):
        windows_md5 = self.proxy.get_file_md5('C:\pm2_config\station_script\dll_exec.py')
        if md5_golden == windows_md5:
            pass
        else:
            raise WindowsError('Apollo script and Windows script not matched! Please '
                               'update the Windows script')
