import pyvisa
import time
from tkinter import messagebox
__author__ = "Yuri Du o W o"
__date__ = "2020/3/20"

#   Please Install "pyvisa" package before running this script. Compatible under python 3.6.2 version
#   Type UXM address here
instrument_address = "10.74.21.166"


class InstrumentTalker:
    # This class is used to communicate with instruments
    def __init__(self):
        self.instr_handle1 = self.init_visa()
        print(self.query("*IDN?"))

    def close(self):
        self.instr_handle1.close()

    def init_visa(self):
        print("=======Initiating Visa resources========")
        rm = pyvisa.ResourceManager()
        print(rm.list_resources())
        my_instr = rm.open_resource('TCPIP0::{}::hislip2::INSTR'.format(instrument_address))
        my_instr.timeout = 10000
        return my_instr

    def apply_changes(self, cell="NR"):
        if cell == "NR":
            self.write("BSE:CONFig:NR5G:CELL1:APPLY")
        else:
            self.write("BSE:CONFig:LTE:CELL1:APPLY")

    def run_scpi(self, command):
        if command.endswith("?"):
            ret = self.query(command)
            if "OPC" in command and ret != "1\n":
                print("Check!!!")
                # raise Exception("OPC is not finished!")
            else:
                print(ret)
                return ret
        else:
            return self.write(command)

    def query(self, command):
        print(command + '\n')
        retry_counter = 0
        while True:
            try:
                ret = self.instr_handle1.query(command, 8)
                return ret.strip("\n")
            except pyvisa.errors.VisaIOError:
                retry_counter += 1
                time.sleep(15)
                if retry_counter >= 5:
                    raise Exception("Query Fail!")
                else:
                    continue

    def write(self, command):
        print(command + '\n')
        try:
            self.instr_handle1.write(command)
        except:
            print("Something wrong with the VISA write")

    def parse_connection_status(self):
        print("Let's see what's going on here? (´・ω・`)")
        lte_status = instr.query("BSE:STATus:LTE:CELL1?")
        nr_status = instr.query("BSE:STATus:NR5G:CELL1?")
        if lte_status != "CONN":
            return "1"
        elif nr_status != "CONN":
            return "2"


if "__main__" == __name__:
    while True:
        instr = InstrumentTalker()
        ret = instr.parse_connection_status()
        if ret == "1":
            #   Turn on both LTE & NR RRC timer
            scpi_list = ["BSE:CONFig:LTE:CELL1:RRC:CTIMer 1",
                         "BSE:CONFig:NR5G:ALL:STATus:MONItoring 1",
                         "BSE:CONFig:NR5G:DL:POWer:EPRE:DBmBw -0.500000000E+02",
                         "BSE:CONFig:NR5G:CELL1:APPLY",
                         "BSE:CONFig:LTE:CELL1:APPLY",
                         ]
            for i in scpi_list:
                instr.write(i)
            #   Toggle Flight mode to reconnect
            messagebox.showwarning("Flight mode", "Please turn off and then turn on flight mode")
            #   Re-aggregate to NR
            scpi_list2 = ["BSE:CONFig:LTE:CELL1:CAGGregation:NRCC:DL  CELL1",
                          "BSE:CONFig:LTE:CELL1:CAGGregation:NRCC:APPly"]
            for i in scpi_list2:
                instr.write(i)
            counter = 0
            while True:
                if counter >= 2:
                    print("Reconnect Fail, Please check your UE or restart TA")
                    if messagebox.askyesno("Oops", "Cell connection resume Fail,Please try restarting TA. "
                                                   "Or select NO to do it again :)"):
                        break
                    else:
                        counter = 0
                else:
                    time.sleep(5)
                    counter += 1
                    if instr.query("BSE:STATus:NR5G:CELL1?") and instr.query("BSE:STATus:LTE:CELL1?") != "CONN":
                        messagebox.showwarning("Flight mode", "Please turn off and then turn on flight mode")
                        time.sleep(5)
                        #   retry to aggregate NR cell
                        if instr.query("BSE:STATus:LTE:CELL1?") == "CONN":
                            scpi_list3 = ["BSE:CONFig:NR5G:DL:POWer:EPRE:DBmBw -0.{}00000000E+02".format(5-counter),
                                          "BSE:CONFig:NR5G:CELL1:APPLY",
                                          "BSE:CONFig:LTE:CELL1:CAGGregation:NRCC:DL CELL1",
                                          "BSE:CONFig:LTE:CELL1:CAGGregation:NRCC:APPly"]
                            for f in scpi_list3:
                                instr.write(f)
                            break
                    else:
                        break
        elif ret == "2":
            scpi_list = ["BSE:CONFig:LTE:CELL1:RRC:CTIMer 1",
                         "BSE:CONFig:NR5G:ALL:STATus:MONItoring 1",
                         "BSE:CONFig:NR5G:DL:POWer:EPRE:DBmBw -0.500000000E+02",
                         "BSE:CONFig:NR5G:CELL1:APPLY",
                         "BSE:CONFig:LTE:CELL1:APPLY",
                         ]
            for i in scpi_list:
                instr.write(i)
            scpi_list2 = ["BSE:CONFig:LTE:CELL1:CAGGregation:NRCC:DL CELL1",
                          "BSE:CONFig:LTE:CELL1:CAGGregation:NRCC:APPly"]
            for i in scpi_list2:
                instr.write(i)
            counter = 0
            while True:
                if counter >= 3:
                    print("Reconnect Fail, Please check your UE or restart TA")
                    if messagebox.askyesno("Oops", "Cell connection resume Fail,Please try restarting TA. "
                                                   "Or select NO to do it again :)"):
                        break
                    else:
                        counter = 0
                else:
                    time.sleep(5)
                    counter += 1
                    if instr.query("BSE:STATus:NR5G:CELL1?") != "CONN":
                        messagebox.showwarning("Flight mode", "Please turn off and then turn on flight mode")
                        time.sleep(5)
                        #   retry to aggregate NR cell
                        if instr.query("BSE:STATus:LTE:CELL1?") == "CONN":
                            scpi_list3 = ["BSE:CONFig:NR5G:DL:POWer:EPRE:DBmBw -0.{}00000000E+02".format(5-counter),
                                          "BSE:CONFig:NR5G:CELL1:APPLY",
                                          "BSE:CONFig:LTE:CELL1:CAGGregation:NRCC:DL  CELL1",
                                          "BSE:CONFig:LTE:CELL1:CAGGregation:NRCC:APPly"]
                            for f in scpi_list3:
                                instr.write(f)
                    else:
                        break
        instr.close()
