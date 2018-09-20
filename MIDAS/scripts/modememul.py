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

print "Test Modem Emulation"
print "===================="

#syntax

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <serial_port>" + " <baudrate>" + " <databits>" + " <parity>" + " <stopbits>" " <device_ip>" + " <tunnel_port>" + " <filename>")
 return

if len(sys.argv) < 8:
    script_usage()
    sys.exit()

serial_port = sys.argv[1]
baudrate = sys.argv[2]
databits = sys.argv[3]
parity = sys.argv[4]
stopbits = sys.argv[5]
device_ip = sys.argv[6]
tunnel_port = sys.argv[7]
filename = sys.argv[8]


def modem_outbound():
  ser = serial.Serial(serial_port, '{0}'.format(baudrate), timeout=0, parity='{0}'.format(parity), stopbits = int('{0}'.format(stopbits)), bytesize = int('{0}'.format(databits)), rtscts = True)
  childid = pexpect.fdpexpect.fdspawn(ser)
  if ser.isOpen():
   ser.flushInput()
   ser.flushOutput()
   print 'serial opened'
   time.sleep(10)
   print 'test case: modem emulation commands' 
   childid.sendline('at\r')
   time.sleep(10) #required for line 3
   outfile = childid.expect(['123','OK'])
   print outfile
  if outfile == 1: 
   print "response OK"
  else:
   print "response NOT OK"
   sys.exit()
  print "test case:  modem emulation outbound connection"
  childid.sendline('atdt192.168.51.195:23\r')
  time.sleep(25) # required for line 3
  #result = childid.expect(['>','CONNECT'])
  result = childid.expect(['>'.format(baudrate)])
  print result
  if result == 0:
   print "connection successful"
  else:
   print "no answer"
  childid.delaybeforesend = 0
  childid.sendline("+++")
  ser.close()
  #childid.close()
  return result
  

def modem_inbound(fname, conn_type):
 ser = serial.Serial(serial_port, '{0}'.format(baudrate), timeout=0, parity='{0}'.format(parity), stopbits = int('{0}'.format(stopbits)), bytesize = int('{0}'.format(databits)), rtscts = True)
 childid = pexpect.fdpexpect.fdspawn(ser)
 ser.close()
 ser.open()
 time.sleep(5)
 print fname
 result = 0
 if ser.isOpen():
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  host = device_ip
  port = int(tunnel_port)
  s.connect((device_ip,port))
  pexpect.run('rm tunneldata')
  pexpect.run('rm serialdata')
  if (conn_type == 'manual'):
   ser.write('ata\r')
   time.sleep(5)
  f = open(fname,'rb')
  z = bytearray(f.read(10000))
  while z:
   print "sending data from network to serial..."
   s.sendall(z)
   serdata = open('serialdata','a')
   seread = ser.read()
   serdata.write(seread)
   time.sleep(10)
   serdata.close()
   x = ser.inWaiting()
   for i in range (0,5): # run loop to make sure all the data is read.this is mandatory for tunnel modem emulation
    if x != 0:
     seread = ser.read(ser.inWaiting())
     time.sleep(5) #wait until all the data is read
     serdata = open('serialdata','a')
     time.sleep(10)
     serdata.write(seread)
     time.sleep(10)
    #ser.flushInput()
     #ser.flushOutput()
   else:
    time.sleep(3)
   
   time.sleep(2)
   print "sending data from serial to network..."
   ser.write(z)
   time.sleep(5)
   z = bytearray(f.read(10000))
   datarecv = s.recv(102400)
   tdata = open('tunneldata','a')
   time.sleep(10)
   tdata.write(datarecv)
   time.sleep(10)
   tdata.close()
   serdata.close()
 print "data sent through the tunnel"

 print "check data received"
 actualfilesize = os.path.getsize(fname)
 print actualfilesize
 tunfile = open('tunneldata','r')
 serfile = open('serialdata','r')
 fsize1 = os.path.getsize('tunneldata')
 print fsize1
 fsize2 = os.path.getsize('serialdata')
 print fsize2
 if (fsize1 == actualfilesize) and (fsize2 >= actualfilesize):
  print "data sent through the tunnel"
  result = 1
 else:
  print "failed to send data"
 f.close()
 tunfile.close()
 serfile.close()
 ser.close()
 return result 

