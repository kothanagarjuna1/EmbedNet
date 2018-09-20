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
import decimal


def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>" + "<serial port> ")
 return

if len(sys.argv) < 2:
    script_usage()
    sys.exit()

device_ip = sys.argv[1]
serial_port = sys.argv[2]

def reboot():
  print "reboot device"
  pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")
  time.sleep(30)

def virtualLine(line):
  reboot()
  print "Configure baud rate and set flow control to hardware"
  deviceid = pexpect.spawn('telnet '+device_ip)
  time.sleep(8)
  deviceid.sendline('config')
  deviceid.sendline('mach10\r')
  deviceid.sendline('line 1\r')
  deviceid.sendline('state enabled\r')
  deviceid.sendline('write\r')
  deviceid.sendline('exit')
  deviceid.sendline('line virtual_1\r')
  deviceid.sendline('state enabled\r')
  deviceid.sendline('write\r')
  deviceid.sendline('exit')
  deviceid.sendline('line virtual_2\r')
  deviceid.sendline('state enabled\r')
  deviceid.sendline('write\r')
  deviceid.sendline('exit')
  deviceid.sendline('exit')
  deviceid.sendline('line 1')
  deviceid.sendline('baud rate 9600')
  time.sleep(3)
  deviceid.sendline('flow control hardware')
  time.sleep(2)
  deviceid.sendline('protocol mux')
  time.sleep(2)
  deviceid.sendline('flow control hardware')
  deviceid.sendline('write')
  time.sleep(2)
  deviceid.sendline('exit')
  deviceid.sendline('line virtual_'+line)
  deviceid.sendline('protocol tunnel')
  deviceid.sendline('flow control hardware')
  deviceid.sendline('exit')
  if line == "1":
   deviceid.sendline('tunnel virtual_'+line)
   deviceid.sendline('accept')
   deviceid.sendline('local port 10003')
  elif line == '2':
   deviceid.sendline('tunnel virtual_'+line)
   deviceid.sendline('accept')
   deviceid.sendline('local port 10004') 
  deviceid.sendline('write')
  time.sleep(5)
  deviceid.close()

  print "Test Case Tunnel Virtual Line Protocol Tunnel"
  ser = serial.Serial(serial_port,rtscts=True)
  ser.flushOutput()
  ser.flushInput()
  ser.close()
  ser.open() 
 
  ser1 = os.open(serial_port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY )
  serid = pexpect.fdpexpect.fdspawn(ser1)

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  if line == "1":
   tunport = int(10003)
  elif line == "2":
   tunport = int(10004)
  sock.connect((device_ip, tunport))
  
  ser.write('1v'+line+'\r')
  time.sleep(2)
  start_inst = serid.expect('K')
  print "res is",start_inst
  time.sleep(3)
  print "send data from serial"
  ser.write('1sb~\r')
  time.sleep(3)
  ser.write('def~\r')
  time.sleep(5)
  ser.write('1p\r')
  time.sleep(5)
  x = sock.recv(100)
  print"data", x

  print "send data from network"
  sock.send('abc\r')
  time.sleep(5)
  ser.write('1rb.100\r')
  time.sleep(3)
  net_res = serid.expect('Kabc')
  print "res is",net_res
  time.sleep(3)

  print "end virtual instance"
  ser.write('1k\r')
  #ser.write('1K\r')
  time.sleep(3)
  end = serid.expect('K')
 
  if start_inst == 0:
    if x == 'def' and net_res == 0 and end == 0:
      print "Tunnel Virtual Line_"+line+" Test Case Passed"
      res = 1
    else:
      print "Tunnel Virutal Line_"+line+" Test Case Failed"
  else:
    print "Failed to start virtual instance"
    res = 0


  print "Test Case: Line Virutal Protocol Command Line"
  deviceid = pexpect.spawn('telnet '+device_ip)
  deviceid.sendline('config')
  deviceid.sendline('line virtual_'+line)
  deviceid.sendline('protocol command line')
  ser.write('1v'+line+'\r')
  time.sleep(8)
  ser.write('1rb.100\r')
  time.sleep(5)
  data = ser.read(20)
  print "data read is",data
  pat = re.search('Command Line',data)
  print "end virtual instance"
  ser.write('1k\r')
  #ser.write('1K\r')
  time.sleep(3)
  end = serid.expect('K')
  if pat.group() == 'Command Line':
   if end == 0:
    print "Virutal Line_"+line+" Protocol Command Line Test Case Passed"
    res = 1
   else:
    print "Failed to end connection.Test Case Failed"
  else:
   print "Virtual Line_"+line+" Protocol Command Line Test Case Failed"
   res = 0 
 
  deviceid.close()
  
  print "Test Case: Line Virtual Protcol Mach10 Command Line"

  deviceid = pexpect.spawn('telnet '+device_ip)
  deviceid.sendline('config')
  deviceid.sendline('line virtual_'+line)
  deviceid.sendline('protocol mach10 command interface')
  ser.write('1v'+line+'\r')
  time.sleep(8)
  ser.write('1sb~\r')
  time.sleep(6)
