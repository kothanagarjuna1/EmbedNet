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

print "Test Radio"
print "========="

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>" + " <wlanprofile_24ghz> " + " <wlanprofile_5ghz> ")
 return

if len(sys.argv) < 3:
    script_usage()
    sys.exit()

device_ip = sys.argv[1]
wlanprofile_24ghz = sys.argv[2]
wlanprofile_5ghz = sys.argv[3]

xml_path = "/home/lantronix/MIDAS/xml/" 

def reboot():
 print "reboot device for changes to take effect"
 pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")
 print "device is rebooting"
 time.sleep(30)


def radio():
 clientid = pexpect.spawn('telnet '+device_ip)
 time.sleep(4)
 clientid.sendline('config')
 clientid.sendline('radio')
 clientid.sendline('band 2.4 ghz')
 clientid.sendline('write')
 reboot()
 clientid = pexpect.spawn('telnet '+device_ip)
 time.sleep(4)
 print "delete all wlan profiles"
 d = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"deletewlanprofiles.xml")
 print d
 print "try connecting to wlan profile in 5ghz"
 print "try 1"
 clientid.sendline('config')
 clientid.sendline('wlan connect {0}'.format(wlanprofile_5ghz))
 time.sleep(4)
 t1 = clientid.expect('ERROR')
 time.sleep(4)
 print "try 2"
 clientid.sendline('config')
 clientid.sendline('wlan connect {0}'.format(wlanprofile_5ghz))
 time.sleep(4)
 t2 = clientid.expect('ERROR')
 time.sleep(4)
 print "try 3"
 clientid.sendline('config')
 clientid.sendline('wlan connect {0}'.format(wlanprofile_5ghz))
 time.sleep(4)
 t3 = clientid.expect('ERROR')
 time.sleep(4)
 if t1 == 0 and t2 == 0 and t3 == 0:
  print "wlan profile "+wlanprofile_5ghz+" not found in scan."
  scan24_res = 1
  time.sleep(6)
  print "try connecting to wlan profile in 2.4"
  clientid.sendline('wlan connect {0}'.format(wlanprofile_24ghz))
  scan_24 = clientid.expect(['Password:','ERROR'])
  if scan_24 == 0:
   print "wlan profile "+wlanprofile_24ghz+" found in scan.test case radio band 2.4 ghz only passed."
  elif scan_24 == 1:
   print "wlan profile "+wlanprofile_24ghz+" not found in scan.retry"
   time.sleep (4)
   clientid.sendline('wlan connect {0}'.format(wlanprofile_24ghz))
   scan_24 = clientid.expect('Password:')
   if scan_24 == 0:
    print "wlan profile "+wlanprofile_24ghz+" 2.4 ghz found in scan.test case radio band 2.4 ghz only passed "
    scan24_res = 1
   else:
    print "wlan profile "+wlanprofile_24ghz+" 2.4 ghz not found in scan"
    scan24_res = 0
    sys.exit()
 else:
  print "wlan profile "+wlanprofile_5ghz+" in 5 ghz found in scan.test case radio band 5 ghz only failed."
  sys.exit()
 print "change radio band to 5ghz"
 clientid.sendline('\r')
 clientid.sendline('\r')
 clientid.expect('config')
 clientid.sendline('radio')
 time.sleep(3)
 clientid.expect('config')
 clientid.sendline('band 5 ghz')
 time.sleep(3)
 clientid.sendline('write')
 time.sleep(3)
 reboot()
 clientid = pexpect.spawn('telnet '+device_ip)
 time.sleep(4)
 clientid.sendline('config')
 clientid.sendline('wlan connect {0}'.format(wlanprofile_5ghz))
 scan_5 = clientid.expect(['Password:','ERROR'])
 if scan_5 == 0:
   print "wlan profile "+wlanprofile_5ghz+" found in scan."
   scan5_res = 1
 elif scan_5 == 1:
   print "retry"
   time.sleep (4)
   clientid.sendline('wlan connect {0}'.format(wlanprofile_5ghz))
   scan_5 = clientid.expect(['Password:','ERROR'])
   if scan_5 == 0:
    print "wlan profile "+wlanprofile_5ghz+" 5 ghz found in scan"
    scan5_res = 1
    clientid.sendline('wlan connect {0}'.format(wlanprofile_24ghz))
    time.sleep(4)
    scan_24 = clientid.expect('ERROR')
    if scan_24 == 0:
      print "wlan profile "+wlanprofile_24ghz+" not found in scan. test case radio band 5ghz only passed"
      scan5_res  = 1
   elif scan_5 == 1:
    print "wlan profile "+wlanprofile_5ghz+" not found in scan.test case radio band 5ghz only failed"
    scan5_res = 0

 print "test radio band dual"
 print "change radio band to dual"
 clientid.sendline('config')
 clientid.sendline('radio')
 clientid.sendline('band dual')
 clientid.sendline('write')
 reboot()
 clientid = pexpect.spawn('telnet '+device_ip)
 time.sleep(4)
 clientid.sendline('config')
 clientid.sendline('wlan connect {0}'.format(wlanprofile_24ghz))
 scan_24 = clientid.expect(['Password:','ERROR'])
 if scan_24 == 0:
    print "wlan profile "+wlanprofile_24ghz+" found in scan"
    clientid.sendline('\r')
    time.sleep(3)
    scandual_res = 1
 elif scan_24 == 1:
    print "retry"
    time.sleep(6)
    clientid.sendline('wlan connect {0}'.format(wlanprofile_24ghz))
    scan_24 = clientid.expect(['Password:','ERROR'])
    if scan_24 == 0:
     print "wlan profile "+wlanprofile_24ghz+" found in scan"
     clientid.sendline('\r')
     scandual_res = 1
    elif scan_24 == 1:
      print "wlan profile "+wlanprofile_24ghz+" not found in scan"
      scandual_res = 1

 print "try connecting to wlan profile in 5ghz"
 time.sleep(6)
 clientid.sendline('wlan connect {0}'.format(wlanprofile_5ghz))
 scan_5 = clientid.expect('Password:')
 if scan_5 == 0:
      print "wlan profile "+wlanprofile_5ghz+" found in scan.radio band dual test case passed"
      scandual_res = 1
 else:
      print "wlan profile "+wlanprofile_5ghz+" not found in scan.radio band dual test case failed"
      scandual_res = 0

 if scan24_res and scan5_res and scandual_res == 1:
      print "Test Case Radio PASSED"
 else:
      print "Test Case Radio FAILED"
 
 
radio()
 

#end
sys.exit()

