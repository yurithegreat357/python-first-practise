"""
Initialte instrument : Instrument_setup()
Instrument idn : Id_instrument()
Measure cable loss : MeasureCableLos_apollos()
Build Path loss files: Apollo_Save_path_loss()
"""
import logging
from time import *
from apollo.libs import lib
from .....libs.server import Server
from ...config.pm2_station_cal_step_param import load_step_parameter
from ...libs.win_ctrl_pm2 import WinConnectPM2
from .....utils.product_def import load_config_module
from .....utils.scan import set_scan_container_number, scan_all_labels

__author__ = 'Yuri Du'
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
code_path = __name__

# user_dict
mb_tst_info = None
config = None
md5_num = None
windows = None


def pre_sequence_definition():
    seq = lib.get_sequence_definition('PRE SEQ')
    seq.add_step(labels_scan, name='SCAN CONTAINER')
    seq.add_step(module_load, name='LOAD_MODULES')
    seq.add_step(version_control, name='VERSION_CONTROL')
    seq.add_step(init_instrument, name='INIT_INSTRUMENT')
    seq.add_step(pre_finalize, name='PRE_FINALIZE', group_level=lib.FINALIZATION)
    return seq


def main_sequence_definition():
    seq = lib.get_sequence_definition('MAIN_INT_PRODUCT_SEQ')
    seq.add_step(userdict_invoke, name='INITIATE_USER_DICT')
    seq.add_step(module_load, name='LOAD_MODULES_MAIN')
    seq.add_step(instrument_idn, name='INSTRUMENT_IDN')
    seq.add_step('MEASURE_CABLE_LOSS_PATH1', codepath=code_path, function='measure_cable_loss', kwargs={'path': 1},
                 loop_on_error=2)
    seq.add_step('MEASURE_CABLE_LOSS_PATH2', codepath=code_path, function='measure_cable_loss', kwargs={'path': 2},
                 loop_on_error=2)
    seq.add_step('MEASURE_CABLE_LOSS_PATH3', codepath=code_path, function='measure_cable_loss', kwargs={'path': 3},
                 loop_on_error=2)
    seq.add_step('MEASURE_CABLE_LOSS_PATH4', codepath=code_path, function='measure_cable_loss', kwargs={'path': 4},
                 loop_on_error=2)
    seq.add_step('MEASURE_CABLE_LOSS_PATH5', codepath=code_path, function='measure_cable_loss', kwargs={'path': 5},
                 loop_on_error=2)
    seq.add_step('MEASURE_CABLE_LOSS_PATH6', codepath=code_path, function='measure_cable_loss', kwargs={'path': 6},
                 loop_on_error=2)
    seq.add_step('MEASURE_CABLE_LOSS_PATH7', codepath=code_path, function='measure_cable_loss', kwargs={'path': 7},
                 loop_on_error=2)
    seq.add_step('MEASURE_CABLE_LOSS_PATH8', codepath=code_path, function='measure_cable_loss', kwargs={'path': 8},
                 loop_on_error=2)
    seq.add_step(save_path_loss, name='SAVE_PATH_LOSS')
    seq.add_step(main_finalize, name='MAIN_FINALIZE', group_level=lib.FINALIZATION)
    return seq


def save_path_loss():
    step_dict, step_name = load_step_parameter(ctrl_handle=windows)
    test_status, test_message = windows.run_dll(step_dict['object_name'])
    if 'PASS' in test_status:
        return lib.PASS
    else:
        return lib.FAIL, test_message


def version_control():
    """
    check the script verion
    :return:
    """
    step_dict, step_name = load_step_parameter(ctrl_handle=windows)
    logger.warning('Windows code check PASS!')
    if lib.get_apollo_mode() == lib.MODE_DEBUG:
        logger.info('Skip version check if run in DEBUG mode')
        return lib.SKIPPED
    windows.check_win_dll(step_dict['dll_dict'])
    windows.windows_version_ctrl(step_dict['exec_md5'])
    server = Server(lib.conn.SERVER, 'server')
    server.source_code_diff_check('/opt/cisco/te/scripts/projects/wnbu/trunk/',
                                  ['utils', 'product_group_1', 'libs'])
    return lib.PASS


