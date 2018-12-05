from SimpleXMLRPCServer import SimpleXMLRPCServer
import tkMessageBox
import imp
import os
import shutil
import errno
from dll_exec import *
from threading import *
from Tkinter import *


class ApolloCommUI(object):
    def __init__(self):
        self.host = '1.1.1.1'
        self.port = 9997
        self.tk = Tk()
        self.tk.title('#Apollo comm#')
        width = 80
        height = 100
        self.frame = Frame(self.tk, width=width, height=height).grid
        self.host_cache = StringVar()
        self.port_cache = StringVar()
        self.file_io(mode='r')
        self.file_name_list = ['AOA_cal_step_param', 'test_logs', 'dll_libs', 'pm2_step_param', 'station_cal_step_param',
                               'station_param', 'station_script', 'product_def', 'test_results', 'global']

    def menu_list(self):
        Label(self.tk, text='IP address:').grid(row=1, column=1)
        Label(self.tk, text='Listening port:').grid(row=2, column=1)
        Entry(self.tk, textvariable=self.host_cache).grid(row=1, column=3)
        Entry(self.tk, textvariable=self.port_cache).grid(row=2, column=3)
        self.but_connect()
        self.but_build_file()
        self.but_shutdown()
        mainloop()

    def set_up_server(self):
        # register a function to respond to XML-RPC requests and start XML-RPC server
        self.file_io(mode='w')
        server = SimpleXMLRPCServer((self.host_cache.get(), int(self.port_cache.get())))
        try:
            # foo = imp.load_source('LabViewCtrl', r'C:\pm2_config\station_script\dll_exec.py')
            print "Server {0} Listening on port {1}...".format(self.host_cache.get(), self.port_cache.get())
            server.register_instance(LabViewCtrl())
            server.serve_forever()
        except IOError:
            tkMessageBox.showwarning(title='Cannot start server', message='dll_exec.py not exist. '
                                                                          'Make sure you put it in the '
                                                                          'C:\pm2_config\station_script')
            self.tk.quit()

    def build_folders(self):
        root_dir = 'C:\pm2_config'
        if tkMessageBox.askyesno(title='Warning', message='Are you sure you want to build file path?'
                                                          'All existing files will be replaced!'):
            if os.path.isdir(root_dir):
                shutil.rmtree(root_dir)
            try:
                os.mkdir(root_dir)
                for elements in self.file_name_list:
                    os.mkdir('{}\{}'.format(root_dir, elements))
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            tkMessageBox.showinfo(title='Congratulation', message='Build path finished!')
        else:
            tkMessageBox.showwarning(title='FrenchBullDog', message='Building path process aborted')

    def file_io(self, mode=None):
        if mode == 'r':
            try:
                f = open('saved_address.txt', 'r')
                cache = f.readlines()
                modified = cache[0].split('\n')
                self.host_cache.set(modified[0])
                self.port_cache.set(cache[1])
            except IOError:
                f = open('saved_address.txt', 'w')
                f.write('192.168.1.1\n' + '9007')
                f.close()
                self.host_cache.set('192.168.1.1')
                self.port_cache.set(str(9007))
        if mode == 'w':
            f = open('saved_address.txt', 'w')
            f.write('{}'.format(self.host_cache.get()) + '\n' + self.port_cache.get())
            f.close()

    def but_connect(self):
        Button(self.tk, text='Start Server', command=self.set_up_server).grid(row=3, column=1)

    def but_build_file(self):
        Button(self.tk, text='Build File Path', command=self.build_folders).grid(row=3, column=2)

    def but_shutdown(self):
        Button(self.tk, text='Exit', command=self.tk.quit).grid(row=3, column=3)

    def server_thread(self):
        t = Thread(target=self.parse_shutdown)
        t.start()
        self.set_up_server()
        t.join()


def main():
    c = ApolloCommUI()
    c.menu_list()


if __name__ == '__main__':
    main()