#  res = serid.expect('500K')
 # print "res",res
  ser.write('mach10_getsettings~\r')
  time.sleep(6)
  m_res = serid.expect('K')
  print m_res
  ser.write('1p\r')
  time.sleep(4)
  p_res = serid.expect('K')
  print p_res
  ser.write('1rb~2000\r')
  time.sleep(4)
  bytesToRead = ser.inWaiting()
  serdata = ser.read(bytesToRead)
  print "serdata",serdata
  mach10_res = re.search('project_tag',serdata)
  print "res",mach10_res.group()
  #mach10_res = serid.expect('K{"project_tag":')  
  #print mach10_res
  ser.write('1k')
  end = serid.expect('K')

  if m_res == 0 and p_res == 0 and mach10_res.group() == 'project_tag' and end == 0:
   print "Line Virtual Line_"+line+" Protocol Mach10 Command Interface Test Case Passed"
   res = 1
  else:
   print "Line Virtual Line_"+line+" Protocol Mach10 Command Interface Test Case Failed"
   res = 0

  deviceid.close()
  
  print "Test Case Virtual Line Modem Emulation" 
  #reboot()
  deviceid = pexpect.spawn('telnet '+device_ip)
  deviceid.sendline('config')
  deviceid.sendline('line virtual_'+line)
  deviceid.sendline('protocol modem emulation')
  ser.write('1v'+line+'\r')
  time.sleep(4)
  ser.write('1rb.200\r')
  time.sleep(4)
  ser.write('1sx\r')
  time.sleep(4)
  ser.write('61740d\r')
  time.sleep(4)
  at_res = serid.expect('K')
  ser.write('1p\r')
  time.sleep(4)
  p = serid.expect('K')
  ser.write('1rb~200\r')
  time.sleep(4)
  modem_res = serid.expect('OK')
  print modem_res
  ser.write('1k\r')
  time.sleep(3)
  end = serid.expect('K')
  if modem_res == 0 and end == 0:
   print "Line Virtual Line_"+line+" Modem Emulation Test Case Passed"
   res = 1
  else:
   print "Line Virutal Line_"+line+" Modem Emulation Test Case Failed"
   res = 0

  print "Test Case Virtual Line Modem Emulation"
  reboot()
  ser = serial.Serial(serial_port,rtscts=True)
  ser.close()
  ser.open()
  ser.flushInput()
  ser.flushOutput()

  ser1 = os.open(serial_port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY )
  serid = pexpect.fdpexpect.fdspawn(ser1)
  deviceid = pexpect.spawn('telnet '+device_ip)
  deviceid.sendline('config')
  deviceid.sendline('line virtual_'+line)
  deviceid.sendline('protocol trouble log')
  ser.write('1v'+line+'\r')
  time.sleep(4)
  r = serid.expect('K')
  print r
  ser.write('1sb~\r')
  time.sleep(4)
  ser.write('tlog~\r')
  time.sleep(4)
  ser.write('1p\r')
  time.sleep(4)
  print "here"
  ser.write('1rb~1000\r')
  time.sleep(5)
  bytesToRead = ser.inWaiting()
  serdata = ser.read(bytesToRead)
  print "serdata",serdata
  tlog = re.search('Reset occurred',serdata)
  if tlog:
   print "Line Virtual_"+line+" Trouble Log Test Case Passed"
   res = 1
  else:
   print "Line Virtual "+line+" Trouble Log Test Case Failed"
   res = 0


  print "Test Case Virtual Line Protocol None"
  reboot()
  ser = serial.Serial(serial_port,9600)
  ser.close()
  ser.open()
  ser.flushInput()
  ser.flushOutput()

  ser1 = os.open(serial_port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY )
  serid = pexpect.fdpexpect.fdspawn(ser1)

  deviceid = pexpect.spawn('telnet '+device_ip)
  deviceid.sendline('config')
  deviceid.sendline('line virtual_'+line)
  deviceid.sendline('protocol none')
  time.sleep(3)
  deviceid.sendline('write')

  ser.write('1v'+line+'\r')
  time.sleep(2)
  r1 = serid.expect('K')
  print r1
  ser.write('1sb~\r')
  time.sleep(6)
  ser.write('abc~\r')
  time.sleep(4)
  r2 = serid.expect('K')
  print r2
  ser.write('1p\r')
  time.sleep(4)
  r3 = serid.expect('K')
  print r3
  print "line receive"
  line_receive = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d"  +'"' +"group=Line&optionalGroupInstance=virtual_"+line+"&action=Receive&optionalItem=Receiver")
  print "line receive",line_receive
  res = re.search('abc',line_receive)
  if res:
       print "line receive picks up characters.Virtual Line_"+line+" Protocol None Test Case Passed"
       res = 1
  else:
       print "failed to receive characters.Virtual Line_"+line+" Protocol None Test Case Failed"
       res = 0
  ser.write('1k\r')
  time.sleep(3)

  print "line transmit"
  ser.write('1v'+line+'\r')
  time.sleep(3)
  ser.write('1rb~100\r')
  time.sleep(3)
  line_transmit = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"' +"group=Line&optionalGroupInstance=virtual_"+line+"&action=Transmit+H&optionalItem=Transmitter")
  time.sleep(3)
  ser.write('1rb~100\r')
  time.sleep(3)
  x = serid.expect('H') 
  print "x", x
  if x == 0:
    print "line transmitted characters successfully.Virtual Line_"+line+" Protocol None Test Case Passed"
    res = 1
  else:
    print "failed to transmit characters.Virtual Line_"+line+" Protocol None Test Case Failed"
    res = 0


  if res == 1:
   print "Virutal Line_"+line+" TEST CASE PASSED"
  else:
   print "Virtual Line_"+line+" TEST CASE FAILED"

  deviceid.close()

print "Test Line Virtual_1"
virtualLine("1")

print "Test Line Virutal_2"
virtualLine("2")

sys.exit()

