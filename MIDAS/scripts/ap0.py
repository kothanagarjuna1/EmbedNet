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
import re

print "Test ap0 Security Suites and Modes - Triggered, Initial Trigger And Always"
print "============================================================================"

#syntax

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>" + " <vut_serial_port>" + "<ap0 band>")
 return

if len(sys.argv) < 3:
    script_usage()
    sys.exit()

device_ip = sys.argv[1]
xpw_serial_port = sys.argv[2] # use midas platform as vut.enable command mode on the line.script uses wlan connect to test ap0. so make sure to delete all wlan profiles
band = sys.argv[3]

def fs():

 print "compact file system before proceeding with ap0 test cases"

 pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d  "+ '"'+ "group=File System&optionalGroupInstance&action=Format"+'"')

 pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d  "+ '"'+ "group=File System&optionalGroupInstance&action=Compact"+'"')

def trigger(security_suite,encryption,ap0_mode):
   print "trigger ap0"
   clientid = pexpect.spawn('telnet '+device_ip)
   clientid.sendline('\r')
   clientid.sendline('\r')
   clientid.sendline('status')
   clientid.expect('status')
   clientid.sendline('cpm')
   clientid.expect('status CPM')
   clientid.sendline('roles')
   clientid.expect('status CPM Roles')
   clientid.sendline('role ap trigger')
   clientid.expect('status CPM Roles Role AP Trigger')
   clientid.sendline('state active')
   clientid.expect('status CPM Roles Role AP Trigger')
   if ap0_mode == 'Triggered':
     ser = os.open(xpw_serial_port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY )
     vut = pexpect.fdpexpect.fdspawn(ser)
     ser1 = serial.Serial(xpw_serial_port,9600)
     time.sleep(5)
     vut.sendline('status\r')
     #vut.expect('status')
     vut.sendline('device\r')
     #vut.expect('status Device')
     vut.sendline('reboot')
     time.sleep(2)
     vut.expect('okay/cancel')
     time.sleep(2)
     vut.sendline('okay\r')
     time.sleep(2)
     print ("Rebooting vut to disconnect from ap0")
     vut.expect('Rebooting')
     vut.close()
     print "test link down after uptime expires when no clients are connected"
     time.sleep(125)
     clientid.sendline('exit')
     clientid.sendline('exit')
     clientid.sendline('exit')
     clientid.sendline('exit')
     clientid.sendline('status\r')
     clientid.sendline('interface ap0\r')
     clientid.sendline('show')
     time.sleep(10)
     ap0 = clientid.expect(['Link up','No link'])
     if ap0 == 1:
      print "link down after uptime expired and no clients connected to ap0.test case passed"
      clientid.sendline('exit')
      clientid.sendline('status')
      clientid.expect('status')
      clientid.sendline('cpm')
      clientid.expect('status CPM')
      clientid.sendline('roles')
      clientid.expect('status CPM Roles')
      clientid.sendline('role ap trigger')
      clientid.expect('status CPM Roles Role AP Trigger')
      clientid.sendline('state active')
      clientid.expect('status CPM Roles Role AP Trigger')
      time.sleep(8)
     elif ap0 == 0:
      print "link is up after uptime expired and no clients connected to ap0.test case failed"
   time.sleep(10)
   clientid.close()
   xpw(security_suite,encryption,ap0_mode)


