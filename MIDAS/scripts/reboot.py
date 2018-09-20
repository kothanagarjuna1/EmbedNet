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
from time import gmtime, strftime

showtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())


print str(showtime) + "\t Test case: soft reboot"
print str(showtime) + "\t ======================"

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + "<eth0_ip>"  + "<wlan0_ip>" + "<serial_port>")
 return

if len(sys.argv) < 3:
    script_usage()
    sys.exit()


eth0_ip = sys.argv[1]
wlan0_ip = sys.argv[2]
serial_port = sys.argv[3]

def rebootDevice():
  reb = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+eth0_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")
  print reb
  print str(showtime) + "\t wait 1 min for device to come up"
  time.sleep(60)

def softReboot():

 ser = os.open(serial_port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY )
 clientid = pexpect.fdpexpect.fdspawn(ser)
 time.sleep(5)
 ser1 = serial.Serial(serial_port,9600) # open the serial port
 tc = 1
 ser1.close()
 ser1.open()
 for i in range(0,20):
  print "soft reboot iteration",i
  print str(showtime) + "\t ========================"
  if ser1.isOpen():
    rebootDevice()
    ping_device = pexpect.run('ping -c 5 '+eth0_ip)
    ping_res = re.search('5 received',ping_device)
    if ping_res:
     print str(showtime) + "\t device is online"
     uptime = pexpect.run("curl --digest -u admin:PASSWORD http://"+eth0_ip+"/export/status -X POST -d" +'"'+"optionalGroupList=device")
     print "uptime is",uptime
     print str(showtime) + "\t check wlan link"
     wlan_stat = pexpect.run("curl --digest -u admin:PASSWORD http://"+eth0_ip+"/export/status -X POST -d" +'"'+"optionalGroupList=interface:wlan0"
)
     wlan_link = re.search("Link up",wlan_stat)
     wlan_ip = re.search(wlan0_ip,wlan_stat)
     if wlan_link and wlan_ip:
      print str(showtime) + "\t wlan link is up and got an ip"
      print str(showtime) + "\t wait for 3 min run tlog before rebooting"
      time.sleep(180)
      tlog = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+eth0_ip+"/tlog")
      time.sleep(10)
      print "tlog",tlog
      #rebootDevice()
     else:
      print str(showtime) + "\t wlan link failed to come up"
      sys.exit()
    else:
      print str(showtime) + "\t device is not online"
      print str(showtime) + "\t write tlog to a file"
      clientid.sendline('\r')
      #clientid.expect('>')
      clientid.sendline('tlog')
      #clientid.expect('>')
      time.sleep(4)
      log_out = file('tlog.txt','w')
      clientid.logfile = log_out
      print str(showtime) + "\t logfile",clientid.logfile
      sys.exit()
     
softReboot()

#end
sys.exit()

