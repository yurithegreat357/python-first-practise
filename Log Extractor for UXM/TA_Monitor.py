import os
from threading import Thread
from datetime import datetime
from pyvisa import *
import shutil
import time
import zipfile
from tkinter import messagebox
import winreg as reg

__author__ = "Yuri Du"
__date__ = "2020/07/06"
# HCCU Export Log
# SYSTem:EXPortlog "C:\Temp\{setup}\systemlogs {date} {time} {status}.zip"
# SYSTem:CLEAnlog
# HCCU Log Path: C:\TEMP\TSPC_1eUXM5G_LF


class LogExtractor:
    def __init__(self):
        date_time_obj = datetime.now()
        root_dir = r"D:\LogExtractor"
        self.timestamp_str = date_time_obj.strftime("%b%d%Y%H%M")
        self.log_path = r"C:\ProgramData\Keysight\5GTA\Logs\\"
        self.log_file_list = os.listdir(self.log_path)
        self.copied_path = r"D:\LogExtractor\LogResultAssert_" + self.timestamp_str
        self.hccu_log_path = r'C:\TEMP\TSPC_1eUXM5G_LF\\'
        self.add_to_registry()
        if not os.path.exists(root_dir):
            os.mkdir(root_dir)
        try:
            os.mkdir(self.copied_path)
        except OSError:
            print("Creation of the directory %s failed" % self.copied_path)
        else:
            print("Successfully created the directory %s " % self.copied_path)
        ret_list = os.listdir(root_dir)

        if len(ret_list) >= 50:
            messagebox.showwarning(title="警告", message="LOG数量已超过50个，请叫工程师来拷贝{} "
                                                       "下的log并删除多余的LOG以释放空间！！"
                                   .format(root_dir))

    def remove_copied_path(self):
        shutil.rmtree(self.copied_path, ignore_errors=True)

    def check_hccu_directory(self):
        """Check out the HCCU log path to clean up the file storage"""
        ret_list = os.listdir(self.hccu_log_path)
        if len(ret_list) >= 10:
            print("HCCU log files count exceed 10, cleanup process started")
            for every_file in ret_list:
                os.remove(self.hccu_log_path + every_file)
                print("Cleaning up HCCU log file {}".format(every_file))

    def copy_hccu_logs(self):
        instr = HCCUInstrument()
        instr.logger = logging.getLogger("Main.HCCU")
        instr.open("TCPIP0::{}::hislipHCCU::INSTR".format("127.0.0.1"))
        instr.send(r'SYSTem:EXPortlog "C:\Temp\{setup}\systemlogs {date} {time} {status}.zip"')
        # time.sleep(120)
        file_list = os.listdir(self.hccu_log_path)
        extracted_file_name = file_list[len(file_list) - 1]
        print("Copying HCCU log from {} to {}".format(self.hccu_log_path + extracted_file_name, self.copied_path))
        shutil.copy(self.hccu_log_path + extracted_file_name, self.copied_path)
        instr.send(r"SYSTem:CLEAnlog")
        instr.terminate()

    def extract_ta_log(self):
        matching = [s for s in self.log_file_list if "Assert-Host" in s]
        if matching:
            print("Assert Logs Found!!")
            t = Thread(target=self.copy_hccu_logs)
            t.start()
            copy_list = []
            for every_file in self.log_file_list:
                if 'Archive' in every_file or 'PersistentErrors' in every_file:
                    pass
                else:
                    copy_list.append(every_file)
            print(copy_list)
            for element in copy_list:
                source_path = self.log_path + element
                shutil.copy(source_path, self.copied_path)
                print("Copying {} to {}".format(source_path, self.copied_path))
            t.join()
            return True
        else:
            return False

    def compress_file(self):
        def zipdir(filepath, ziph):
            # ziph is zipfile handle
            for root, dirs, files in os.walk(filepath):
                for file in files:
                    ziph.write(os.path.join(root, file))
        zipf = zipfile.ZipFile('{}.zip'.format(self.copied_path), 'w', zipfile.ZIP_DEFLATED)
        print("Compressing Files, Please wait")
        zipdir(self.copied_path, zipf)
        zipf.close()
        self.remove_copied_path()

    @staticmethod
    def add_to_registry(remove_key=False):
        # in python __file__ is the instant of
        # file path where it was executed
        # so if it was executed from desktop,
        # then __file__ will be
        # c:\users\current_user\desktop
        pth = os.path.dirname(os.path.realpath(__file__))

        # name of the python file with extension
        s_name = "TA_Monitor.py"

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