def ap0(security_suite,encryption,ap0_mode):
 print "TEST ap0 mode",ap0_mode
 print "configure ap0 interface"
 clientid = pexpect.spawn('telnet '+device_ip)
 time.sleep(8)
 clientid.sendline('\r')
 clientid.sendline('\r')
 clientid.sendline('config')
 clientid.expect('config')
 clientid.sendline('access point')
 #clientid.expect('config Access Point')
 clientid.sendline('mode {0}'.format(ap0_mode))
 time.sleep(8)
 #clientid.expect('config Access Point')
 if ap0_mode == 'Triggered':
  clientid.sendline('uptime 120 seconds')
  time.sleep(5)
  #clientid.expect('config Access Point')
 clientid.sendline('SSID SUBHA_DEVICE\r')
 time.sleep(8)
 clientid.expect('config Access Point')
 clientid.sendline('suite {0}'.format(security_suite))
 time.sleep(8)
 clientid.expect('config Access Point')
 clientid.sendline('encryption {0}'.format(encryption))
 time.sleep(8)
 clientid.expect('config Access Point')
 clientid.sendline('config Access Point')
 time.sleep(8)
 clientid.expect('config Access Point')
 clientid.sendline('passphrase superman')
 time.sleep(8)
 clientid.expect('config Access Point')
 clientid.sendline('mode {0}'.format(ap0_mode))
 time.sleep(8)
 clientid.sendline('band {0}'.format(band))
 if band == '2.4':
  clientid.sendline('channel 8')
 elif band == '5':
  clientid.sendline('channel 48') 
 clientid.expect('config Access Point')
 clientid.sendline('write\r')
 time.sleep(2)
 print "Rebooting device for changes to take effect"
 pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d  "+ "group=Device&optionalGroupInstance&action=Reboot"+'"')
 time.sleep(60)
 clientid.close()
 if ap0_mode == 'Triggered' or ap0_mode == 'Initial Trigger':
  trigger(security_suite,encryption,ap0_mode)
 else:
  xpw(security_suite,encryption,ap0_mode)

def ap0_status(ap0_mode):
 print "check ap0 link status"
 time.sleep(20)
 clientid = pexpect.spawn('telnet '+device_ip)
 clientid.sendline('\r')
 clientid.sendline('\r')
 clientid.sendline('status\r')
 clientid.sendline('access point')
 #clientid.sendline('interface ap0\r')
 clientid.sendline('show')
 time.sleep(2)
 #ap0 = clientid.expect(['Link up','No link'])
 #ap0 = clientid.expect(['No link'])
 ap0 = clientid.expect(['State: Down','Up'])
 print "ap0" , ap0
 if ap0_mode == 'Triggered':
  if ap0 == 0:
   print "ap0 link down after client disconnected.test case passed",ap0_mode
  elif ap0 == 1:
   print "ap0 link up after client disconnected.test case failed",ap0_mode
 if ap0_mode == 'Initial Trigger':
  if ap0 == 0:
    print "ap0 link down after client disconnected.test failed",ap0_mode
  elif ap0 == 1:
    print "ap0 link up after client disconnected.test case passed",ap0_mode
 clientid.sendline('exit')
 clientid.sendline('exit')
 clientid.close()

def xpw(security_suite,encryption,ap0_mode):
 ser = os.open(xpw_serial_port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY )
 vut = pexpect.fdpexpect.fdspawn(ser)
 time.sleep(3)
 ser1 = serial.Serial(xpw_serial_port,9600)
 time.sleep(5)
 vut.sendline('\r')
 vut.sendline('\r')
 vut.sendline('config')
 time.sleep(2)
