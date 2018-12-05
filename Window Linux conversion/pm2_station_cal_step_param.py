"""
Created by Yuri;
This is the user parameters scripts. Every attribute name is sync with
every Apollo test step. Make sure the attributes match with it when configuring
test parameters
You can define global level parameter by directly setting attributes under
 sequence class. See example as followed:
==============================
set up parameters:
class ExamplePreSeq(object):
    TEST_STEP_NAME = {
        'local_parameter1': 'parameter_value',
        'local_parameter2': 'parameter_value2',
    }
    GLOBAL_PARAMETER_int = 666
    GLOBAL_PARAMETER_float = 666.6
==============================
invoke parameters in test steps:
from ...libs.test_step_parameters import ExamplePreSeq, load_step_parameter


def test_step():
    blah
    blah
    param = load_step_parameter(module_name=ExamplePreSeq)
    invoke1 = param['local_parameter1']  #invoke1='parameter_value'
    invoke2 = param['local_parameter2']  #invoke2='parameter_value2'
    invoke3 = ExamplePreSeq.GLOBAL_PARAMETER_int    #invoke3=666
    invoke4 = ExamplePreSeq.GLOBAL_PARAMETER_float   #invoke4=666.6

def test_step():
    blah
    blah
    blah
    load_json_limits_to_step(array_row=4, limit_name='Frequency', ctrl_handle=Windows)
==============================

This document is for dll file reference. Find the dll object in 'dll name'.h file
after building LabView vi to dll.
The writing format is "dll usage/function : dll object name"
The example is shown as follow:
==========================Start======================================
#include "extcode.h"
#pragma pack(push)
#pragma pack(1)

#ifdef __cplusplus
extern "C" {
#endif

void __cdecl Id_instrument(void);  <----- The object is here, use this to invoke it in python

long __cdecl LVDLLStatus(char *errStr, int errStrLen, void *module);

#ifdef __cplusplus
} // extern "C"
#endif

#pragma pack(pop)
======================End of tutorial==================================

Initialte instrument : Instrument_setup()
Instrument idn : Id_instrument()
Measure cable loss : MeasureCableLos_apollos()
Build Path loss files: Apollo_Save_path_loss()
"""
from apollo.libs import lib
import logging
import json
logger = logging.getLogger(__name__)
JSON_LIMITS_PATH = '/opt/cisco/te/scripts/projects/wnbu/trunk/product_group_1/barbados/config/pm2_station_cal_limits.json'

class Pm2PreSeq(object):
    LABEL_SCAN = {
        'test1': 'label_scan_test'
    }


class Pm2MainSeq(object):
    pass


class Pm2StationCal(object):
    LOAD_MODULES_MAIN = {
        'msg': 'THIS IS A TEST MSG!!!'
    }
    LOAD_MODULES = {
        'msg': 'This is a string test'
    }

    VERSION_CONTROL = {
        'exec_md5': '8935beac2b7981ea0bc3266cc0026210',
        'dll_dict': {
            'Barbados_Station_Cal.dll': '84de920e1a8ca22df8ee5d715a4ec7b6'
        }
    }

    INIT_INSTRUMENT = {
        'object_name': 'CPP_Initialize_Equipments'
    }

    INSTRUMENT_IDN = {
        'object_name': 'CPP_get_inst_info'
    }

    MEASURE_CABLE_LOSS_PATH1 = {
        'object_name': 'CPP_Cal_path_loss'
    }

    MEASURE_CABLE_LOSS_PATH2 = {
        'object_name': 'CPP_Cal_path_loss'
    }

    MEASURE_CABLE_LOSS_PATH3 = {
        'object_name': 'CPP_Cal_path_loss'
    }
    MEASURE_CABLE_LOSS_PATH4 = {
        'object_name': 'CPP_Cal_path_loss'
    }

    MEASURE_CABLE_LOSS_PATH5 = {
        'object_name': 'CPP_Cal_path_loss'
    }

    MEASURE_CABLE_LOSS_PATH6 = {
        'object_name': 'CPP_Cal_path_loss'
    }

    MEASURE_CABLE_LOSS_PATH7 = {
        'object_name': 'CPP_Cal_path_loss'
    }

    MEASURE_CABLE_LOSS_PATH8 = {
        'object_name': 'CPP_Cal_path_loss'
    }

    SAVE_PATH_LOSS = {
        'object_name': 'CPP_Save_path_loss'
    }

    global_msg = 'This is a global msg'


def load_step_parameter(module_name='Pm2StationCal', ctrl_handle=None):
    """
    Load station cal custom parameter in accordance to test step.
    Don't use this function in test def if no parameter are defined in test_step_parameters.py
    or it will raise type error.
    :param module_name: Fill in your import parameter class here
    :param ctrl_handle: Put your windows comm global param at here.
    :return: the parameter dict. See test_step_parameters.py docstring for more details
    """
    _, step_dict, input_dict, output_dict, _ = lib.getstepdicts()
    step_name = step_dict['name']
    try:
        ret = eval('{}.{}'.format(module_name, step_name))
        # convert every parameters to txt files on Windows machine
        for keys, value in ret.items():
            ctrl_handle.config_windows_limits(limits_list=[value], tst_area='station_cal', step=step_name, name=keys)
        return ret, step_name
    except AttributeError:
        logger.warning('No user defined parameters found :-(')


def load_json_limits_to_step(limit_name=None, array_row=None, ctrl_handle=None):
    """
    Load limits parameters to Step folder at Windows.
    :param limit_name: limit name
    :param array_row: Rows of array
    :param ctrl_handle: Include Windows_control object here
    :return:
    """
    _, step_dict, input_dict, output_dict, _ = lib.getstepdicts()
    step_name = step_dict['name']
    json_data = open(JSON_LIMITS_PATH)
    limit_probe = json.load(json_data)
    value = limit_probe[limit_name]
    if isinstance(str, (value,)):
        ctrl_handle.config_windows_limits(limits_list=[value], tst_area='AOA', step=step_name, name=limit_name)
        return '{} : {}'.format(limit_name, value)
    if isinstance(list, (value,)):
        if array_row:
            ctrl_handle.config_windows_limits(limits_list=[array_converter(row=array_row, input_array=value)],
                                              tst_area='AOA', step=step_name, name=limit_name)
        else:
            raise IOError('Array row is not defined!!')
        return '{} : {}'.format(limit_name, value)


def array_converter(row, input_array):
    """
    Convert any list format array into labview compatible one.
    :param row: The row of the formatted array
    for example:
    in this 4 row array.
    [1, 1, 1, 2,
     2, 2, 1, 2,
     3, 1, 2, 2,
    ]
    the output is 1,1,1,2
                  2,2,1,2
                  3,1,2,2
    :return: The formatted array.
    """
    buffer = ''
    output_buff = ''
    row_buff = 0
    for i in input_array:
        row_buff += 1
        buffer += str(i) + ','
        if row_buff == row:
            buffer = buffer[:-1]
            buffer += '\n'
            output_buff += buffer
            buffer = ''
            row_buff = 0
    return output_buff