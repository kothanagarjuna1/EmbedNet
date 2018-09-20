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
#import numpy
import re
from common import print_f

print_f("Test Power Standby")
print_f("===================")

#syntax

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>" + " <device_serial_port> ")
 return

if len(sys.argv) < 3:
    script_usage()
    sys.exit()

device_ip = sys.argv[1]
tunnel_port = sys.argv[2]
serial_port = sys.argv[3]

script_path = "/home/lantronix/MIDAS/xml/"

def ping():
 ping1 = pexpect.run('ping -c 5 ' +device_ip)
 #print ping1
 ping_res = 1
 if re.search('100%',ping1):
   print "cannot ping device"
   ping_res = 0
 else:
   print "able to ping device"
 print "ping_res",ping_res
 return ping_res

def wakeup():
 print_f("check tlog to confirm device wakeup from standby")
 clientid = pexpect.spawn("telnet "+device_ip)
 time.sleep(3)
 clientid.sendline('\r')
 clientid.expect('>') 
 clientid.sendline('tlog')
 log = clientid.expect(['Standby','reset'])
 if log == 0:
   print_f("device powered up from standby")
   res = 1
 else:
    print_f("device reset")
    res = 0
 clientid.close()
 return res

ping()

def device_config():
 print_f("configure device")
 telnet_config = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+script_path+"telnet.xml")
 print_f("enabled telnet ........")
 time.sleep(10)
 print_f("import xml")
 xml = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+script_path+"power.xml")
 print xml
 time.sleep(10)
 #print xml
 xml_res = re.search('Succeeded',xml)
 if xml_res: 
   print_f("xml import successful")
   print_f("Reboot")
   pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d  "+'"'+  "group=Device&optionalGroupInstance&action=Reboot"+'"')
   time.sleep(60)
   power()

def power():
  print_f("establish outgoing and incoming tunnel")
  tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  #server_address = ()
  host = '192.168.51.25'
  port = 6001
  port = int(port)
  print_f("bind socket to port")
  tcpsock.bind((host,port))
  tcpsock.listen(10)

  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  tunnel_port = '10001'
  port = int(tunnel_port)
  conn = s.connect((device_ip,port))
  time.sleep(5)
  print conn

  test_res = 1

  print test_res

  print_f("wait for time powered up to expire.sleep 3 min")
  time.sleep(200)
  ping_res = ping()
  if ping_res:
    print_f("device did not power down since tunnel is active. Test Passed")
  else:
    print_f("device powered down even though tunnel is active.Test Failed")
    test_res = 0

  print_f("disconnect incoming tunnel")
  s.close()
  ping_res = ping()
  if ping_res:
    print_f("device did not power down since tunnel connect is active.Test Passed")
  else:
    print_f("device powered down even though tunnel is active. Test Failed")
    test_res = 0
 
  print_f("disconnect outgoing tunnel")
  tcpsock.close()
  time.sleep(8)
  ping_res = ping()
  if ping_res:
     print_f("device did not power down after tunnel is disconnected.Test Failed")
     test_res = 0
  else:
     print_f("device powered down after tunnel is disconnected. Test Passed")
 
  print_f("wait for max time power down to expire. sleep 60s")
  time.sleep(70)
  ping_res = ping()
  if ping_res: 
   print_f("device powered up after max power down expired")
   wakeup()
   print_f("enable command mode")
   ser = serial.Serial(serial_port)
   ser.close()
   ser.open()
   clientid = pexpect.spawn("telnet "+device_ip)
   time.sleep(3)
   clientid.sendline('\r')
   clientid.expect('>')
   clientid.sendline('config')
   clientid.expect('config')
   clientid.sendline('line 1')
   clientid.sendline('protocol command line')
   clientid.sendline('write')
   print_f("wait for time powered up to expire.sleep 3 min")
   time.sleep(200)
   ping_res = ping()
   if ping_res == 1:
    print_f("device did not power down since command mode is enabled.Test Passed")
    clientid.sendline('protocol tunnel')
    clientid.sendline('write')
    time.sleep(5)
    ping_res = ping()
    if ping_res:
     print_f("device did not power down after command mode is disabled. Test Failed")
     test_res = 0
    else:
     print_f("device powered down after command mode is disabled. Test Passed")
     print_f("wait for max time power down to expire.sleep 1 min")
     time.sleep(70)
     ping_res = ping()
     if ping_res:
      print_f("device powered up from standby")
      wakeup()
      print_f("enable http server")
      clientid = pexpect.spawn("telnet "+device_ip)
      time.sleep(5)
      clientid.sendline('\r')
      clientid.sendline('config')
      clientid.sendline('power')
      clientid.sendline('application http server')
      clientid.sendline('state enabled')
      time.sleep(5)
      clientid.sendline('write')
      clientid.close()
      http_access = pexpect.run("curl --digest -u admin:PASSWORD http://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
      print_f(http_access)
      print_f("wait for http inactivity timeeout to expire.sleep 300s")
      time.sleep(340)
      ping_res = ping()
      if ping_res:
       print_f("evice did not power down when http server was inactive.Test Failed")
       test_res = 0
      else:
       print_f("device powered down when http server was inactive. Test Passed")

  print "result is",test_res
  if test_res == 0:
    print_f("Power Management TEST CASE FAILED")
  else:
    print_f("Power Management TEST CASE PASSED") 

#main

device_config()


sys.exit()

#subprocess.call("python /home/LtrxEngr/check.py",shell = True)
