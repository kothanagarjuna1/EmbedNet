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

#syntax

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <serial_port>" + " <wlan0_ip>" + "<eth0_ip>" "<reassoc_flag>")
 return

if len(sys.argv) < 4:
    script_usage()
    sys.exit()

serial_port = sys.argv[1]
wlan0_ip = sys.argv[2]
eth0_ip = sys.argv[3]
reassoc_flag = sys.argv[4]

print wlan0_ip

xml_path = "/home/lantronix/Desktop/xpico240_new/scripts_wireless/"
script_path = "/home/lantronix/Desktop/xpico240_new/scripts_wireless/"

def reboot():
 print "Reboot"
 pexpect.run("curl --anyauth -u admin:PASSWORD http://"+eth0_ip+"/action/status -X POST -d  "+ "group=Device&optionalGroupInstance&action=Reboot"+'"')
 print "wait for device to come online"
 time.sleep(30)

def wlanLink(security_suite):
 tc = 0
 ser = os.open(serial_port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY )
 clientid = pexpect.fdpexpect.fdspawn(ser)
 time.sleep(5)
 ser = serial.Serial(serial_port)
 ser.close()
 ser.open()
 time.sleep(4)
 print "wait for wlan0 link to come up"
 time.sleep(25)
 clientid.sendline('status')
 time.sleep(3)
 clientid.sendline('int wlan0')
 clientid.sendline('show')
 time.sleep(5)
 wlan0ip = clientid.expect([wlan0_ip])
 if wlan0ip == 0:
    print "wlan0 got dhcp address"
    print "wlan profile test passed",security_suite
    tc = 1
 else:
    print "failed to get dhcp address"
    print "wlan profile test failed",security_suite
 clientid.sendline('exit')
 clientid.sendline('wlan')
 clientid.sendline('show')
 time.sleep(5)
 if security_suite == 'wpa2':
  res = clientid.expect(['Security Suite     : WPA2'])
 elif security_suite == 'wpa':
  res = clientid.expect(['Security Suite     : WPA'])
 elif security_suite == 'wep':
  res = clientid.expect(['Security Suite     : WEP'])
 if res == 0:
   print "wlan0 security suite is",security_suite
 else:
   print "wlan0 security suite does not match"
   print "test failed"
   sys.exit()
 clientid.sendline('exit')
 clientid.sendline('exit\r')
 return tc
 ser.close()


def wlanProfile(security_suite):
 print "Configure line as command line"
 telnetid = pexpect.spawn('telnet '+eth0_ip)
 time.sleep(4)
 telnetid.sendline('\r')
 telnetid.sendline('config')
 telnetid.sendline('line 1')
 telnetid.sendline('protocol command line')
 time.sleep(3)
 telnetid.sendline('write')
 print "delete all wlan profiles"
 x = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+eth0_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"deletewlanprofiles.xml")
 print "delete wlan profile",x
 ser = os.open(serial_port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY )
 clientid = pexpect.fdpexpect.fdspawn(ser)
 time.sleep(5)
 ser = serial.Serial(serial_port)
 ser.close()
 ser.open()
 time.sleep(4)
 clientid.sendline('config')
 time.sleep(3)
 print "configure wlan profile",security_suite
 clientid.expect('config')
 clientid.sendline('wlan profile wpa2_ccmp')
 time.sleep(2)
 clientid.sendline('okay')
 time.sleep(2)
 clientid.sendline('basic')
 if security_suite == 'wpa2': 
  clientid.sendline('network name wpa2_ccmp')
 elif security_suite == 'wpa':
  clientid.sendline('network name wpa_ccmp')
  time.sleep(10)
 elif security_suite == 'wep':
   clientid.sendline('network name wep')
   time.sleep(10)
 clientid.sendline('exit')
 clientid.sendline('security')
 if security_suite == 'wpa2':
  clientid.sendline('suite wpa2')
 elif security_suite == 'wpa':
   clientid.sendline('suite wpa')
 elif security_suite == 'wep':
   clientid.sendline('suite wep')
   time.sleep(2)
   clientid.sendline('wep')
   time.sleep(2)
   clientid.sendline('key size 104')
   time.sleep(2)
   clientid.sendline('key 1')
   time.sleep(2)
   clientid.sendline('key 11111111111111111111111111')
 time.sleep(3)
 clientid.sendline('write')
 if security_suite == 'wpa2' or security_suite == 'wpa':
  clientid.sendline('wpax')
  clientid.sendline('passphrase superman')
 clientid.sendline('write')
 clientid.sendline('exit\r')
 clientid.sendline('exit\r')
 clientid.sendline('exit\r')
 clientid.sendline('exit\r')
 clientid.sendline('exit\r')
 clientid.sendline('\r')
 print "wait for wlan0 link to come up"
 time.sleep(25)
 clientid.sendline('status')
 time.sleep(3)
 clientid.sendline('int wlan0')
 clientid.sendline('show')
 time.sleep(5)
 wlan0ip = clientid.expect([wlan0_ip])
 if wlan0ip == 0:
    print "wlan0 got dhcp address"
    print "wlan profile test passed",security_suite
    res = 1
 else:
    print "failed to get dhcp address"
    print "wlan profile test failed",security_suite 
    res = 0
 clientid.sendline('exit')
 clientid.sendline('wlan')
 clientid.sendline('show')
 time.sleep(5)
 if security_suite == 'wpa2':
  res = clientid.expect(['Security Suite     : WPA2'])
 elif security_suite == 'wpa':
  res = clientid.expect(['Security Suite     : WPA'])
 elif security_suite == 'wep':
  res = clientid.expect(['Security Suite     : WEP'])
 if res == 0:
   print "wlan0 security suite is",security_suite
   res = 1
 else:
   print "wlan0 security suite does not match"
   print "test failed"
   res = 0
 return res

