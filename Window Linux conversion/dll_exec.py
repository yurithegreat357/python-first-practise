import os
import hashlib
from ctypes import *
import errno


class LabViewCtrl:
    """
    author : Yuri Du
    This class is the main control handle for instrument control via Windows. The main control
    method is using dll or exe. You can build it through LabView Project viewer.
    """

    def __init__(self):
        self.main_config_directory = 'C:\pm2_config\\'
        self.dll_path = r'C:\Development\projects\WNBU\Barbados_3K\Barbados_Station_Cal\Barbados_Station_Cal_DLL\builds\\'
        self.exec_file_path = 'C:\pm2_config\station_script\dll_exec.py'
        self.test_result_path = r'C:\pm2_config\test_results\test_result.txt'

    def run_dll(self, dll_object, path):
        """
        This is a multi-tool function for Apollo to control Windows machine
        running dll files.
        :param dll_object: Read dll invoke list to instance correct object, Or error will be raised
        :param path: dll path on Windows machine.
        :return: Depends on  dll
        """
        if os.path.exists(self.test_result_path):
            os.remove(self.test_result_path)
        chihuahua = cdll.LoadLibrary(path)
        eval('chihuahua.{}()'.format(dll_object))
        return self.get_test_result()

    @staticmethod
    def build_directory(path):
        """
        Build a folder on Windows machine
        :param path: building path.
        :return:
        """
        try:
            os.mkdir('{}'.format(path))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        return True

    def build_config_txt(self, path=None, step=None, limits_list=None, name=None):
        """
        Receive a list from apollo and write it into a txt file
        :param path: the path to create txt file
        :param step: The same as apollo step name. Import it from apollo
        :param limits_list: must be a list. If input single parameter, use [] to wrap around the value
        :param name: file name(limits name)
        :return: md5 file name of the txt
        """
        build_path = path + name + '.txt'
        if step:
            build_path = path + step + '\\' + name + '.txt'
            if not os.path.exists(path + step):
                os.mkdir(path + '\\' + step)
            else:
                pass
        f = open(build_path, 'w')
        for i in range(len(limits_list)):
            if i >= len(limits_list) - 1:
                f.write('{}'.format(limits_list[i]))
            else:
                f.write('{},'.format(limits_list[i]))
        f.close()
        return self.get_file_md5(path=build_path)

    @staticmethod
    def get_file_md5(path):
        """
        Open the specific txt file and readout the md5 code for limits compare.
        :param path:
        :return:
        """
        build_path = path
        f = open(build_path, 'r')
        data = f.read()
        diff_check = hashlib.md5()
        diff_check.update(data)
        md5_code = diff_check.hexdigest()
        return md5_code

    def check_dll(self):
        """
        Open the specific folder and readout the md5 code of txt file.
        dll files are stored in "C:\Users\kiosk\Desktop\Barbados_station_cal\dll_apollo"
        :return: A dict which keys are dll file name,
        """

        ret = os.listdir(self.dll_path)
        md5_dict = {}
        for elements in ret:
            md5_dict[elements] = self.get_file_md5(path=self.dll_path + '\{}'.format(elements))
        return md5_dict

    @staticmethod
    def check_exec_script():
        """
        Send a copy of this script to Apollo for matching.
        :return:
        """
        f = open(os.path.realpath(__file__))
        content = f.read()
        f.close()
        return unicode(content)

    @staticmethod
    def check_exec(path):
        f = open(path)
        content = f.read()
        f.close()
        return content

    def get_test_result(self):
        """
        Open the test result txt file and send it to Apollo.
        Remove the file after transferring the message.
        :return:
        """
        f = open(self.test_result_path)
        test_result = f.read()
        f.close()
        os.remove(self.test_result_path)
        return test_result


if __name__ == '__main__':
    test = LabViewCtrl()
    print test.get_file_md5(path=os.path.realpath(__file__))
    print test.check_dll()
