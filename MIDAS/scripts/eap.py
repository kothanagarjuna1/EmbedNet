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
 print("Usage: " + os.path.basename(sys.argv[0]) + " <serial_port>" + " <wlan0_ip>" + " <eth0_ip>" + " <credential>")
 return

if len(sys.argv) < 4:
    script_usage()
    sys.exit()

serial_port = sys.argv[1]
wlan0_ip = sys.argv[2]
eth0_ip = sys.argv[3]
credential = sys.argv[4] #values 1 or 0

print wlan0_ip

xml_path = '/home/lantronix/MIDAS/xml/'

def reboot():
 print "Reboot"
 pexpect.run("curl --anyauth -u admin:PASSWORD http://"+eth0_ip+"/action/status -X POST -d  "+ "group=Device&optionalGroupInstance&action=Reboot"+'"')

def eap(eap_protocol,version):

 print "Configure line as command line"
 telnetid = pexpect.spawn('telnet '+eth0_ip)
 telnetid.sendline('config')
 telnetid.sendline('line 1')
 telnetid.sendline('protocol command line')
 telnetid.sendline('write')
 ser = os.open(serial_port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY )
 clientid = pexpect.fdpexpect.fdspawn(ser)
 time.sleep(5)
 ser = serial.Serial(serial_port)
 ser.close()
 ser.open()
 time.sleep(4)
 clientid.sendline('config')
 time.sleep(3)
 print "configure wlan profile",eap_protocol
 clientid.expect('config')
 clientid.sendline('wlan profile Radius')
 time.sleep(2)
 clientid.sendline('okay')
 time.sleep(2)
 clientid.sendline('basic') 
 clientid.sendline('network name Radius')
 clientid.sendline('exit')
 clientid.sendline('security')
 clientid.sendline('suite wpa2')
 time.sleep(3)
 clientid.sendline('write')
 clientid.sendline('wpax')
 #clientid.expect('config WLAN Profile')
 clientid.sendline('authentication 8021X')
 time.sleep(2)
 clientid.sendline('ieee 8021x {0}'.format(eap_protocol))
 time.sleep(2)
 clientid.sendline('username wcurrier')
 clientid.sendline('password test')
 clientid.sendline('credentials client')
 clientid.sendline('write')
 #print "wait"
 #time.sleep(100)
 

def eaprotocol(eap_protocol,version):
 if credential == '1':
  imp = pexpect.run("curl --digest -u admin:PASSWORD http://"+eth0_ip+"/import/config -X POST --form configrecord=@"+xml_path+"eap.xml")
  print imp
 eap(eap_protocol,version)
 ser = os.open(serial_port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY )
 clientid = pexpect.fdpexpect.fdspawn(ser)
 time.sleep(5)
 ser = serial.Serial(serial_port)
 ser.close()
 ser.open()
 time.sleep(4)
 if eap_protocol == 'eap-ttls':
  print "test eap-ttls mschapv2" 
  clientid.sendline('eap-ttls option mschapv2')
  clientid.sendline('write')
  #print "wait"
  #time.sleep(100)
  reboot()
  time.sleep(80)
  res = wlanStatus()
  print "test eap-ttls eap-mschapv2"
  clientid.sendline('eap-ttls option eap-mschapv2')
  clientid.sendline('write')
  reboot()
  time.sleep(80)
  res = wlanStatus()
  print "test eap-ttls chap"
  clientid.sendline('eap-ttls option chap')
  clientid.sendline('write')
  reboot()
  time.sleep(80)
  res = wlanStatus()
  print "test eap-ttls pap"
  clientid.sendline('eap-ttls option pap')
  clientid.sendline('write')
  reboot()
  time.sleep(80)
  res = wlanStatus()
  print "eap-ttls eap-md5"
  clientid.sendline('eap-ttls option eap-md5')
  clientid.sendline('write')
  reboot()
  time.sleep(80)
 # eap(eap_protocol)
 if eap_protocol == 'eap-tls' or eap_protocol == 'peap' or eap_protocol == 'eap-ttls':
   imp = pexpect.run("curl --digest -u admin:PASSWORD http://"+eth0_ip+"/import/config -X POST --form configrecord=@"+xml_path+"eap.xml")
   #print imp
   if eap_protocol == 'eap-tls':
    reboot()
    time.sleep(80)
    res = wlanStatus()
 if eap_protocol == 'peap':
  if version == '1':
   print "test peap version 1"
   clientid.sendline('peap version 1')
  elif version == '0':
   print "test peap version 0"
   clientid.sendline('peap version 0')
  print "test peap eap-md5"
  clientid.sendline('peap option eap-md5')
  clientid.sendline('write')
  reboot()
  time.sleep(80)
  res = wlanStatus()
  print "peap eap-tls"
  clientid.sendline('peap option eap-tls')
  clientid.sendline('peap credentials client')
  time.sleep(3)
  clientid.sendline('write')
  reboot()
  time.sleep(80)
  res = wlanStatus()
 if eap_protocol == 'FAST':
   print "test FAST md5"
   clientid.sendline('fast option md5')
   clientid.sendline('write')
   reboot()
   time.sleep(80)
   res = wlanStatus()
   print "test FAST mschapv2"
   clientid.sendline('fast option mschapv2')
   clientid.sendline('write')
   reboot()
   time.sleep(80)
   res = wlanStatus()
   print "fast option gtc"
   clientid.sendline('fast option gtc')
   clientid.sendline('write')
   reboot()
   time.sleep(80)
   res = wlanStatus()
 return res
 