def config_load():
    """
    Load config file by config module name
    :return:
    """
    # load the config module
    # if all arguments are None, load the default product definition file
    global config
    config = load_config_module('STATIONCAL')
    windows.create_product_def_folder('STATIONCAL')
    windows.build_product_def('STATIONCAL', 'cal_header', config.cal_header)
    windows.build_product_def('STATIONCAL', 'station_cal_path', config.station_cal_path)
    windows.build_product_def('STATIONCAL', 'frequency', config.frequency)
    logger.info('Cal header is {}, cal path is {}'.format(config.cal_header, config.station_cal_path))

def userdict_init():
    """
    Initialize userdict to sttore the scanned labels of MB and Radio
    :return: None
    """
    userdict = lib.apdicts.userdict
    if 'mb_tst_info' not in userdict:
        userdict['mb_tst_info'] = dict()

    global mb_tst_info
    mb_tst_info = userdict['mb_tst_info']


def ask_change_probe(path):
    lib.ask_question(question='Change to port {}'.format(str(path)), picture_size='large',
                     picture_path='media/station_cal_info.jpg')
    return lib.PASS


def labels_scan():
    """ Labels scanning from operator input
    :return: lib.PASS if the function passes
    """
    userdict_init()
    container_name = lib.get_my_container_key().split('|')[-1]
    logger.warning(container_name)
    # container_num = container_number[0][-2:]
    mb_tst_info['slot'] = container_name[8:]
    logger.warning('The slot is {}'.format(mb_tst_info['slot']))
    return lib.PASS


def get_windows_parallel(timeout=60):
    """
    A tool for Apollo requests to wait for Windows windows test results, For Apollo parallel
    step use only! Don't use this in a single
    Create a 'lib.apdicts.userdict['STATUS_buff'] = None' at the start of test as the flag.
    Always place this function at the end of every parallel step request function.
    :param timeout: in seconds
    :return: True if all data Finished with 'END' mark(See Windows machine data transfer protocol)
    return 'FAIL' if timeout reached or FAIL in test data stream.
    """
    counter = timeout
    while True:
        sleep(1)
        counter -= 1
        if lib.apdicts.userdict['STATUS_buff']:
            break
        if counter <= 0:
            break
    if not lib.apdicts.userdict['STATUS_buff']:
        lib.apdicts.userdict['STATUS_buff'] = None
        return 'FAIL'
    if lib.apdicts.userdict['STATUS_buff'] == 'PASS':
        lib.apdicts.userdict['STATUS_buff'] = None
        return 'PASS'
    if lib.apdicts.userdict['STATUS_buff'] == 'FAIL':
        lib.apdicts.userdict['STATUS_buff'] = None
        return 'FAIL'


def module_load():
    first_exception = None
    config_data = lib.apdicts.configuration_data
    lib.apdicts.userdict['STATUS_buff'] = None
    logger.warning('Syncing Windows Machine {}'.format(config_data['win' + mb_tst_info['slot']]['windos_addr']))
    global windows
    windows = WinConnectPM2(port=config_data['win'+mb_tst_info['slot']]['ctrl_port'],
                            win_addr=config_data['win'+mb_tst_info['slot']]['windos_addr'])
    if first_exception is not None:
        if 'Address already in use' in first_exception:
            lib.ask_question(question='Please restart the apollo to reset the connection')
        raise first_exception
    logger.info('Successfully sync with Windows machine {} at port {}'
                .format(config_data['win' + mb_tst_info['slot']]['windos_addr'],
                        config_data['win' + mb_tst_info['slot']]['ctrl_port']))
    # Station config test
    build_windows_station_cofig(config_dict=config_data['win'+str(mb_tst_info['slot'])])
    msg, step_name = load_step_parameter(ctrl_handle=windows)     # step parameter test
    logger.warning(msg['msg'])
    return lib.PASS


