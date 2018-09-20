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
import urllib
import urllib2
import httplib
#from requests.auth import HTTPBasicAuth
import urllib2, sys, re, base64
from urlparse import urlparse
#from mechanize import Browser
import threading, time
import signal
import telnetlib
from time import gmtime, strftime


def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>" + "<config_FW>")
 return

if len(sys.argv) < 2:
    script_usage()
    sys.exit()


device_ip = sys.argv[1]
config_FW = sys.argv[2] #configuration or firmware update

showtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
  

def rebootDevice():
 pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")
 print str(showtime) + "\t device is rebooting"
 time.sleep(30)

def factorydefaults():
 pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=factory Defaults")
 print str(showtime) + "\t factory defaults the device"
 time.sleep(2)
 print str(showtime) + "\t ..............................."
 time.sleep(2)
 print str(showtime) + "\t ..............................."
 time.sleep(5)
 print str(showtime) + "\t device is rebooting"
 time.sleep(30)

def ping():
 ping1 = pexpect.run('ping -c 5 ' +device_ip)
 #print ping1
 ping_res = 1
 if re.search('100%',ping1):
   print str(showtime) + "\t cannot ping device"
   ping_res = 0
 else:
   print str(showtime) + "\t able to ping device"
 print str(showtime) + "\t ping_res",ping_res
 return ping_res


def Reg():
  print str(showtime) + "\t Test case : Davice registration with mach10 server"
    
  #tlog = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/tlog")
  #print "data: " + str(tlog)
  print str(showtime) + "\t ............................................"
  print str(showtime) + "\t ............................................"
  print str(showtime) + "\t device checking with mach10 server.... Registration successfull or not"

  count = 0
  while True:
  	time.sleep(1)
  	count = count + 1
        tlog = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/tlog")
  	if str(tlog).__contains__('Registered successfully'):
                print str(showtime) + "\t data: " + str(tlog)
  		print str(showtime) + "\t Device registred successfully with mach10 server : PASSED"
  		break
  	if ("Registered successfully" not in tlog) and (count > 100):
  		print str(showtime) + "\t Firmware upgrade Test case FAILED" 
  		break

  
def config():
  print str(showtime) + "\t Test case : Config updates"
  print str(showtime) + "\t --------------------------------"
  tn = telnetlib.Telnet(device_ip)
  tn.read_until(b">")
  time.sleep(2)
  tn.write('status'.encode('ascii') + b"\n")
  tn.read_until(b"status>")
  time.sleep(2)
  tn.write('mach10'.encode('ascii') + b"\n")
  time.sleep(2)
  tn.read_until(b"status Mach10>")
  '''
  time.sleep(180)
  tn.write('show'.encode('ascii') + b"\n")
  print "wait 5 sec to print  status:"
  data = tn.read_until(b"status Mach10>")
  '''
  count = 0
  while True:
  	time.sleep(5)
  	count = count + 5
  	tn.write('show'.encode('ascii') + b"\n")
  	#print "wait 5 sec to print  status:"
  	data = tn.read_until(b"status Mach10>")
  	if str(data).__contains__('Successfully Applied'):
  		print str(showtime) + "\t data: " + str(data)
        	print str(showtime) + "\t Configured Updates successully from mach10 server"
        	print str(showtime) + "\t Apllying config updates TEST CASE PASSED"
  		break
  	if ('Successfully Applied' not in data) and (count > 180):
        	print "Apllying config updates Test case FAILED"
  		break

  """
  count = 0
  while True:
  	time.sleep(1)
  	count = count + 1
        tn = telnetlib.Telnet(device_ip)
        print "aaaa"
        tn.read_until(b">")
        #time.sleep(2)
        tn.write('status'.encode('ascii') + b"\n")
	print "bbbbb"
        tn.read_until(b"status>")
        #time.sleep(2)
        tn.write('mach10'.encode('ascii') + b"\n")
        print "ccccc"
        #time.sleep(2)
        tn.read_until(b"status Mach10>")
        #time.sleep(180)
        tn.write('show'.encode('ascii') + b"\n")
        data = tn.read_until(b"status Mach10>")
        #print "data: " + str(data)
  	if str(data).__contains__('Registered successfully'):
                print "data: " + str(data)
  		print "Configured Updates successully from mach10 server"
		print "Apllying config updates Test case PASSED"
  		break
  	if ("Registered successfully" not in data) and (count > 150):
  		print "Apllying config updates Test case FAILED" 
  		break
	tn.write("exit\n")
  """

def FW():
  print str(showtime) + "\t ------------------------------"
  print str(showtime) + "\t ------------------------------"
  print str(showtime) + "\t Test case : Firmware upgrade"
  print "------------------------------"
  
  #tlog = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/tlog")
  #print "data: " + str(tlog)
  print str(showtime) + "\t ............................................"
  print str(showtime) + "\t ............................................"
  print str(showtime) + "\t started firmware uploading..........."
  count = 0
  while True:
  	time.sleep(1)
  	count = count + 1
        tlog = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/tlog")
  	if str(tlog).__contains__('Firmware upgrade successful'):
                print str(showtime) + "\t data: " + str(tlog)
                time.sleep(2)
  		print str(showtime) + "\t Firmware Update successully from mach10 server"
		time.sleep(2)
  		print str(showtime) + "\t Firmware upgrade TEST CASE PASSED"
                time.sleep(2)
  		print str(showtime) + "\t Device rebooting"
  		break
  	if ("Firmware upgrade successful" not in tlog) and (count > 600):
  		print str(showtime) + "\t Firmware upgrade Test case FAILED" 
  		break

def mach10():
  
  factorydefaults()
  print str(showtime) + "\t Configuring xpico240 for mach10"
  if (config_FW == 'FW'):
     mach10_FW = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+script_path+"mach10_FW.xml")
     time.sleep(10)
     print str(showtime) + "\t mach10 device configuration imported successfully\n" + str(mach10_FW)
     Reg()
     FW()
     mach10_config = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+script_path+"mach10.xml")
  else:
     mach10_config = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+script_path+"mach10.xml")
     time.sleep(10)
     Reg()
     print str(showtime) + "\t mach10 device configuration imported successfully\n" + str(mach10_config)
     config()  
#main program

mach10()

sys.exit()


