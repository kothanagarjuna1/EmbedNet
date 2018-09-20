#!/usr/local/bin/python3

import serial
import sys
import time
import os
import pexpect.fdpexpect
import pexpect
import socket
import shutil
import subprocess
#import numpy
import re
from time import gmtime, strftime

showtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())

#syntax

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>" )
 return

if len(sys.argv) < 1:
    script_usage()
    sys.exit()

device_ip = sys.argv[1]
script_path = "/home/lantronix/MIDAS/xml"

def reboot():
  print str(showtime) + "\t reboot for changes to take effect"
  reb = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")
  res = re.search('Rebooting',reb)
  if res:

   time.sleep(60)
  else:
   print str(showtime) + "\t failed to reboot"

def xml():
  print str(showtime) + "\t import cert and keys"
  pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+script_path+"cert.xml")
  time.sleep(5)
  #reboot()


def httpServer():
   xml()
   print str(showtime) + "\t telnet to device.set http server mode as enable"
   deviceid = pexpect.spawn('telnet '+device_ip)
   time.sleep(5)
   deviceid.sendline('config')
   deviceid.sendline('http server')
   deviceid.sendline('mode enabled')
   deviceid.sendline('write')
   reboot()
   print str(showtime) + "\t telnet to device"
   deviceid = pexpect.spawn('telnet '+device_ip)
   time.sleep(5)
  #conn = pexpect.run('telnet '+device_ip+' '+'80')
  #http_conn = re.search('Connected to '+device_ip,conn)
   exportStatus = pexpect.run("curl --digest -u admin:PASSWORD http://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
   #print exportStatus
   exportStatus_s = pexpect.run("curl --anyauth -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
   device_stat = re.search('Y4',exportStatus)
   device_stat_s = re.search('Y4',exportStatus_s)
   print "aaaaaaaaaa" + str(device_stat)
   print "bbbbbbbbbb" + str(device_stat_s)
   if device_stat and device_stat_s:
     print str(showtime) + "\t connected to webm. http server mode always test PASSED"
   else:
     print str(showtime) + "\t failed to connect to webm. http server mode always test FAILED"
   print str(showtime) + "\t set http server mode as trigger"
   deviceid.sendline('config')
   deviceid.sendline('http server')
   deviceid.sendline('mode triggered')
   deviceid.sendline('write')
   reboot()
   exportStatus = pexpect.run("curl --digest -u admin:PASSWORD http://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
   #print exportStatus
   http_trigger = re.search('Connection refused',exportStatus)
   if http_trigger:
     print str(showtime) + "\t failed to connect to webm. HTTP Trigger test PASSED.Trigger http server" 
     clientid = pexpect.spawn('telnet '+device_ip)
     time.sleep(5)
     clientid.sendline('\r')
     clientid.sendline('\r')
     clientid.sendline('status')
     clientid.expect('status')
     clientid.sendline('cpm')
     clientid.expect('status CPM')
     clientid.sendline('roles')
     clientid.expect('status CPM Roles')
     clientid.sendline('role http server trigger')
     clientid.sendline('state active')
     time.sleep(5)
     print str(showtime) + "\t connect to webm after triggering http server"
     exportStatus = pexpect.run("curl --digest -u admin:PASSWORD http://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
     #print exportStatus
     exportStatus_s = pexpect.run("curl --anyauth -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
     #print exportStatus_s
     device_stat = re.search('Y4',exportStatus)
     device_stat_s = re.search('Y4',exportStatus_s)
     if device_stat and device_stat_s:
      print str(showtime) + "\t connected to webm after http server trigger. http server mode trigger test PASSED"
     else:
      print str(showtime) + "\t failed to connect to webm after http server trigger. http server mode trigger test FAILED"

  
   
#main program 
#xml()
httpServer()

sys.exit()

#subprocess.call("python /home/LtrxEngr/check.py",shell = True)
