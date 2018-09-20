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

print "Test Tunnel Multiple Connections"
print "================================"

#syntax

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>" + " <device_serial_port> ")
 return

if len(sys.argv) < 2:
    script_usage()
    sys.exit()

device_ip = sys.argv[1]
serial_port = sys.argv[2]

xml_path = "/home/ltrxengr/xpico200/xml/"

def fileCompare(mul_conn):
 file1 = open('100ktext.dat', 'r')
 fread1 = file1.readlines()
 if mul_conn == '0':
  file2 = open('serialdata.txt', 'r')
 elif mul_conn == '1':
  file2 = open('tunlog1.txt','r')
  file3 = open('tunlog2.txt','r')
  file4 = open('tunlog3.txt','r')
  file5 = open('tunlog4.txt','r')
 result = 0
 if mul_conn == '0':
  fread2 = file2.readlines()
 elif mul_conn == '1':
  fread2 = file2.readlines()
  fread3 = file3.readlines()
  fread4 = file4.readlines()
  fread5 = file5.readlines()


 if mul_conn == '0':
  if (fread1 == fread2):
   print ('file match.TCP tunnel test PASSED')
   result = 1
  else:
   print ('file different.TCP tunnel test FAILED.')
 elif mul_conn == '1':
  if fread1 == fread2 == fread3 == fread4 == fread5:
   print ('file match.TCP tunnel test PASSED')
   result = 1
  else:
   print ('file different.TCP tunnel test FAILED.')


 return result

 file1.close()
 file2.close()
 file3.close()
 file4.close()

def sendFile(fname,mul_conn):
#open socket connection to port 10001
 s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 if mul_conn == '1':
   s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 tunnel_port = 10001
 host = device_ip
 port = int(tunnel_port)
 s.connect((device_ip,port))
 time.sleep(3)
 if mul_conn == '1':
   s1.connect((device_ip,port))
   time.sleep(3)
   s2.connect((device_ip,port))
   time.sleep(3)
   s3.connect((device_ip,port))
   time.sleep(3)
 pexpect.run('rm logfile.txt serialdata.txt tunlog1.txt tunlog2.txt tunlog3.txt tunlog4.txt')
 ser = serial.Serial(serial_port,rtscts = True, dsrdtr = False)
 ser.close()
 ser.open()
 time.sleep(5)
 if ser.isOpen():
  print ('serial opened')
  ser.flushInput()
  ser.flushOutput()
  f = open(fname,'r')
  z = bytearray(f.read(10000))
  if mul_conn == '0':
   while z:
    #if ('{0}'.format(flag) == '0') or ('{0}'.format(flag) == '2'):
      s.sendall(z)
      serdata = open('serialdata.txt','a')
      seread = ser.read()
      serdata.write(seread)
      serdata.close()
      x = ser.inWaiting()
      print (x)
      for i in range (0,5):
       if x != 0:
        serdata= open('serialdata.txt','a')
        seread = ser.read(ser.inWaiting())
        time.sleep(5)
        serdata.write(seread)
       #ser.flushInput()
       #ser.flushOutput()
        serdata.close()
       else:
        time.sleep(2)
      print ("data sent through tunnel")
      outfile = open('logfile.txt','a')
      ser.write(z)
      time.sleep(20)
      z = bytearray(f.read(15000))
      recvdata = s.recv(102400)
      outfile.write(recvdata)
      print ('data written')
      outfile.close()
      #fileCompare('0')
  elif mul_conn == '1':
   while z:
      tun1 = open('tunlog1.txt','a')
      tun2 = open('tunlog2.txt','a')
      tun3 = open('tunlog3.txt','a')
      tun4 = open('tunlog4.txt','a')
      ser.write(z)
      time.sleep(20)
      z = bytearray(f.read(15000))
      tundata1 = s.recv(102400)
      tun1.write(tundata1)
      print ('data written')
      tundata2 = s1.recv(102400)
      tun2.write(tundata2)
      tundata3 = s2.recv(102400)
      tun3.write(tundata3)
      tundata4 = s3.recv(102400)
      tun4.write(tundata4)
      tun1.close()
      tun2.close()
      tun3.close()
      tun4.close()
      #fileCompare('1')
 
 else:
  print ('cannot open serial port')
 f.close()
 s.close()
 ser.close()


def device_config(serial_port,mul_conn):
  print "reboot device"
  pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")
  time.sleep(25)
  clientid = pexpect.spawn('telnet '+device_ip)
  clientid.sendline('enable')
  clientid.sendline('config')
  clientid.sendline('line 1')
  clientid.sendline('protocol tunnel')
  clientid.sendline('exit')
  clientid.sendline('tunnel 1')
  clientid.sendline('accept')
  clientid.sendline('local port 10001')
  if mul_conn == '0':
   print "disable multiple connections"
   clientid.sendline('multiple connection disabled\r')
  elif mul_conn == '1':
    print "enable multiple connections"
    clientid.sendline('multiple connection enabled\r')
    time.sleep(2)
  clientid.sendline('write')
  time.sleep(2)
  if mul_conn == '1':
   sendFile('100ktext.dat','1')
   fileCompare('1')
  elif mul_conn == '0':
   sendFile('100ktext.dat','0')
   fileCompare('0')
#main program 
#print "Test one incoming tunnel"
#device_config(serial_port,'0')
print "Test multiple incoming tunnels"
print "Test multiple incoming tunnels.Supports 4 tunnels"
device_config(serial_port,'1')

sys.exit()

#subprocess.call("python /home/LtrxEngr/check.py",shell = True)
