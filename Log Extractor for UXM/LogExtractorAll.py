#! /usr/bin/python
# -*- coding: utf-8 -*-
import os
import pathlib
from datetime import datetime
import shutil
import time
import zipfile

dateTimeObj = datetime.now()
timestampStr = dateTimeObj.strftime("%b%d%Y%H%M")
ta_log_path = r"C:\ProgramData\Keysight\5GTA\Logs\Archive"
file_list = os.listdir(ta_log_path)
path = r"\LogResult" + timestampStr
current = pathlib.Path(__file__).parent.absolute()
filtered_logs = str(current) + path
try:
    shutil.rmtree(r'C:\\ProgramData\\Keysight\\5GTA\Logs\\Archive_bk')
except OSError:
    print("Removal of the directory %s failed" % r"C:\ProgramData\Keysight\5GTA\Logs\Archive_bk")
else:
    print("Successfully remove the directory %s " % r"C:\ProgramData\Keysight\5GTA\Logs\Archive_bk")
shutil.copytree(ta_log_path, r"C:\ProgramData\Keysight\5GTA\Logs\Archive_bk")

try:
    os.mkdir(filtered_logs)
except OSError:
    print("Directory %s Already exist" % str(current) + path)
else:
    print("Successfully created the directory %s " % str(current) + path)


def sort_alf_func(e):
    return e


def zipdir(filepath, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(filepath):
        for file in files:
            ziph.write(os.path.join(root, file))


file_counter = 1
for every_file in file_list:
    file_container = os.listdir(ta_log_path + "\\" + every_file)
    # matching = [s for s in file_container if "Assert-Host" in s]
    currentFolder_path = ta_log_path + "\\" + every_file
    alf_sort_list = []
    filecopy_list = []
    for i in file_container:
        # if i.endswith(".alf"):
        #     alf_sort_list.append(i)
        #     test_value = i[20:-3]
        # else:
        filecopy_list.append(i)
    # alf_sort_list.sort(key=sort_alf_func)
    if alf_sort_list:
        file_size1 = pathlib.Path(currentFolder_path + "\\{}".
                                  format(alf_sort_list[len(alf_sort_list)-1])).stat().st_size
        file_size2 = pathlib.Path(currentFolder_path + "\\{}".
                                  format(alf_sort_list[len(alf_sort_list) - 2])).stat().st_size
        if file_size1 > file_size2:
            filecopy_list.append(alf_sort_list[len(alf_sort_list) - 1])
        else:
            filecopy_list.append(alf_sort_list[len(alf_sort_list)-1])
            filecopy_list.append(alf_sort_list[len(alf_sort_list) - 2])
        filecopy_list.append(alf_sort_list[0])
    copy_destination = filtered_logs + "\\" + str(file_counter)
    os.mkdir(copy_destination)
    for elements in filecopy_list:
        try:
            shutil.copy(currentFolder_path + "\\{}".format(elements), copy_destination)
        except PermissionError:
            print("Copying {} has errors, skipping".format(currentFolder_path + "\\{}".format(elements)))
    file_counter += 1
print("Log extraction finished!!")
print("now Compressing files")
current_folder_item = os.listdir(str(current))
for item in current_folder_item:
    if item.startswith("LogResult"):
        if not item.endswith(".zip"):
            zipf = zipfile.ZipFile('{}.zip'.format(item), 'w', zipfile.ZIP_DEFLATED)
            print("Creating zip file {}.zip at {}".format(item, str(current)+"\\" + item))
            zipdir(item, zipf)
            zipf.close()
            shutil.rmtree(str(current)+"\\" + item, ignore_errors=True)
print("All works finished!!")
time.sleep(3)

