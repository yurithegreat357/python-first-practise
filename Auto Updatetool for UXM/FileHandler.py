import os
import subprocess
import re
import time
import shlex
import winreg as reg
from typing import List
from winreg import *
import shutil
import traceback
import threading

__author__ = 'Yuri Du'
#   Property of Keysight Technologies, All rights reserved

install_new_update_tool = False

# "C:\LanSafe Installer\Setup.exe" -r -f1C:\LanSafeSilentFile.iss create iss file
# HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\
# Latest FW version 1.4.5.20961
# Firmware log path :C:\Users\Administrator\AppData\Local\Temp\UXMUpdateTool or
# D:\ProgramData\Keysight\E7515B\UxmInfoCmdLine.log
# info viewer path: C:\Program Files\Keysight\E7515B\InfoViewer
# ^((?!Information).)*$
# "UXM5G_FirmwareUpdateTool_Installer_2.0.13.0.exe" /S /v/qn (Silent install command)
# Firmware update usually takes about 16 - 20 minutes
doge = "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒\n" \
       "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░░░░░░░░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒\n" \
       "▒▒▒▒▒▒▒▒▒▒▒▒▒░░░░░░░░░░░░░░░░░░░▒▒▒▒▒▒▒▒▒▒▒▒\n" \
       "▒▒▒▒▒▒▒▒▒▒░░░░░░░░░░░░░░░░░░░░░░░░░▒▒▒▒▒▒▒▒▒\n" \
       "▒▒▒▒▒▒▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒▒▒▒▒▒▒\n" \
       "▒▒▒▒▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▄░░▒▒▒▒▒\n" \
       "▒▒▒▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██▌░░▒▒▒▒\n" \
       "▒▒▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░▄▄███▀░░░░▒▒▒\n" \
       "▒▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░█████░▄█░░░░▒▒\n" \
       "▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░▄████████▀░░░░▒▒\n" \
       "▒▒░░░░░░░░░░░░░░░░░░░░░░░░▄█████████░░░░░░░▒\n" \
       "▒░░░░░░░░░░░░░░░░░░░░░░░░░░▄███████▌░░░░░░░▒\n" \
       "▒░░░░░░░░░░░░░░░░░░░░░░░░▄█████████░░░░░░░░▒\n" \
       "▒░░░░░░░░░░░░░░░░░░░░░▄███████████▌░░░░░░░░▒\n" \
       "▒░░░░░░░░░░░░░░░▄▄▄▄██████████████▌░░░░░░░░▒\n" \
       "▒░░░░░░░░░░░▄▄███████████████████▌░░░░░░░░░▒\n" \
       "▒░░░░░░░░░▄██████████████████████▌░░░░░░░░░▒\n" \
       "▒░░░░░░░░████████████████████████░░░░░░░░░░▒\n" \
       "▒█░░░░░▐██████████▌░▀▀███████████░░░░░░░░░░▒\n" \
       "▐██░░░▄██████████▌░░░░░░░░░▀██▐█▌░░░░░░░░░▒▒\n" \
       "▒██████░█████████░░░░░░░░░░░▐█▐█▌░░░░░░░░░▒▒\n" \
       "▒▒▀▀▀▀░░░██████▀░░░░░░░░░░░░▐█▐█▌░░░░░░░░▒▒▒\n" \
       "▒▒▒▒▒░░░░▐█████▌░░░░░░░░░░░░▐█▐█▌░░░░░░░▒▒▒▒\n" \
       "▒▒▒▒▒▒░░░░███▀██░░░░░░░░░░░░░█░█▌░░░░░░▒▒▒▒▒\n" \
       "▒▒▒▒▒▒▒▒░▐██░░░██░░░░░░░░▄▄████████▄▒▒▒▒▒▒▒▒\n" \
       "▒▒▒▒▒▒▒▒▒██▌░░░░█▄░░░░░░▄███████████████████\n" \
       "▒▒▒▒▒▒▒▒▒▐██▒▒░░░██▄▄███████████████████████\n" \
       "▒▒▒▒▒▒▒▒▒▒▐██▒▒▄████████████████████████████\n" \
       "▒▒▒▒▒▒▒▒▒▒▄▄████████████████████████████████\n" \
       "████████████████████████████████████████████"


def logging_process(step_name, remove_log=False):
    if not remove_log:
        with open('{}.txt'.format(step_name), 'w') as f:
            f.write('Nop')
    else:
        os.remove('{}.txt'.format(step_name))


