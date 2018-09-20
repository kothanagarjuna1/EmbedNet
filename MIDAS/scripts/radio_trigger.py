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

print "Test Radio Trigger"
print "================="

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>" + " <wlanprofile_24ghz> " + " <wlanprofile_5ghz> ")
 return

if len(sys.argv) < 3:
    script_usage()
    sys.exit()

device_ip = sys.argv[1]
wlanprofile_24ghz = sys.argv[2]
wlanprofile_5ghz = sys.argv[3]

xml_path = "/home/ltrxengr/xpw/xml/" 

def reboot():
 print "reboot device for changes to take effect"
 pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")
 print "device is rebooting"
 time.sleep(30)


def radioTrigger():
 clientid = pexpect.spawn('telnet '+device_ip)
 time.sleep(4)
 clientid.sendline('config')
 clientid.sendline('radio')
 clientid.sendline('mode trigger')
 clientid.sendline('write')
 reboot()
 clientid = pexpect.spawn('telnet '+device_ip)
 time.sleep(4)
 clientid.sendline('status')
 clientid.sendline('radio')
 clientid.sendline('show')
 time.sleep(8)
 radio_mode = clientid.expect('Triggered')
 if radio_mode == 0:
   print "radio mode is set to trigger"
 else:
   print "radio mode is not set to trigger"
   sys.exit()
 clientid.sendline('exit')
 clientid.sendline('exit')
 clientid.sendline('tlog')
 time.sleep(5)
 radio_stat = clientid.expect('Radio Mode is "Triggered"')
 if radio_stat == 0:
   print "radio is down as expected"
   radio_res = 1
   clientid.sendline('\r')
   clientid.sendline('config\r')
   clientid.sendline('wlan connect {0}'.format(wlanprofile_24ghz))
   time.sleep(4)
   conn = clientid.expect('ERROR')
   if conn == 0:
     print "cannot connect to wlan profile in 2.4 ghz as expected when radio is down"
     print "trigger radio"
     clientid.sendline('exit')
     clientid.sendline("status")
     clientid.sendline("cpm")
     clientid.sendline("roles")
     clientid.sendline("role radio trigger")
     clientid.sendline("state active")
     clientid.sendline('exit')
     clientid.sendline('exit')
     clientid.sendline('exit')
     clientid.sendline('exit')
     time.sleep(5)
     print "check radio is up"
     clientid.sendline("tlog")
     #tlog = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/tlog"
     radio_stat = clientid.expect("WLAN Region:")
     if radio_stat == 0:
       print "radio is up"
       time.sleep(10)
       print "connect to wlan profile in 2.4 ghz"
       clientid.sendline('\r')
       clientid.sendline('\r')
       clientid.sendline('config')
       clientid.sendline('wlan connect {0}'.format(wlanprofile_24ghz))
       conn_24 = clientid.expect('Password:')
       if conn_24 == 0:
         clientid.sendline('\r')
         clientid.sendline('\r')
         print "wlan profile 2.4 ghz found in scan."
         conn24_res = 1
         print "connect to wlan profile in 5 ghz"
         clientid.sendline('wlan connect {0}'.format(wlanprofile_5ghz))
         conn_5 = clientid.expect(['Password:','ERROR'])
         if conn_5 == 0:
           clientid.sendline('\r')
           clientid.sendline('\r')
           print "wlan profile 5 ghz found in scan" 
           conn5_res = 1
         elif conn_5 == 1:
           print "wlan profile 5ghz not found in scan"
           print "retry"
           time.sleep(6)
           clientid.sendline('wlan connect {0}'.format(wlanprofile_5ghz))
           conn_5 = clientid.expect(['Password:','ERROR'])
           if conn_5 == 0:
             print "wlan profile 5 ghz found in scan"
             conn5_res = 1
           else:
             print "wlan profile 5 ghz not found in scan"
             conn5_res = 0
       elif conn_24 == 1:
         print "wlan profile 2.4 ghz not found in scan"
         print "retry"
         print "here"
         time.sleep(10)
         clientid.sendline('wlan connect {0}'.format(wlanprofile_24ghz))
         conn_24 = clientid.expect(['ERROR','Password:'])
         if conn_24 == 1:
           print "wlan profile 2.4 ghz found in scan"
           conn24_res = 1
         else:
           print "wlan profile 2.4 ghz not found in scan" 
           conn24_res = 0
           print "try again"
           clientid.sendline('wlan connect {0}'.format(wlanprofile_24ghz))
           conn_24 = clientid.expect(['ERROR','Password:'])
           if conn_24 == 1:
            print "wlan profile 2.4 ghz found in scan"
            conn24_res = 1
           else:
             print "wlan profile 2.4ghz not found in scan"
             sys.exit()

      
       if radio_stat == 0 and conn24_res == 1 and conn5_res == 1:
         print "Radio Mode Trigger Test Case PASSED"
       else:
         print "Radio Mode Trigger Test Case FAILED"
 else:
  print "radio is not down. It is still up.Radio Mode Trigger Test Case FAILED"
  sys.exit()

 clientid.sendline('\r')
 clientid.sendline('\r')
 clientid.sendline('config')
 clientid.sendline('radio')
 clientid.sendline('mode enable')
 clientid.sendline('write')
 reboot()

               
radioTrigger()
 

#end
sys.exit()

