#!/usr/local/bin/python3

import serial
import sys
import time
import os
#import fdpexpect
import pexpect.fdpexpect
import pexpect
import socket
import shutil
import subprocess
import re
#import requests

print "Test CLI Server"
print "==============="

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>")
 return

if len(sys.argv) < 1:
    script_usage()
    sys.exit()

device_ip = sys.argv[1]

xml_path = "/home/ltrxengr/xpw/xml/" 

def reboot():
 print "reboot device for changes to take effect"
 pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")
 print "device is rebooting"
 time.sleep(30)


def cli_server():
 reboot()
 clientid = pexpect.spawn('telnet '+device_ip)
 time.sleep(4)
 clientid.sendline('config')
 clientid.sendline('cli server')
 clientid.sendline('telnet')
 print "change telnet port number"
 clientid.sendline('port 100\r')
 time.sleep(4)
 clientid.sendline('okay')
 time.sleep(10)
 clientid.close()
 #clientid.sendline('exit')
 #clientid.sendline('exit') 
 #t = pexpect.run('telnet '+device_ip+' 100')
#print t
 clientid = pexpect.spawn('telnet '+device_ip+' 100')
 time.sleep(3)
 t_res = clientid.expect('>')
 #t_res = re.search('>',t)
 if t_res == 0:
    print "can telnet to device after changing port number"
    print "set inactivity timeout" 
    clientid.sendline('config')
    clientid.sendline('cli server')
    clientid.sendline('inactivity timeout 1\r')
    time.sleep(65)
    clientid = pexpect.spawn('telnet '+device_ip+' 100')
    time.sleep(3)
    tel_conn = clientid.expect('>')
    if tel_conn == 0:
      print "can telnet to device after inactivity timeout expired"
      print "Test Case CLI Server PASSED"
    else:
      print "Test Case CLI Server FAILED"
 else:
   print "cannot telnet to device after changing port number.Test Case CLI Server FAILED" 
    
               
cli_server()
 

#end
sys.exit()

