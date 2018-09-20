#!/usr/local/bin/python3

import serial
import sys
import time
import os
#import fdpexpect
import pexpect.fdpexpect
import socket
import shutil
import subprocess
import re
#import requests
from common import print_f

print_f("Test OEM - CHANGE ETH0 MAC AND REGION CODE")
print_f("==========================================")

def script_usage():
 print_f("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>" + "<serial port>" + "<secure flag>")
 return

if len(sys.argv) < 3:
    script_usage()
    sys.exit()


device_ip = sys.argv[1]
secure_flag = sys.argv[2] # values 1 or 0
serial_port = sys.argv[3]

script_path = "/home/lantronix/MIDAS/xml/"
print_f(secure_flag)

if secure_flag == '0':
  http_var = "http://"+device_ip
else:
  http_var = "-k https://"+device_ip
  pexpect.run("curl --digest -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form configrecord=@../cert.xml")
  res = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")
  res = re.search('Rebooting',res)
  if res:
    print_f("device is rebooting. wait for 80s")
    time.sleep(80)
  else:
    print_f("failed to reboot")
    sys.exit()


print_f(http_var)


def oem():
 tc = 1
 print_f("aaaaaaaaaa")
 importXML = pexpect.run("curl --digest -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form configrecord=@"+script_path+"oem_config.xml")
 print_f(importXML)
 importStatus = re.search("Succeeded",importXML)
 if importStatus:
   print_f("xml import successful")
   res = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")
   res = re.search('Rebooting',res)
   if res:
    print_f("device is rebooting. wait for 80s")
    time.sleep(80)
    print_f("ping to check whether device is online")
    ping_res = pexpect.run('ping -c 4 '+device_ip)
    print_f(ping_res)
    time.sleep(4)
    res = re.search('100%',ping_res)
    if res:
     print_f("device is not online.")
     sys.exit()
    else:
     print_f("verify eth0 mac and region code")
     print_f("bbbb")
     clientid = pexpect.spawn('telnet '+device_ip)
     print_f("ccc")
     time.sleep(5)
     clientid.sendline('\r')
     clientid.sendline('\r')
     clientid.sendline('tlog\r')
     time.sleep(5)
     print_f("ddd")
     eth0_mac = clientid.expect(['eth0 MAC Address 00:81:A3:B7:66:62','eth0 MAC Address 00:80:A3:B7:87:E1'])
     print_f(eth0_mac)
     region = clientid.expect(['WLAN Region: Japan', 'WLAN Region: United States'])
     print_f(region)
     if region == 0 and eth0_mac == 0:
       print_f("Test Case:eth0 mac and region code saved as OEM config.TEST PASSED")
       print_f("revert to lantronix defaults")
       print_f("Test Case:first use incorrect password to remove oem config. this should fail")
       importXML = pexpect.run("curl --digest -u admin:PASSWORD "+http_var+"/import/config -X POST --form configrecord=@"+script_path+"oem_wrong_password.xcr")
       print_f("wrong passwd",importXML)
       importStatus = re.search("ERROR: Not permitted to remove OEM factory settings",importXML)
       if importStatus:
         print_f("failed to remove oem config. password incorrect.TEST PASSED")
       else:
         print_f( "oem config removed even though password is incorrect.TEST FAILED")
         tc = 0
       print_f("use correct password to remove oem config")
       importXML = pexpect.run("curl --digest -u admin:PASSWORD "+http_var+"/import/config -X POST --form configrecord=@"+script_path+"remove_oem.xcr")
       importStatus = re.search("Removed OEM factory settings",importXML)
       if importStatus:
        print_f("xml import successful.factory default to verify lantronix defaults")
        res = pexpect.run("curl --anyauth -u admin:PASSWORD "+http_var+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=factory defaults")
        time.sleep(20)
        ser = os.open(serial_port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY )
        clientid = pexpect.fdpexpect.fdspawn(ser)
        ser1 = serial.Serial(serial_port,9600) # open the serial port
        time.sleep(5)
        #ser1.close()
        #ser1.open() 
        clientid.sendline('\r')
        clientid.sendline('status\r')
        clientid.sendline('interface eth0')
        clientid.sendline('show')
        time.sleep(3)
        eth0_org_mac = clientid.expect(['00:80:A3:B7:87:E1','00:81:A3:B7:66:62'])
        print_f(eth0_org_mac)
        clientid.sendline('exit\r')
        clientid.sendline('exit\r')
        clientid.sendline('xml')
        clientid.sendline('xcr dump oem')
        time.sleep(4)
        region = clientid.expect(['United States','Japan'])
       else:
         print_f("failed to import lantronix default xml.TEST FAILED")
         tc = 0
       if eth0_org_mac == 0 and region == 0:
          print_f("Test Case:reverted to lantronix defaults.TEST PASSED")
       else:
          print_f("failed to restore lantronix defaults.TEST FAILED")
          tc = 0
     else:
        print_f("failed to save eth0 mac and region code as OEM config.TEST FAILED")
        tc = 0
 else:
   print_f("failed to reboot")
   tc = 0

 if tc == 0:
   print_f("OEM TEST CASE FAILED")
 else:
   print_f("OEM TEST CASE PASSED")

  
#main 
oem()

sys.exit()