def device_config(port , conn_type):
  clientid = pexpect.spawn("telnet "+device_ip)
  clientid.sendline('status\r')
  clientid.expect('status')
  clientid.sendline('device\r')
  clientid.expect('status Device')
  clientid.sendline('reboot')
  clientid.expect('okay/cancel')
  clientid.sendline('okay\r')
  print ("Rebooting")
  #clientid.expect('Rebooting')
  time.sleep(60)
  clientid = pexpect.spawn("telnet "+device_ip)
  clientid.sendline('\r')
  clientid.sendline('\r')
  clientid.sendline('config\r')
  clientid.expect('config')
  clientid.sendline('line 1')
  clientid.expect('config Line 1')
  clientid.sendline('baud rate {0}'.format(baudrate))
  clientid.expect('config Line 1')
  clientid.sendline('data bits {0}'.format(databits))
  clientid.expect('config Line 1')
  clientid.sendline('parity {0}'.format(parity))
  clientid.expect('config Line 1')
  clientid.sendline('stop bits {0}'.format(stopbits))
  clientid.expect('config Line 1')
  clientid.sendline('flow control hardware\r')
  clientid.expect('config Line 1')
  clientid.sendline('protocol modem emulation\r')
  clientid.sendline('exit\r')
  clientid.expect('config')
  clientid.sendline('write\r')
  clientid.expect('config')
  clientid.sendline('write\r')
  clientid.expect('config')
  clientid.sendline('exit\r')
  clientid.expect('>')
  #clientid.sendline('status\r')
  #clientid.expect('status')
  #clientid.sendline('modem emulation 1')
  #clientid.expect('status Modem Emulation 1')
  #clientid.sendline('current connection\r')
  #clientid.expect('status Modem Emulation 1')
  #clientid.sendline('kill\r')
  #clientid.expect('okay/cancel')
  #clientid.sendline('okay\r')
  #time.sleep(5)
  #clientid.expect('status Modem Emulation 1')
  kill = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d "+ '"'+ "group=Modem Emulation&optionalGroupInstance=1&optionalItem=Current Connection&optionalItemInstance=&action=Kill"+'"')
  print "connection killed"
  #clientid.sendline('exit\r')
  #clientid.expect('status Modem Emulation 1')
  #clientid.sendline('exit\r')
  #clientid.expect('status')
  #clientid.sendline('write\r')
  #clientid.expect('status')
  #clientid.sendline('exit\r')
  #clientid.expect('>')
  clientid.sendline('config\r')
  clientid.expect('config')
  clientid.sendline('modem emulation 1')
  clientid.expect('config Modem Emulation 1')
  print conn_type
  if (conn_type == 'automatic'):
   print "test incoming connection automatic"
   clientid.sendline('incoming connection automatic\r')
  elif (conn_type == 'manual'):
   print "test incoming connection manual"
   clientid.sendline('incoming connection manual\r')
  clientid.expect('config Modem Emulation 1')
  clientid.sendline('listen port {0}'.format(port))
  clientid.expect('config Modem Emulation 1')
  clientid.sendline('exit\r')
  clientid.expect('config')
  clientid.sendline('write\r')
  clientid.expect('config')
  clientid.sendline('exit\r')
  clientid.expect('>')
  clientid.close()
  print "test case: modem emulation inbound connection"
  if conn_type == 'automatic':
   inbound_auto = modem_inbound(filename, 'automatic')
  elif conn_type == 'manual':
   inbound_auto = modem_inbound(filename, 'manual')
 
  if (inbound_auto == 1):
    print "modem emul inbound connection passed",conn_type
  else:
    print "modem emul inbound connection failed",conn_type

# main program
device_config(tunnel_port,'automatic')
device_config(tunnel_port,'manual')
outbound_res = modem_outbound()
if outbound_res == 0:
  print "modem emul tunnel outbound connection TEST CASE PASSED"
else:
  print "modem emul tunnel outbound connection failed"

sys.exit()
