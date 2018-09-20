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
#import numpy
import re
#import requests
import time
import datetime


script_path = "/home/lantronix/MIDAS/xml/"

def print_f(log_str, log_str1='NONE'):
    showtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if log_str1 == 'NONE':
        print ("{0} \t {1}").format(str(showtime), log_str)
    else:
        print ("{0} \t {1} {2}").format(str(showtime), log_str, log_str1)

def VUT_factorydefaults(vut_ip):
    clientid = pexpect.spawn('telnet '+vut_ip)
    clientid.sendline('\r')
    clientid.sendline('\r')
    time.sleep(3)
    clientid.sendline('enable\r')
    clientid.expect('enable')
    clientid.sendline('reload factory defaults\r')
    clientid.sendline('yes\r')
    clientid.sendline('no\r')
    print_f("EDS4100 reload factory defaults.......")
    time.sleep(2)
    print_f(".......................................")
    time.sleep(2)
    print_f(".......................................")
    time.sleep(2)
    print_f("device is rebooting")
    time.sleep(2)
"""
def xpico_factorydefaults():
    clientid = pexpect.spawn('telnet '+device_ip)
    clientid.sendline('\r')
    clientid.sendline('\r')
    time.sleep(3)
    clientid.sendline('status\r')
    time.sleep(2)
    clientid.sendline('device\r')
    time.sleep(2)
    clientid.sendline('factory Defaults\r')
    time.sleep(2)
    clientid.sendline('okay\r')
    time.sleep(2)
    print_f("xpico200 factory defaults.......")
    print_f("device is rebooting")
    time.sleep(30)
"""
def xport_CPM(device_ip):
  print "Configure CTS & RTS enable"
  deviceid = pexpect.spawn('telnet '+device_ip)
  time.sleep(8)
  deviceid.sendline('config')
  deviceid.sendline('cpM')
  deviceid.sendline('role  Line 1 Flow.CTS')
  deviceid.sendline('state enabled')
  deviceid.sendline('role  Line 1 Flow.RTS')
  deviceid.sendline('state enabled')
  deviceid.sendline('write')
  deviceid.sendline('exit')
  deviceid.sendline('exit')
  deviceid.sendline('exit')
  deviceid.sendline('exit')

def factorydefaults(device_ip): 
    pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=factory Defaults")
    time.sleep(2)
    print_f("factory defaults the device")
    time.sleep(2)
    print_f("...............................")
    time.sleep(2)
    print_f("...............................")
    time.sleep(5)
    print_f("device is rebooting")
    time.sleep(30)

def reboot(device_ip):
	pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")
	time.sleep(2)
	print_f("...............................")
	time.sleep(5)
	print_f("device is rebooting")
	time.sleep(30)

def telnet(device_ip):
    print_f("configure device")
    pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form configrecord=@"+script_path+"telnet.xml")
    time.sleep(5)
    print_f("enabled telnet ........")

def wlan_up(device_ip):
    print_f("configure device")
    pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form configrecord=@"+script_path+"wlan0.xml")
    time.sleep(15)
    print_f("wlan0 link is up")
    print_f("enabled telnet ........")
    time.sleep(30)


def USB_HOST_up(device_ip):
   	clientid = pexpect.spawn('telnet '+device_ip)
    #clientid.sendline('\r')
	clientid.sendline('\r')
	time.sleep(3)
	clientid.sendline('config\r')
	time.sleep(3)
	clientid.sendline('uSB Host\r')
	time.sleep(3)
	clientid.sendline('state enabled\r')
	time.sleep(3)
	clientid.sendline('write\r')
	time.sleep(3)
	clientid.sendline('exit\r')
	time.sleep(3)
	clientid.sendline('cpM\r')
	time.sleep(3)
	clientid.sendline('role uSB Host Overcurrent\r')
	time.sleep(3)
	clientid.sendline('state enabled\r')
	time.sleep(3)
	clientid.sendline('write\r')
	time.sleep(3)
	clientid.sendline('exit\r')
	time.sleep(3)
	clientid.sendline('exit\r')
	time.sleep(3)
	clientid.sendline('exit\r')
	time.sleep(3)
	clientid.sendline('exit\r')
	time.sleep(5)
	print_f("USB line enumurated....after reboot")
	reboot(device_ip)

def wlan_radius_up(device_ip):
    print_f("configure device")
    pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form configrecord=@"+script_path+"radius_profile.xml")
    time.sleep(15)
    print_f("wlan0 radius link is up")
    print_f("enabled telnet ........")
    time.sleep(30)