# vut.expect('config')
 print "connect to ap0"
 vut.sendline('wlan connect SUBHA_DEVICE')
 time.sleep(5)
 ap0_pass = vut.expect(['Password:','ERROR'])
 print "ap0_pass",ap0_pass
 if ap0_pass == 0:
  vut.sendline('superman')
  #print "wait"
  #time.sleep(40)
 elif ap0_pass == 1:
   print "retry"
   time.sleep(6)
   vut.sendline('wlan connect SUBHA_DEVICE')
   time.sleep(3)
   ap0_pass = vut.expect(['Password:','ERROR'])
   if ap0_pass == 1:
    print "retry 1"
    time.sleep(5)
    vut.sendline('wlan connect SUBHA_DEVICE')
    time.sleep(3)
    ap0_pass = vut.expect(['Password:','ERROR'])
    if ap0_pass == 1:
     print "cannot connect to ap0"
     sys.exit()
   elif ap0_pass == 0:
     vut.sendline('superman')
 time.sleep(5)
 #vut.sendline('exit\r')
 vut.sendline('exit')
 time.sleep(20)
 vut.sendline('status')
 vut.sendline('wlan')
 vut.sendline('show')
 time.sleep(10)
 ap0_ssid = vut.expect(['SUBHA_DEVICE','Disconnected'])
 #print "ap0",ap0_ssid
 
 vut.sendline('show')
 time.sleep(3)
 wlan_status = vut.expect(['Connected','Disconnected'])
 #print "wlan",wlan_status
 
 vut.sendline('show')
 time.sleep(3)
 sec_suite = vut.expect([security_suite,'Disconnected'])
 #print "security",sec_suite
 
 encr = vut.sendline('show')
 time.sleep(3)
 encr = vut.expect([encryption,'Disconnected'])
 #print "encryption",encr
 
 vut.sendline('exit')
 vut.sendline('interface wlan0')
 vut.sendline('show')
 time.sleep(4)
 ip_add = vut.expect(['192.168.0.1','No link'])
 vut.sendline('exit\r')
 vut.sendline('exit\r')

 if wlan_status == 0 and ap0_ssid == 0 and sec_suite == 0 and encr == 0 and ip_add == 0:
  print "connected to ap0.test case passed",security_suite,encryption
 else: 
  print "failed to connect to ap0.test case failed",security_suite,encryption

 if ap0_mode == 'Triggered' or ap0_mode == 'Initial Trigger':
   print "wait for uptime to expire"
   time.sleep(125)
   vut.sendline('status')
   vut.expect('status')
   vut.sendline('wlan')
   time.sleep(3)
   #vut.expect('status WLAN') 
   vut.sendline('show')
   time.sleep(4)
   wlan0_status = vut.expect(['Disconnected','Connected'])
   if wlan0_status == 1:
     print "client is connected. ap0 up"
     vut.sendline('exit')
     vut.sendline('exit')
     vut.sendline('status\r')
     vut.expect('status')
     vut.sendline('device\r')
     #vut.expect('status Device')
     vut.sendline('reboot')
     time.sleep(4)
     vut.expect('okay/cancel')
     time.sleep(2)
     vut.sendline('okay\r')
     time.sleep(2)
     print ("Rebooting to disconnect vut from ap0")
     vut.expect('Rebooting')
     time.sleep(10)
     ap0_status(ap0_mode)
     
   elif wlan0_status == 0:
     print "ap0 down.test case failed"
   vut.sendline('exit')
   vut.sendline('exit')

 vut.sendline('exit')
 vut.sendline('exit')
 vut.close()

  
#main program
fs()

print "TEST WPA2 CCMP"
ap0('WPA2','CCMP','always')
time.sleep(4)
print "TEST WPA TKIP"
ap0('WPA','TKIP','always')
time.sleep(4)
print "TEST WPA2 TKIP"
ap0('WPA2','TKIP','always')
time.sleep(4)
print "TEST WPA CCMP"
ap0('WPA','CCMP','always')
time.sleep(4)

#fs()
print "TEST WPA2 CCMP"
ap0('WPA2','CCMP','Triggered')
time.sleep(4)
ap0('WPA2','CCMP','Triggered')
print "TEST WPA TKIP"
ap0('WPA','TKIP','Triggered')
time.sleep(4)
print "TEST WPA2 TKIP"
ap0('WPA2','TKIP','Triggered')
time.sleep(4)
print "TEST WPA CCMP"
ap0('WPA','CCMP','Triggered')
time.sleep(4)

#fs()
print "TEST WPA2 CCMP"
ap0('WPA2','CCMP','Initial Trigger')
time.sleep(4)
print "TEST WPA TKIP"
ap0('WPA','TKIP','Initial Trigger')
time.sleep(4)
print "TEST WPA2 TKIP"
ap0('WPA2','TKIP','Initial Trigger')
time.sleep(4)
print "TEST WPA CCMP"
ap0('WPA','CCMP','Initial Trigger')
time.sleep(4)


sys.exit()

#subprocess.call("python /home/LtrxEngr/check.py",shell = True)