def wpa2_ccmp():
 print "Configure line as command line"
 telnetid = pexpect.spawn('telnet '+wlan0_ip)
 time.sleep(4)
 telnetid.sendline('config')
 telnetid.sendline('line 1')
 telnetid.sendline('protocol command line')
 time.sleep(3)
 telnetid.sendline('write')
 telnetid.close()
 time.sleep(4)

 print "delete all wlan profiles before running the test"
 x = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+eth0_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"deletewlanprofiles.xml")
 print "delete wlan profile",x
 ser = os.open(serial_port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY )
 clientid = pexpect.fdpexpect.fdspawn(ser)
 time.sleep(5)
 ser = serial.Serial(serial_port,xonxoff=True)
 ser.close()
 ser.open()
 time.sleep(4)
 clientid.sendline('config')
 time.sleep(3)
 print "configure wlan profile wpa2_ccmp"
 clientid.expect('config')
 clientid.sendline('wlan profile wpa2_ccmp')
 time.sleep(2)
 clientid.sendline('okay')
 time.sleep(2)
 clientid.sendline('basic')
 clientid.sendline('network name wpa2_ccmp')
 clientid.sendline('exit')
 clientid.sendline('security')
 clientid.sendline('suite wpa2')
 time.sleep(3)
 clientid.sendline('wpax')
 clientid.sendline('passphrase superman')
 clientid.sendline('write')
 clientid.sendline('exit\r')
 clientid.sendline('exit\r')
 clientid.sendline('exit\r')
 clientid.sendline('exit\r')
 clientid.sendline('exit\r')
 clientid.sendline('\r')
 wlanLink('wpa2')


def wpa_ccmp():
 ser = os.open(serial_port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY )
 clientid = pexpect.fdpexpect.fdspawn(ser)
 time.sleep(5)
 ser = serial.Serial(serial_port)
 ser.close()
 ser.open()
 time.sleep(4)
 clientid.sendline('config')
 time.sleep(3)
 clientid.expect('config')
 print "configure wlan profile wpa_ccmp"
 clientid.expect('config')
 clientid.sendline('wlan profile wpa_ccmp')
 time.sleep(2)
 clientid.sendline('okay')
 time.sleep(2)
 clientid.sendline('basic')
 clientid.sendline('network name wpa_ccmp')
 clientid.sendline('exit')
 clientid.sendline('security')
 clientid.sendline('suite wpa')
 time.sleep(3)
 clientid.sendline('write')
 clientid.sendline('wpax')
 clientid.sendline('passphrase superman')
 clientid.sendline('write')
 clientid.sendline('exit\r')
 clientid.sendline('exit\r')
 clientid.sendline('exit\r')
 clientid.sendline('exit\r')
 clientid.sendline('exit\r')
 clientid.sendline('\r')
 #wlanLink('wpa')

def wep():
 ser = os.open(serial_port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY )
 clientid = pexpect.fdpexpect.fdspawn(ser)
 time.sleep(5)
 ser = serial.Serial(serial_port)
 ser.close()
 ser.open()
 time.sleep(4)
 clientid.sendline('config')
 time.sleep(3)
 print "configure wlan profile wep"
 clientid.expect('config')
 clientid.sendline('wlan profile wep')
 time.sleep(2)
 clientid.sendline('okay')
 time.sleep(2)
 clientid.sendline('basic')
 clientid.sendline('network name wep')
 clientid.sendline('exit')
 clientid.sendline('security')
 clientid.sendline('write')
 clientid.sendline('suite wep')
 time.sleep(2)
 clientid.sendline('wep')
 time.sleep(2)
 clientid.sendline('key size 104')
 time.sleep(2)
 clientid.sendline('key 1')
 time.sleep(2)
 clientid.sendline('key 11111111111111111111111111')
 clientid.sendline('write')
 clientid.sendline('exit\r')
 clientid.sendline('exit\r')
 clientid.sendline('exit\r')
 clientid.sendline('exit\r')
 clientid.sendline('exit\r')
 #wlanLink('wep')
 ser.close()

