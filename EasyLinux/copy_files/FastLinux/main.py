#!/usr/bin/env python
from tkMessageBox import *
import os
from time import sleep
import pexpect
from datetime import *
from pexpect import pxssh
import copy_update_config
from Tkinter import *
from Tkconstants import *

__author__ = "Yuri Du"
__version__ = '20180820'


class CopyFile(object):
    """
    This is a script for svn update and copying(Broadcasting) files to product machines.
    """
    def __init__(self):
        self.window_buffer = ''
        self.file_name = None
        self.local_path = os.path.dirname(os.path.realpath(__file__)) + '/copy_files'
        self.tk = Tk()
        self.tk1 = Tk()
        self.tk.title('#FastLinux Main Panel#')
        self.tk1.title('Console')
        width = 80
        height = 100
        self.frame = Frame(self.tk, width=width, height=height).grid
        self.img = PhotoImage(file=os.path.dirname(os.path.realpath(__file__))+'/img/tron.gif')
        self.img = self.img.subsample(x=2, y=2)
        self.product = StringVar(self.tk)
        self.product.set('--Select product group--')
        self.address = StringVar(self.tk)
        self.address.set('--Select destination address--')
        self.antigua_machine = StringVar(self.tk)
        self.antigua_machine.set('--Select Antigua machine--')
        self.barbados_machine = StringVar(self.tk)
        self.barbados_machine.set('--Select Barbados machine--')
        self.select_file = StringVar(self.tk)
        self.select_file.set('--Select files--')
        self.ext_machine = StringVar(self.tk)
        self.ext_machine.set('--This is Extension slot--')
        self.entry_bar = StringVar(self.tk)
        self.entry_bar.set('Address/Machines')
        scroll = Scrollbar(self.tk1)
        scroll.activate(index='slider')
        scroll.pack(side=RIGHT, fill=Y)
        self.text = Text(self.tk1, height=80, width=80, yscrollcommand=scroll.set)
        self.text.pack()
        scroll.config(command=self.text.yview())

    def menu_list(self):
        Label(self.tk, text='Product Machine copy & update interface', image=self.img).grid(row=0, column=1)
        Entry(self.tk, textvariable=self.entry_bar).grid(row=1, column=1)
        OptionMenu(self.tk, self.address, *copy_update_config.copy_addr).grid(row=2, column=0)
        OptionMenu(self.tk, self.product, *copy_update_config.product_group).grid(row=2, column=1)
        OptionMenu(self.tk, self.antigua_machine, *copy_update_config.antigua_machine).grid(row=2, column=2)
        OptionMenu(self.tk, self.barbados_machine, *copy_update_config.barbados_machine).grid(row=2, column=3)
        OptionMenu(self.tk, self.select_file, *os.listdir(self.local_path)).grid(row=3, column=0)
        OptionMenu(self.tk, self.ext_machine, *copy_update_config.ext).grid(row=1, column=3)
        self.but_update()
        self.but_exit()
        self.but_copy_product_group()
        self.but_copy_single()
        mainloop()

    def group_transfer(self):
        result = self.product.get()
        probe = result.startswith('--')
        if probe:
            showwarning(title='Warming', message='No product group selected')
        else:
            if result == 'Antigua':
                self.group_copy(copy_list=copy_update_config.antigua_machine)
                self.antigua_machine.set('--Select Antigua machine--')
            elif result == 'Barbados':
                self.group_copy(copy_list=copy_update_config.barbados_machine)
                self.barbados_machine.set('--Select Barbados machine--')
            elif result == 'Extension':
                self.group_copy(copy_list=copy_update_config.ext)
                self.ext_machine.set('--This is Extension slot--')

    def but_update(self):
        Button(self.tk, text='Update', command=self.update_local_single, bg='gold').grid(row=3, column=3)

    def but_exit(self):
        Button(self.tk, text='Exit', command=self.tk.quit, bg='lawn green').grid(row=4, column=3)

    def but_copy_single(self):
        Button(self.tk, text='Copy to Single machine', command=self.copy_local_single, bg='royalblue1')\
            .grid(row=3, column=2)

    def but_copy_product_group(self):
        Button(self.tk, text='Copy to product group', command=self.group_transfer, bg='cyan2').grid(row=3, column=1)

    def new_windows(self, info):
        self.text.insert(END, info)
        self.text.insert(END, '\n')

    def copy_local_single(self):
        antigua = self.antigua_machine.get()
        barbados = self.barbados_machine.get()
        ext = self.ext_machine.get()
        prob1 = antigua.startswith('fxca')
        prob2 = barbados.startswith('fxca')
        prob3 = ext.startswith('fxca')
        if prob1:
            self.copy_commands(des_machine=antigua)
            self.antigua_machine.set('--Select Antigua machine--')
        if prob2:
            self.copy_commands(des_machine=barbados)
            self.barbados_machine.set('--Select Barbados machine--')
        if prob3:
            self.copy_commands(des_machine=ext)
            self.ext_machine.set('--Select Ext Machine--')
        else:
            showwarning(title='Warning', message='No machines selected, Cannot update!')

    def update_local_group(self):
        group = self.product.get()
        if group == 'Antigua':
            self.svn_update_group(machine_list=copy_update_config.antigua_machine)
        if group == 'Barbados':
            self.svn_update_group(machine_list=copy_update_config.barbados_machine)

    def update_local_single(self):
        antigua = self.antigua_machine.get()
        barbados = self.barbados_machine.get()
        ext = self.ext_machine.get()
        entry = self.entry_bar.get()
        prob1 = antigua.startswith('fxca')
        prob2 = barbados.startswith('fxca')
        prob3 = ext.startswith('fxca')
        prob4 = entry.startswith('fxca')
        if prob1:
            self.svn_update(machine=antigua)
        if prob2:
            self.svn_update(machine=barbados)
        if prob3:
            self.svn_update(machine=ext)
        if prob1 and prob2 and prob3 is False:
            self.new_windows(info='No machines selected, Cannot update!')
            showwarning(title='Warning', message='No machines selected, Cannot update!')
        if prob4:
            self.svn_update(machine=entry)

    def copy_commands(self, des_machine):
        file_name = self.select_file.get()
        addr = self.local_path + '/' + file_name
        result = self.address_check(addr=self.address.get())
        if result:
            command = 'scp -r {0} {1}:{2}'.format(addr, des_machine,
                                                  self.address.get())
            child = pexpect.spawn(command)
            index = child.expect(['.*assword:', 'connecting (yes/no)?', pexpect.EOF], timeout=40)
            if index == 0:
                child.sendline(copy_update_config.user_password)
                child.expect(pexpect.EOF)
                child.sendline('\r')
                child.expect(pexpect.EOF)
            elif index == 1:
                child.sendline('yes')
                child.expect(pexpect.EOF)
                child.expect('.*assword:')
                child.sendline(copy_update_config.user_password)
                child.expect(pexpect.EOF)

            self.new_windows(info='Files has been successfully copy to {}'.format(des_machine))
            self.create_logs(machine=des_machine, move='copy files address:{0} -> {1}'.format(addr, self.address.get()))
            self.select_file.set('--Select Files--')
        else:
            pass

    # def svn_checkout(self, machine):

    def svn_update(self, machine):
        addr_check = self.address_check(addr=self.address.get())
        result = askyesno(title='Update warning', message='You are going to update a prod machine. Make sure you '
                                                          'inform your supervisors before!\rYour update path is {}'
                          .format(self.address.get()), default='no')
        if result and addr_check:
            s = pxssh.pxssh()
            s.login(machine, copy_update_config.user_name, copy_update_config.user_password)
            s.sendline('cd {}'.format(self.address.get()))
            s.prompt()
            s.sendline('svn update')
            self.new_windows(info='svn update')
            k = s.expect(['Upda.*', 'Run.*'])
            if k == 1:
                s.sendline('svn cleanup')
                s.prompt()
            g = s.expect(['.*{}\':'.format(copy_update_config.user_name), 'Run.*', pexpect.TIMEOUT])
            s.prompt()
            if g == 0:
                s.sendline(copy_update_config.user_password)
                s.prompt(timeout=120)
                self.new_windows(info=(s.before))
            if g == 1:
                s.sendline('svn cleanup')
                s.expect(pexpect.EOF)
                s.expect('.*assword')
                s.sendline(copy_update_config.user_password)
                s.prompt()
                self.new_windows(info=(s.before))
            i = 0
            while True:
                k = s.expect(['At revi*', pexpect.EOF])
                if k == 0:
                    self.new_windows(info='Svn update complete!')
                    self.create_logs(machine=machine, move='svn update address:{}'.format(self.address.get()))
                    break
                elif k == 1:
                    i += 1
                    if i >= 10:
                        self.new_windows(info='Svn update timeout')
                        showwarning(message='SVN update timeout!! Please use manual update')
                        self.create_logs(machine=machine, move='svn update timeout:{}'.format(self.address.get()))
                        break
                    else:
                        pass
        else:
            self.new_windows(info='Update aborted')
            self.create_logs(machine=machine, move='svn update aborted')

    def svn_update_group(self, machine_list):
        for i in range(1, len(machine_list)):
            self.svn_update(machine=machine_list[i])

    def address_check(self, addr=None):
        result = addr.startswith('/')
        if result:
            return True
        else:
            showwarning(title='address hazard', message='Illegal address, Plz refill it')
            self.new_windows(info='Cannot process. Illegal address!')

    def group_copy(self, copy_list=[]):
        for i in range(1, len(copy_list)):
            self.new_windows(info=copy_list[i])
            self.copy_commands(des_machine=copy_list[i])
        showinfo(title='Mission Finish', message='Copy finish! Totally {} machines'.format(len(copy_list)-1))

    @staticmethod
    def create_logs(machine, move):
        timestamp = str(datetime.now())
        f = open('linux_log.txt', 'a+')
        f.write(timestamp+' '+machine + ' ' + move + '\n')
        f.close()


def main():
    c = CopyFile()
    c.menu_list()


if __name__ == '__main__':
    main()
