import pexpect
import os
from datetime import *
import subprocess

user_name = 'blaze'
password = 'Cisco20180.'

command = '/opt/cisco/te/scripts/projects/wnbu/trunk/product_group_1/barbados/'
os.chdir('/opt/cisco/te/scripts/projects/wnbu/trunk/product_group_1/barbados/')
g = command.split('/')
print g
print len(g)
neo_command = ''
for i in range(0, len(g)-2):
    neo_command += g[i] + '/'
print neo_command
print g[len(g)-2]
timestamp = str(datetime.now())
print timestamp
# s = pexpect.spawn('svn update')
# s.expect('Upda.*',)
# print (s.before)
# g = s.expect(['.*assword', 'Run.*', pexpect.EOF])
# print g
# if g == 0:
#     s.sendline(password)
#     s.sendline('\r')
#     s.expect(pexpect.EOF)
#     result = s.before
#     print result
# elif g == 1:
#     s.sendline('svn cleanup')
#     s.expect(pexpect.EOF)
#     s.expect('.*assword')
#     s.sendline(password)
#     # print (s.before)
# h = s.expect(['Updated.*', 'At.*', pexpect.EOF])