def reassociation():
 ser = os.open(serial_port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY )
 clientid = pexpect.fdpexpect.fdspawn(ser)
 time.sleep(5)
 ser = serial.Serial(serial_port)
 ser.close()
 ser.open()
 time.sleep(4)
 print "disable all wlan profiles"
 clientid.sendline('config')
 clientid.expect('config')
 clientid.sendline('wlan profile wpa_ccmp')
 clientid.sendline('basic')
 clientid.sendline('state disable')
 time.sleep(3)
 clientid.sendline('write')
 clientid.sendline('exit')
 clientid.sendline('exit')
 clientid.sendline('wlan profile wpa2_ccmp')
 clientid.sendline('basic')                                     
 clientid.sendline('state disable')
 time.sleep(3)                                 
 clientid.sendline('write')
 clientid.sendline('exit')
 clientid.sendline('exit')   
 clientid.sendline('wlan profile wep')
 clientid.sendline('basic')                                     
 clientid.sendline('state disable')
 time.sleep(3)                                 
 clientid.sendline('write')
 clientid.sendline('exit')
 clientid.sendline('exit')
 clientid.sendline('exit')
 time.sleep(10)
 clientid.sendline('status')
 clientid.sendline('wlan')
 clientid.sendline('show')
 time.sleep(5)
 nolink = clientid.expect(['Disconnected'])
 if nolink == 0:
  print "wlan link is down"
 else:
  print "wlan link is not down after disabling wlan profile"
  sys.exit()
 clientid.sendline('exit')
 clientid.sendline('exit')

 print "enable wlan profile wpa2_ccmp"
 clientid.sendline('config')
 clientid.sendline('wlan profile wpa2_ccmp')
 clientid.sendline('basic')
 clientid.sendline('state enable')
 time.sleep(3)
 clientid.sendline('write')
 clientid.sendline('exit')
 clientid.sendline('exit')
 clientid.sendline('exit\r')
 wlanLink('wpa2')
 print "enable wlan profile wep"
 clientid.sendline('config') 
 clientid.sendline('wlan profile wep')
 clientid.sendline('basic')
 clientid.sendline('state enable')
 time.sleep(3)
 clientid.sendline('write')
 clientid.sendline('exit')
 clientid.sendline('exit')
 print "disable wlan profile wpa2_ccmp. verify device re-associates with wlan profile wep"
 clientid.sendline('wlan profile wpa2_ccmp')
 clientid.sendline('basic')
 clientid.sendline('state disable')
 time.sleep(3)
 clientid.sendline('write') 
 clientid.sendline('exit')
 clientid.sendline('exit')
 clientid.sendline('exit')
 test_res = wlanLink('wep')
 
 print "enable wlan profile wpa_ccmp"
 clientid.sendline('config')
 clientid.sendline('wlan profile wpa_ccmp')
 clientid.sendline('basic')
 clientid.sendline('state enable')
 time.sleep(3)
 clientid.sendline('write')
 clientid.sendline('exit')
 clientid.sendline('exit')
 print "disable wlan profile wep. verify device re-associates with wlan profile wpa_ccmp"
 clientid.sendline('wlan profile wep')
 clientid.sendline('basic')
 clientid.sendline('state disable')
 time.sleep(3)
 clientid.sendline('write')
 clientid.sendline('exit')
 clientid.sendline('exit')
 clientid.sendline('exit\r')
 test_res = wlanLink('wpa')
 
 if test_res == 0:
  print "Re-association TEST CASE FAILED"
 else:
  print "Re-association TEST CASE PASSED"

 

#main program 
reboot()
def main():
 print reassoc_flag
 if reassoc_flag == '1':
  print "Test Re-association"
  wpa2_ccmp()
  time.sleep(3)
  wpa_ccmp()
  time.sleep(3)
  wep()
  time.sleep(3)
  reassociation()
 else:
  print "Test Wlan Profiles wpa2 ccmp+tkip,wpa ccmp+tkip and wep 104 hex open"
  wpa2_res = wlanProfile('wpa2')
  reboot()
  wpa_res = wlanProfile('wpa')
  reboot()
  wep_res = wlanProfile('wep')
  if wpa2_res == 1 and wpa_res == 1 and wep_res == 1:
   print "Wlan Profiles TEST CASE PASSED"
  else:
   print "Wlan Profile TEST CASE FAILED"

main()
sys.exit()
