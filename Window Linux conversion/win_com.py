import logging
import xmlrpclib
import signal
from socket import *
from functools import wraps
from ..libs.error import AccessPointError
from apollo.libs import lib
import os
import datetime
import errno

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


class WindowsConnect(object):
    def __init__(self, port='9997', win_addr=None, apollo_addr=None,
                 buffer_size=1024):
        """
        This Class is used to send and receive command from Windows machine via xmlrpc + TCP/IP. Using Thread method to
        send command & receive feedback simultaneously. The example is shown in main() function
        :param port: Specify the listening and command sending ports,
        :param win_addr: Windows machine ip address
        """
        if apollo_addr:
            self.apollo_addr = apollo_addr
        else:
            self.apollo_addr = gethostbyname(gethostname())
        self.win_addr = win_addr
        self.port = eval(port)
        self.buff_size = buffer_size
        self.proxy = xmlrpclib.ServerProxy("http://%s:%s/" % (self.win_addr, self.port), allow_none=True)

    @dll_timeout(120, 'Apollo request time out')
    def run_dll(self, object_name, path):
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
    def build_cal_log(data, root_path, sub_path, file_name):
        """
        Create a folder to store station cal result under /tftpboot
        :param data: data to write
        :param root_path: the root path for building the log, add '/' at the end of path string
               (for example: /home/chihuahua/Desktop/)
        :param sub_path: the folder name of the log files
        :param file_name: the log file name, with a Year-Month-Day time stamp + (file name)
        :return:
        """
        stamp = datetime.datetime.today().strftime('%Y-%m-%d')
        folder_path = root_path + sub_path + '/'
        final_path = root_path + sub_path + '/{}_{}'.format(str(stamp), str(file_name))
        logger.warning('The Station Cal logs has been saved to: {}'.format(final_path))
        try:
            os.mkdir(folder_path)
        except OSError:
            pass
        f = open(final_path, 'w')
        f.write(data)
        f.close()

    def config_windows_limits(self, limits_list=None, tst_area=None, step=None, name=None):
        """
        Send command to windows to build local config path and saved as .txt file <0_0>
        for example:
        config_window_limits(limits_list=['2100', '2200', '2300'], tst_area='station_cal, step=.., name='frequency')
        :param limits_list: must be a list. If input single parameter, use [] to wrap around the value.
        :param tst_area: station_cal: Put txt config files into pm2_config/station_cal_step_param
                         pm2: Put txt config files into pm2_config/station_cal_step_param
                         AOA: Put txt config files into pm2_config/AOA_step_param
                         station_config: put txt config under C:\pm2_config\station_param
                         global: put txt config file under C:\pm2_config\global
        :param step: The same as apollo step name. Import it from apollo
        :param name: file name(limits name)
        :return: md5 code of the txt file for checking
        """
        path = None
        if tst_area == 'station_cal':
            if step:
                path = STATION_CAL_STEP_PARAM
            else:
                raise WindowsError('step name not defined, cannot config')
        if tst_area == 'station_config':
            path = STATION_CONFIG_PATH
        if tst_area == 'AOA':
            path = AOA_STEP_PARAM
        if tst_area == 'pm2':
            path = PM2_STEP_PARAM
        if tst_area == 'global':
            path = GLOBAL_PATH
        md5 = self.proxy.build_config_txt(path, step, limits_list, name)
        return md5


def main():
    """
    Example of implementing WindowsConnect module.
    :return:
    """
    test = WindowsConnect(port=8888, win_addr='10.1.1.1')
    test.init_pwr_sensor()

if __name__ == '__main__':
    main()