def get_windows_single():
    """
    Put this at the end of every Apollo send function to get feedback msgs from Windows.
    This function is for single stream line process only.
    :return:
    """
    ret = windows.fet_labview_data()
    status, message = windows.data_deconstruct(ret)
    logger.warning('{}, {}'.format(status, message))
    return status, message


def instrument_idn():
    lib.apdicts.userdict['STATUS_buff'] = None
    step_dict, step_name = load_step_parameter(ctrl_handle=windows)
    test_status, test_message = windows.run_dll(step_dict['object_name'])
    logger.warning(test_message)
    if test_status == 'PASS':
        return lib.PASS
    else:
        return lib.FAIL, test_message


def get_instru_version():
    """
    Using Apollo measure decorator to check out the instrument firmware version. The limits can
    be defined in ..config/limits.py.
    :return:
    """
    ret = windows.fet_labview_data()
    status, message = windows.data_deconstruct(ret)
    if 'FAIL' in status:
        return lib.FAIL, message
    else:
        p = windows.split_data_for_idn(ret)
        logger.warning('The ESG is {0}, Firmware version is {1}'.format(p[0], p[1]))
        logger.warning('The Power Sensor is {0}, Firmware version is {1}'.format(p[2], p[3]))
        lib.apdicts.userdict['STATUS_buff'] = 'PASS'
        return lib.PASS


def measure_cable_loss(path=None):
    """
    Measure formula = |power sensor result - cal_power| according to LabView vi (Measure Cable Loss.vi)
    for example, if the measure value is -60, cal power is -10, the result is |-60 - (-10)| = 50
    :return: if measure number is out of range, will trigger a ask question dialog for further instructions. Each
    cal path has 3 chances of calibration, if you type 'override' in ask_question box, it will ignore
    the result and pursue to the next path.
    """
    lib.apdicts.userdict['RECEIVE'] = 'OPEN'
    ask_change_probe(path=path)
    step_dict, step_name = load_step_parameter(ctrl_handle=windows)
    windows.config_station_cal(path=path, step_name=step_name)
    test_status, test_message = windows.run_dll(step_dict['object_name'])
    splited_data = test_status.split('\n')
    output = windows.process_data(splited_data)
    windows.verify_value(input_list=output, path=1)
    if splited_data[len(splited_data)-1] == 'PASS':
        return lib.PASS
    else:
        return lib.FAIL


def init_instrument():
    step_dict, step_name = load_step_parameter(ctrl_handle=windows)
    logger.info(step_dict['object_name'])
    test_status, test_message = windows.run_dll(step_dict['object_name'])
    if 'PASS' in test_status:
        logger.warning(test_message)
        return lib.PASS
    else:
        return lib.FAIL, test_message

def add_tst_data():
    """
    To provide the required serial number, container, pid, and test area for tst logging. <0_0>
    :return: lib.PASS or lib.FAIL
    """
    # Create a STATIONCAL SN
    lib.add_tst_data(serial_number='STATIONCAL{}'.format(mb_tst_info['slot']), test_area='PCBPM2',
                     product_id='STATIONCAL', test_container=lib.get_my_container_key().split('|')[-1])
    return lib.PASS


def main_finalize():
    return lib.PASS


def userdict_invoke():
    userdict_init()
    return lib.PASS


def build_windows_station_cofig(config_dict=None):
    """
    This function will load the instance's attributes and build a series of config
    files at Windows machine. Including parent-class's attributes if you use inheritance.
    :param config_dict: the class that is name after the windows machine name. [Win01, Win02....]
    :return: The filename and md5 number.
    example:

    """
    for key, value in config_dict.items():
        windows.config_windows_limits(limits_list=[value], tst_area='station_config', name=key)
        logger.info(key + ':' + value)


def pre_finalize():
    config_load()
    add_tst_data()
    return lib.PASS