def wlanStatus():
  print "check wlan0 link"
  wlan_stat = 1
  ser = os.open(serial_port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY )
  clientid = pexpect.fdpexpect.fdspawn(ser)
  time.sleep(5)
  ser = serial.Serial(serial_port)
  ser.close()
  ser.open()
  time.sleep(4)
  clientid.sendline('exit')
  clientid.sendline('exit')
  clientid.sendline('exit')
  clientid.sendline('exit')
  clientid.sendline('exit')
  clientid.sendline('exit')
  clientid.sendline('status')
  time.sleep(3)
  clientid.sendline('wlan')
  clientid.sendline('show')
  time.sleep(25)
  stat = clientid.expect(['802.1X'])
  if stat == 0:
    print "wlan link up"
  else:
    print "wlan link failed to come up"
    wlan_stat = 0
  clientid.sendline('exit')
  clientid.sendline('exit')
  clientid.sendline('exit\r')
  time.sleep(15)
  clientid.sendline('status')
  clientid.sendline('status')
  clientid.sendline('interface wlan0')
  clientid.sendline('show')
  time.sleep(5)
  wlan0ip = clientid.expect([wlan0_ip])
  if wlan0ip == 0:
    print "wlan0 got dhcp address"
  else:
    print "failed to get dhcp address"
    wlan_stat = 0
  clientid.sendline('exit')
  clientid.sendline('exit')
  clientid.sendline('config')
  #clientid.expect('config')
  clientid.sendline('wlan profile Radius')
  clientid.sendline('security')
  clientid.sendline('suite wpa2')
  time.sleep(3)
  clientid.sendline('wpax')
  return wlan_stat 

#main program 

ttls_stat = eaprotocol('eap-ttls','0')
print ttls_stat
tls_stat = eaprotocol('eap-tls','0')
print tls_stat
peap_stat = eaprotocol ('peap','0')
peap_stat = eaprotocol('peap','1')
fast_stat = eaprotocol('FAST','0')

print ttls_stat
print tls_stat
print peap_stat
print fast_stat

if ttls_stat == 1 and tls_stat == 1 and peap_stat == 1 and fast_stat == 1:
  print "EAP protocols test passed"
else:
  print "EAP protocols test failed"

sys.exit()

#subprocess.call("python /home/LtrxEngr/check.py",shell = True)


