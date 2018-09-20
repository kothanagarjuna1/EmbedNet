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
from time import gmtime, strftime

showtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())

#syntax

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>")
 return

if len(sys.argv) < 1:
    script_usage()
    sys.exit()

device_ip = sys.argv[1]

print str(showtime) + "\t Test Clock Source - manual and ntp"

def telnetDevice():
  clientid = pexpect.spawn('telnet '+device_ip)
  time.sleep(2)
  clientid.sendline('\r')
  clientid.sendline('\r')


def device_config():
  print str(showtime) + "\t Test clock source manual"
  clientid = pexpect.spawn('telnet '+device_ip)
  time.sleep(2)
  clientid.sendline('\r')
  clientid.sendline('\r') 
  clientid.sendline('config\r')
  clientid.expect('config')
  clientid.sendline('clock\r')
  clientid.sendline('source manual')
  clientid.sendline('exit')
  clientid.sendline('exit')
  clientid.sendline('status')
  clientid.sendline('clock')
  clientid.sendline('current Time 2016-09-09 18:12:34')
  time.sleep(4)
  clientid.sendline('show')
  current_time = clientid.expect('Current Time: 2016-09-09 18')
  if current_time == 0:
   print str(showtime) + "\t clock set correctly.clock source manual test passed"
  else:
   print str(showtime) + "\t failed to set time. clock source manual test failed"
  print str(showtime) + "\t Test clock source NTP"
  clientid.sendline('exit')
  clientid.sendline('exit')
  clientid.sendline('config')
  clientid.sendline('clock')
  time.sleep(5)
  clientid.sendline('source ntp')
  time.sleep(4)
  clientid.sendline('write')
  clientid.sendline('exit')
  clientid.sendline('exit')
  clientid.sendline('tlog')
  time.sleep(5)
  ntp = clientid.expect(['Starting NTP'])
  if ntp == 0:
    print str(showtime) + "\t ntp running"
    time.sleep(10)
    clientid.sendline('tlog')
    time.sleep(5)
    sync = clientid.expect(['Updating time'])
    if sync == 0:
     print str(showtime) + "\t device synchronised with ntp server.TEST CASE PASSED"
     #print "test ntp sync time default 10 min"
     #print "reboot device"
     #reb = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")
     #print reb
     #time.sleep(60)
     #clientid = pexpect.spawn('telnet '+device_ip)
     #time.sleep(2)
     #clientid.sendline('\r')
     #clientid.sendline('\r')
     #clientid.sendline('config')
     #clientid.sendline('ntp')
    # clientid.sendline('sync time 10 min')
     #print "wait for sync time to expire.sleep 10 min"
     #time.sleep(605)
     #clientid.sendline('exit')
     #clientid.sendline('exit')
     #clientid.sendline('tlog')
     #sync = clientid.expect(['Updating time'])
     #if sync == 0:
      #print "device synchronised with ntp server after sync time.test passed"
     #else:
      #print "failed to synchronise with ntp server after sync time.test failed"
    else:
      print str(showtime) + "\t failed to synchronise with ntp server.test failed"
  else:
     print str(showtime) + "\t ntp server not running"
     sys.exit()


#main
device_config()

sys.exit()