class SwitchCase:
    def __init__(self):
        self.ctrl_handle = FileHandler()

    def read_resume_files(self):
        file_list = os.listdir()
        for every_files in file_list:
            if every_files.startswith("resume"):
                pass
            else:
                self.full_operation()

    def full_operation(self):
        self.ctrl_handle.read_reg_keys()
        self.logging_process('resume_uninstallTA')
        self.ctrl_handle.uninstall_ta()
        self.logging_process('resume_uninstallTA', True)
        time.sleep(40)
        if self.ctrl_handle.update_tool_filename:
            self.ctrl_handle.uninstall_upate_tool()
            self.ctrl_handle.silent_install_update_tool()
        self.ctrl_handle.launch_updatetool_window()
        self.logging_process('resume_update_firmware')
        self.ctrl_handle.update_firmware_version()
        self.ctrl_handle.install_new_ta()

    def logging_process(self, step_name, remove_log=False):
        if not remove_log:
            with open('{}'.format(step_name), 'w') as f:
                f.write('Nop')
        else:
            os.remove(step_name)


class FileHandler:
    def __init__(self):
        self.proc = subprocess
        self.update_tool_comms = self.enum(ADD="-a", INFO="-i", UPDATE="-u")
        self.ta_filename = ''
        self.update_tool_filename = ''
        self.firmware_path = ''
        self.firmware_ver = ''
        self.ta_version = ''
        self.ta_version_current = ''
        self.uninstall_string = ''
        self.updatetool_version = ''
        self.updatetool_overwrite = ''
        self.initial_dir = os.getcwd()
        print(self.initial_dir)
        self.iss_file_dir = self.initial_dir + "\\iss_Files\\"
        self.log_file_path = 'UxmInfoCmdLine.log'
        print("=============================================\n Initializing, Please Wait...\n"
              "=============================================")
        self.read_reg_keys()
        self.get_update_toolversion()
        self.filter_install_file()
        print("InstallingTA version {}, Firmware {}".format(self.ta_version, self.firmware_ver))
        # self.setup_updatetool_dir()
        self.log_file_path = 'UxmInfoCmdLine.log'




    @staticmethod
    def add_to_restart(remove_key=False):
        # in python __file__ is the instant of
        # file path where it was executed
        # so if it was executed from desktop,
        # then __file__ will be
        # c:\users\current_user\desktop
        pth = os.path.dirname(os.path.realpath(__file__))

        # name of the python file with extension
        s_name = "FileHandler.py"

        # joins the file name to end of path address
        address = os.path.join(pth, s_name)

        # key we want to change is HKEY_CURRENT_USER
        # key value is Software\Microsoft\Windows\CurrentVersion\Run
        key = reg.HKEY_CURRENT_USER
        key_value = r"Software\Microsoft\Windows\CurrentVersion\Run"

        # open the key to make changes to
        reg_key = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
        if remove_key:
            reg.DeleteKeyEx(reg_key, "start_up", 0, reg.REG_SZ, address)
        else:
            reg.SetValueEx(reg_key, "start_up", 0, reg.REG_SZ, address)

        # now close the opened key
        reg.CloseKey(reg_key)


    def check_ta_install_status(self):
        reg_addr = r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'
        Registry = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        aKey = OpenKey(Registry, reg_addr)
        # print(RawKey)
        # for i in range(1024):
        #     keyname = EnumKey(aKey, i)
        #     asubkey = OpenKey(aKey, keyname)
        #     val = QueryValueEx(asubkey, "Comments")
        #     print(val)
        for i in range(150):
            try:
                keyname = EnumKey(aKey, i)
                asubkey = OpenKey(aKey, keyname)
                name, trash = QueryValueEx(asubkey, "Comments")
                if "Test Application" in name:
                    return True
            except WindowsError:
                pass
        return False

    def read_reg_keys(self):
        reg_addr = r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'
        Registry = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        aKey = OpenKey(Registry, reg_addr)
        # print(RawKey)
        # for i in range(1024):
        #     keyname = EnumKey(aKey, i)
        #     asubkey = OpenKey(aKey, keyname)
        #     val = QueryValueEx(asubkey, "Comments")
        #     print(val)
        for i in range(3000):
            try:
                keyname = EnumKey(aKey, i)
                asubkey = OpenKey(aKey, keyname)
                name, trash = QueryValueEx(asubkey, "Comments")
                if "Test Application" in name:
                    uninstall_path, trash = QueryValueEx(asubkey, "UninstallString")
                    # print(uninstall_path)
                    self.uninstall_string = uninstall_path
                    ta_current_version, trash = QueryValueEx(asubkey, "DisplayVersion")
                    self.ta_version_current = ta_current_version
            except WindowsError:
                pass

    def uninstall_ta(self):
        uninstall_string = self.uninstall_string
        iss_filename, state = self.check_iss_file(self.ta_version_current, 'uninstall')
        os.chdir(self.initial_dir)
        if not state:
            with open(os.path.join(self.initial_dir, 'uninstallTA.bat'), 'w') as OPN:
                OPN.writelines([uninstall_string + ' -r -f1"{}{}"'.format(self.iss_file_dir, iss_filename),
                                "\n",
                                'exit'])
            # self.send_command('uninstallTA.bat')
            self.send_command(uninstall_string + ' -r -f1"{}{}"'.format(self.iss_file_dir, iss_filename))
            os.remove('uninstallTA.bat')
        else:
            # self.send_command(uninstall_path + ' -s -f1"{}"'.format(self.iss_file_dir))
            with open(os.path.join(self.initial_dir, 'uninstallTA_silent.bat'), 'w') as OPN:
                OPN.writelines([uninstall_string + ' -s -f1"{}{}"'.format(self.iss_file_dir, iss_filename),
                                "\n",
                                'exit'])
            self.send_command(uninstall_string + ' -s -f1"{}{}"'.format(self.iss_file_dir, iss_filename))
            os.remove('uninstallTA_silent.bat')
        timer = 30
        while True:
            ret = self.check_ta_install_status()
            time.sleep(1)
            if not ret or timer >= 30:
                break

    def move_install_files(self, iss_filename):
        shutil.move('C:\\Windows\\'.format(iss_filename), self.iss_file_dir)

    def check_iss_file(self, ta_version, state):
        os.chdir(self.initial_dir + "\\iss_Files\\")
        file_list = os.listdir()
        for everyfile in file_list:
            if ta_version in everyfile:
                if '_'+state in everyfile:
                    return everyfile, True
        return '{}_{}.iss'.format(ta_version, state), False

    def install_new_ta(self):
        os.chdir(self.initial_dir)
        install_string = "\"%s\\%s\"" % (self.initial_dir, self.ta_filename)
        iss_filename, state = self.check_iss_file(self.ta_version, 'install')
        if not state:
            command = " /r /f1" + "\"%s%s_install.iss\"" % (self.iss_file_dir, self.ta_version)
            with open(os.path.join(self.initial_dir, 'installTA.bat'), 'w') as OPN:
                OPN.writelines([install_string + command, "\n", 'exit'])
            # self.send_command('start "{}"'.format(install_string))
            os.chdir(self.initial_dir)
            print(os.getcwd())
            self.send_command('installTA.bat')
            os.remove('installTA.bat')
        else:
            command = install_string + " /s /f1" + "\"%s%s\"" % (self.iss_file_dir, iss_filename)
            with open(os.path.join(self.initial_dir, 'installTA_silent.bat'), 'w') as OPN:
                OPN.writelines([command, "\n",
                                'exit'])
            os.chdir(self.initial_dir)
            self.send_command('installTA_silent.bat')
            # subprocess.call(['installTA_silent.bat'], timeout=10, shell=True)
            os.remove('installTA_silent.bat')
        while True:
            ret = self.check_ta_install_status()
            if ret:
                break
        print("TA install success!")

    def filter_install_file(self):
        # Get every file name and path under the same directory.
        dir_list = os.listdir(self.initial_dir)
        ta_buffer_list = []
        firmware_buffer_list = []
        update_tool_buffer_list = []
        for element in dir_list:
            if element.startswith("5G"):
                ta_buffer_list.append(element)
            elif element.startswith('E7515B'):
                firmware_buffer_list.append(element)
                # self.firmware_path = self.initial_dir + '\\' + element
                # self.firmware_ver = element[-15:-4]
            elif element.startswith('UXM5G'):
                update_tool_buffer_list.append(element)
                self.update_tool_filename = element

        if len(ta_buffer_list) == 1:
            self.ta_filename = ta_buffer_list[0]
            self.ta_version = ta_buffer_list[0][-22:-4]
        else:
            print("TA Install file have conflicts, Please select the one you wanna install?: \n")
            for i, element in enumerate(ta_buffer_list, start=1):
                print("{} --{} \n".format(i, element))
            while True:
                user_result = input("Which one you want to install?(Type in Number):")
                try:
                    self.ta_filename = ta_buffer_list[int(user_result) - 1]
                    self.ta_version = ta_buffer_list[int(user_result) - 1][-22:-4]
                    break
                except Exception as e:
                    print("Please Enter integer Only!!")
                    print(str(e) + '\n')
                    print(repr(e) + '\n')
                    # traceback.print_exc()

        if len(firmware_buffer_list) == 1:
            self.firmware_path = firmware_buffer_list[0]
            self.firmware_ver = firmware_buffer_list[0][-15:-4]
        else:
            print("Firmware files have conflicts, Please select the one you wanna install: \n")
            for i, element in enumerate(firmware_buffer_list, start=1):
                print("{} --{} \n".format(i, element))
            while True:
                user_result = input("Which firmware you want to install?(Type in Number):")
                try:
                    self.firmware_path = firmware_buffer_list[int(user_result) - 1]
                    self.firmware_ver = firmware_buffer_list[int(user_result) - 1][-15:-4]
                    break
                except Exception as e:
                    print("Please Enter integer Only!!")
                    print(str(e) + '\n')
                    print(repr(e) + '\n')
                    # traceback.print_exc()
        if self.updatetool_version != '':
            if len(update_tool_buffer_list) == 1:
                version = update_tool_buffer_list[0]
                compared_num_install = int(version[-8:-6])
                compared_num_current = int(self.updatetool_version)
                if compared_num_current >= compared_num_install:
                    self.update_tool_filename = False
                    print("Current Update Tool version is {}, skip uninstall process".format(compared_num_current))
                else:
                    self.update_tool_filename = update_tool_buffer_list[0]
            else:
                print("Update Tool install files have conflicts, Please select the one you wanna install: \n")
                for i, element in enumerate(update_tool_buffer_list, start=1):
                    print("{} --{} \n".format(i, element))
                while True:
                    user_result = input("Which Update Tool you want to install?(Type in Number):")
                    try:
                        version = update_tool_buffer_list[int(user_result) - 1]
                        self.updatetool_overwrite = update_tool_buffer_list[int(user_result) - 1]
                        compared_num_install = int(version[-8:-6])
                        compared_num_current = int(self.updatetool_version)
                        if compared_num_current >= compared_num_install:
                            self.update_tool_filename = False
                            while True:
                                ret = input("Current Update Tool version is {}, You selected version is {}, "
                                            "overwrite uninstall process?(Y/N)".
                                            format(compared_num_current, compared_num_install))
                                if not ret == 'Y' or ret == 'N':
                                    pass
                                if ret == 'Y':
                                    self.update_tool_filename = self.updatetool_overwrite
                                    break
                                if ret == 'N':
                                    break

                        else:
                            self.update_tool_filename = update_tool_buffer_list[int(user_result) - 1]
                        break
                    except Exception as e:
                        print("Please Enter integer Only!!")
                        print(str(e) + '\n')
                        print(repr(e) + '\n')
                        traceback.print_exc()
                        print('\n')
        else:
            if len(update_tool_buffer_list) == 1:
                self.update_tool_filename = update_tool_buffer_list[0]
            else:
                print("Update Tool install files have conflicts, Please select the one you wanna install: \n")
                for i, element in enumerate(update_tool_buffer_list, start=1):
                    print("{} --{} \n".format(i, element))
                while True:
                    user_result = input("Which Update Tool you want to install?(Type in Number):")
                    try:
                        self.update_tool_filename = update_tool_buffer_list[int(user_result) - 1]
                        break
                    except Exception as e:
                        print("Please Enter integer Only!!")
                        print(str(e) + '\n')
                        print(repr(e) + '\n')
                        traceback.print_exc()
                        print('\n')

    def enum(self, **named_values):
        return type('Enum', (), named_values)

    def send_command(self, command, format_command=False, time_out=30):
        if format_command:
            command = '"{}"'.format(command)

        args = shlex.split(command, posix=False)
        # print(args)
        try:
            outs, errors = self.proc.Popen(command, stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, shell=True,
                                           universal_newlines=True).communicate(timeout=time_out)
            print(errors)
            return outs
        except Exception as inst:
            # p.kill()
            print(type(inst))
            print(inst.args)
            print(inst)

    def get_update_toolversion(self):
        print("Checking current Update Tool Version")
        ret = self.send_command('wmic product where \"description=\'Keysight E7515B/E7515E UXM5G Update Tool\'\" '
                                'get version', time_out=50)
        pattern_version = re.compile(r'[-+]?[0-9]*\.?[0-9]+')
        version = pattern_version.findall(ret)
        try:
            self.updatetool_version = version[1].strip('.')
        except Exception:
            print("Update Tool not detected!")
            self.updatetool_version = ""
        pass

    def launch_updatetool_window(self):
        os.chdir(r"C:\Program Files\Keysight\E7515B\UXM 5G Firmware Tool")
        self.send_command("UXM5GUpdateTool.exe -g", time_out=5)

    def update_tool_command(self, move, path=""):
        """
        Send commands to UpdateTool via cmd
        :param move:  'add':Add a specific firmware file to Update Tool
                      'info':send a logging command and get log files under
                       'D:\ProgramData\Keysight\E7515B\' folder
                     'update':Start Update process

        :param path:
        :return:
        """
        path = '"{}"'.format(path)
        if move == "info":
            self.send_command("UXM5GUpdateTool.exe {}".format(self.update_tool_comms.INFO), time_out=5)
        elif move == "add":
            self.send_command("UXM5GUpdateTool.exe {} {}".format(self.update_tool_comms.ADD, path))
        elif move == "update":
            self.send_command("UXM5GUpdateTool.exe {} {}".format(self.update_tool_comms.UPDATE, path))

    def get_update_tool_status(self):
        os.chdir(r"C:\Program Files\Keysight\E7515B\UXM 5G Firmware Tool")
        self.update_tool_command("info")
        time.sleep(3)
        os.chdir(r"D:\ProgramData\Keysight\E7515B")
        # print(os.listdir(os.getcwd()))
        print("Parsing Firmware Install Status...")
        f = open(r'UxmInfoCmdLine.log', 'r', encoding='UTF-8')
        log_content = f.readlines()
        f.close()
        pattern_info = re.compile(r'^((?!Information).)*$')
        result_buffer: List[str] = []
        for lines in log_content:
            if "Information" in lines:
                pass
            else:
                result_buffer.append(lines)
        for i in result_buffer:
            print(i)

        if not result_buffer:
            # print("Update is not finished!")
            return False

        else:
            return True

    def uninstall_upate_tool(self):
        print("Uninstalling UpdateTool")
        comm_list = ['taskkill /F /IM UXM5GUpdateTool.exe /T',
                     'wmic product where \"description=\'Keysight E7515B/E7515E UXM5G Update Tool\'\" uninstall']
        for every_commands in comm_list:
            print(every_commands)
            self.send_command(every_commands, time_out=70)

    def silent_install_update_tool(self):
        print("Installing Update Tool at background")
        os.chdir(self.initial_dir)
        self.send_command('"{}" /S /v/qn'.format(self.update_tool_filename), time_out=70)

    def update_firmware_version(self):
        os.chdir(r"C:\Program Files\Keysight\E7515B\UXM 5G Firmware Tool")
        comm_list = ['taskkill /F /IM TestApp.exe /T',
                     'taskkill /F /IM Agilent.SA.xSA.exe /T']
        for every_commands in comm_list:
            print(every_commands)
            self.send_command(every_commands, time_out=10)
        # self.launch_updatetool_window()
        time.sleep(5)
        self.update_tool_command('add', self.firmware_path)
        time.sleep(10)
        self.update_tool_command('update', self.firmware_ver)
        print("Now please wait for 16 minutes for Firmware update process, And go get a coffee :)")
        print(doge)
        timer = 900
        while True:
            time.sleep(1)
            timer -= 1
            if timer == 0:
                break
        retry_timer = 240
        tick = 0
        while True:
            ret = self.get_update_tool_status()
            tick += 1
            if ret:
                break
            elif tick >= retry_timer:
                break
        print("Firmware Update Success!!")

    def check_firmware_install_status(self):
        retry_timer = 240
        tick = 0
        while True:
            ret = self.get_update_tool_status()
            tick += 1
            if ret:
                break
            elif tick >= retry_timer:
                break
        print("Firmware Update Success!!")



if "__main__" == __name__:
    test_class = FileHandler()
    test_class.read_reg_keys()
    test_class.uninstall_ta()
    time.sleep(40)
    if test_class.update_tool_filename:
        test_class.uninstall_upate_tool()
        test_class.silent_install_update_tool()
    test_class.launch_updatetool_window()
    test_class.update_firmware_version()
    # input("Install Success!!")
    test_class.install_new_ta()