class InstrumentBase:
    def __init__(self):
        self.instr = None
        self.IsConnected = False
        self.logger = None
        self.IDN = None
        pass

    def open(self, address):
        rm = ResourceManager()
        self.instr = rm.open_resource(address)
        self.IsConnected = True
        self.IDN = self.query("*IDN?")

    def terminate(self):
        self.instr.close()

    def send(self, command):
        self.logger.debug("SCPI>> {}".format(command))
        self.instr.write(command)
        pass

    def query(self, command):
        self.logger.debug("SCPI>> {}".format(command))
        res = self.instr.query(command)
        self.logger.debug("SCPI<< {}".format(res))
        return res
        pass

    def query_list(self, message, convert='f'):
        return self.instr.query_ascii_values(message, convert)

    def wait_for_opc(self):
        self.query("*OPC?")


class HCCUInstrument(InstrumentBase):

    def __init__(self):
        super().__init__()
        pass

    def resume_after_crash(self):
        # C:\ProgramFiles(x86)\Keysight\5GTA\TestApp.exe
        # start "" "C:\Program Files (x86)\Keysight\5GTA\TestApp.exe"
        state_value = self.query(":SYSTem:STATus?")
        if "OPER" not in state_value:
            print("HCCU is not in Operational Status, Resetting....")
            self.hccu_reset(False)
        else:
            os.popen(r'start "" "C:\Program Files (x86)\Keysight\5GTA\TestApp.exe"')

    def hccu_reset(self, first_start_flag):
        if not first_start_flag:
            self.send(":SYSTem:HRESet")
        counter = 600
        while True:
            return_status = self.query(":SYSTem:STATus?")
            if counter == 0:
                self.send(":SYSTem:RESTart")
            if "OPER" in return_status:
                os.popen(r'start "" "C:\Program Files (x86)\Keysight\5GTA\TestApp.exe"')
                break
            else:
                print("HCCU is not Operational, The Current state is {}, Restarting in {} seconds"
                      .format(return_status, counter))
                time.sleep(1)
                counter -= 1


if __name__ == '__main__':
    # log_handle = LogExtractor()
    # ret = log_handle.extract_ta_log()
    # if ret:
    #     log_handle.copy_hccu_logs()
    #     log_handle.compress_file()
    #     print("Log extraction finished")
    #
    log_flag = True
    first_start = True
    while True:
        print("Parsing TA status")
        ret = os.popen('tasklist').read()
        if 'TestApp' in ret and not log_flag:
            log_flag = True
        if 'TestApp' in ret and log_flag:
            print("TA is running......")
            first_start = False
            time.sleep(10)
        else:
            if log_flag:
                hccu_handle = HCCUInstrument()
                hccu_handle.logger = logging.getLogger("Main.HCCU")
                hccu_handle.open("TCPIP0::{}::hislipHCCU::INSTR".format("127.0.0.1"))
                log_handle = LogExtractor()
                ret = log_handle.extract_ta_log()
                if ret:
                    # log_handle.copy_hccu_logs()
                    log_handle.compress_file()
                    print("Log extraction finished")
                    log_handle.check_hccu_directory()
                    log_flag = False
                    hccu_handle.resume_after_crash()
                else:
                    log_handle.remove_copied_path()
                    print("Assert Logs not found. Waiting for TA to restart")
                    if first_start:
                        hccu_handle.hccu_reset(first_start)
                    else:
                        hccu_handle.resume_after_crash()
                    time.sleep(10)
            else:
                print("Assert log has been captured, Waiting for TA to restart")
                time.sleep(10)
