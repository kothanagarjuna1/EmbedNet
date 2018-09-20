#!usr/local/bin/python3

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

print "Test MUX"
print "========="

#syntax

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <serial_port>" + " <baudrate>" + " <databits>" + " <parity>" + " <stopbits>" + " <device_ip>" + " <tunnel_port>" +  " <serial_line>" + " <remote pc/vut>" + " <conn_type>" + " <protocol>" + "<restricted>" + " <interface>")
 return

if len(sys.argv) < 13:
    script_usage()
    sys.exit()

serial_port = sys.argv[1]
baudrate = sys.argv[2]
databits = sys.argv[3]
parity = sys.argv[4]
stopbits = sys.argv[5]
device_ip = sys.argv[6]
tunnel_port = sys.argv[7]
serial_line = sys.argv[8]
remote_ip = sys.argv[9] #must be linux pc
conn_type = sys.argv[10]
protocol = sys.argv[11] # tcp or udp
restricted = sys.argv[12] # values 1 or 0
network = sys.argv[13]

print network

class Timeout():
  """Timeout class using ALARM signal"""
  class Timeout(Exception): pass

  def __init__(self, sec):
    self.sec = sec

  def __enter__(self):
    signal.signal(signal.SIGALRM, self.raise_timeout)
    signal.alarm(self.sec)

  def __exit__(self, *args):
    signal.alarm(0) # disable alarm

  def raise_timeout(self, *args):
    raise Timeout.Timeout()

def mux_http():
  ser = serial.Serial(serial_port)
  childid = pexpect.fdpexpect.fdspawn(ser)
  if ser.isOpen():
   print "serial opened"
   ser.write("1h\r")
   time.sleep(5)
   print "mux http started"
  else:
   print "failed to start mux http"
  out = childid.expect(['K', 'E'])
  print out
  if (out == 0):
     print "mux http instance started"
  else:
     print "failed to start mux instance"
  ser.write("1\r")
  time.sleep(5)
  out1 = childid.expect(['W', 'E'])
  if (out1 == 0):
    print "http instance verified"
  else:
    print "failed to verify http instance"
  
  br = Browser()
  time.sleep(5)
  br.set_handle_robots(False)
  time.sleep(5)
  req = br.open('http://'+device_ip+'/form.html')
  print "req is",req
  br.select_form(name='input')
  time.sleep(5)
  br['user'] = 's'
  time.sleep(5)
  br['email'] = 'pat'
  time.sleep(5)
  ser.write("1rb.100\r")
  time.sleep(5)
  #print "1rb command written"
   #req = br.click(type="submit")
  req = br.submit()
  time.sleep(10)
  print "submitted"
  ser.close()

def mux_tcp():
 print "mux outgoing connection tests begin"
 if (serial_line == '1') or (serial_line == '2'):
  ser = serial.Serial(serial_port, '{0}'.format(baudrate), timeout=0, parity='{0}'.format(parity), stopbits = int('{0}'.format(stopbits)), bytesize = int('{0}'.format(databits)), rtscts = True)
 else:
  ser = serial.Serial(serial_port)
 childid = pexpect.fdpexpect.fdspawn(ser)
 ser.close()
 ser.open()
 sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 tunport = int(tunnel_port)
 sock.settimeout(20)
 if (conn_type == 'connect'):
  sock.bind((remote_ip,4001))
  sock.listen(1)
 tunport = int(tunnel_port)
 result = 0
 muxrec_result = 0
 hexsend_result = 0
 sendbinary_result = 0
 readbinary_result = 0
 time.sleep(5)
 try:
  if ser.isOpen():
   print "serial opened"
   ser.flushInput()
   ser.flushOutput()
   time.sleep(10)
   print 'test case 1: mux receive'
   print "connect to remote host"
   if (conn_type == 'connect'): 
    ser.write('1c192.168.51.25:4001tcp\r')
    time.sleep(5)
    if (serial_line == 'CDC_ACM'):
     time.sleep(60)
   elif (conn_type == 'accept') and (restricted == '0'):
    if network == 'eth0':
     ser.write('1aeth0:10002tcp\r')
     time.sleep(3)
    elif network == 'wlan0':
     ser.write('1awlan0:10002tcp\r')
     time.sleep(3)
    print "check listening sockets"
    time.sleep(60)
    sock.connect((device_ip, tunport))
   elif (conn_type == 'accept') and (restricted == '1'):
    if network == 'eth0':
     print "here 1"
     ser.write('1aeth0:10002tcp\r')
     time.sleep(3)
    elif network == 'wlan0':
     ser.write('1awlan0:10002tcp\r')
     time.sleep(3)
    print "check listening sockets"
    time.sleep(60)
    sock.connect((device_ip, tunport))
   print "verify connection"
   ser.write("1\r")
   #time.sleep(2)
   out = childid.expect(['123','K'])
   #time.sleep(2)
   if (out == 1):
    print "connection established. received K"
   else:
    print "failed to establish the connection"
   if (conn_type == 'accept') and (restricted == '1'):
     if (out == 1):
      print "test case: tcp mux receive passed"
      muxrec_result = 1
     else:
      print "test case: tcp mux receive failed"
  
   if (conn_type == 'connect'): 
    conn,addr = sock.accept()
    print 'connected by',addr
    print "sending"
    print "waiting for receiving event/data"
    ser.write('W1r\r')
    time.sleep(5)
    print "send data"
    conn.send('abcde')
   #ser.write('W1r\r')
    time.sleep(5)

    print "check whether is data waiting"
    out1 = childid.expect(['3','1r'])
    if (out1 == 1):
     print "data is waiting. received 1r"
    else:
     print "there is no data"

    print "read and check data"
    ser.write('1rb.80\r')
    time.sleep(5)
    if (serial_line == 'CDC_ACM'):
     time.sleep(60)
    else:
     time.sleep(5)
    serdata = ser.read(10)
    time.sleep(5)
    print "reading data from serial"
    if (serial_line == 'CDC_ACM'):
     time.sleep(60)
    else:
     time.sleep(10)
    print serdata
    if (serdata == "Kabcde"):
     print "data read from serial"
    else:
     print "failed to read data from serial"

    if (out == 1) and (out1 == 1) and (serdata == 'Kabcde'):
     print "test case: tcp mux receive passed"
     muxrec_result = 1
    else:
     print "test case: tcp mux receive failed"
   
############################################

 
   print "test case 2: send and push Hex data"
   print "initiate hex data send"
   ser.write('1sx\r')
   #print "check"
   time.sleep(3)
   print ser.read()
   out = childid.expect(['1460K','hello'])
   #time.sleep(3)
   if (out == 0):
    print "hex data send initiated"
   else:
    print "failed to initiate hex data send"

   print "send data"
   if (serial_line == 'CDC_ACM'):
    time.sleep(5)
   ser.write('313233\r')
   time.sleep(5)
   if (serial_line == 'CDC_ACM'):
    time.sleep(60)
   out1 = childid.expect(['hello','K'])
   time.sleep(3)
   if (out1 == 1):
    print "data sent"
   else:
    print "failed to send data"

   print "push data from mux and verify remote host receives data"
   ser.write('1p\r')
   time.sleep(5)
   if (conn_type == 'connect'):
    recdata = conn.recv(100)
    time.sleep(3)
    print recdata
   elif (conn_type == 'accept'):
    recdata = sock.recv(100)
    time.sleep(3)
    print recdata
   if (recdata == '123'):
    print "data received", recdata
   else:
    print "failed to receive data"
   if (out == 0) and (out1 == 1) and (recdata == '123'):
    print "test case: hex data send passed"
    hexsend_result = 1
   else:
    print "test case: hex data send failed"
 
###############################################

   print "test case 3: read binary data"
   ser.write('1rb.80\r')
   time.sleep(3)
   out = childid.expect(['K'])
   time.sleep(3)
   if (out == 0):
    print "binary data read initiated"
   if (conn_type == 'connect'):
    conn.send('abcd')
   elif (conn_type == 'accept'):
    sock.send('abcd')
   time.sleep(2)
   serdata = ser.read(20)
   time.sleep(2)
   print "data read from serial is", serdata
   #if (conn_type == 'connect'):
    #conn.send('123')
    #time.sleep(2)
   #elif (conn_type == 'accept'):
    #sock.send('123')
    #time.sleep(2)
   #ser.write('1rb.80.\r')
   #time.sleep(5)
   #serdata1 = ser.read(20)
   #print 'data1 read from serial is', serdata1
   if (out == 0) and (serdata == 'abcd'):
    print "test case: binary data receive passed"
    readbinary_result = 1
   else:
    print "failed to receive binary data"

###############################################

   print "test case 4: send binary data and end the connection"
   ser.write('1sb.\r')
   time.sleep(3)
   out = childid.expect(['1460K','xyz'])
   time.sleep(1)
   if (out == 0):
    print "binary data send initiated"
   ser.write('12345678.\r')
   time.sleep(4)
   out1 = childid.expect(['K'])
   time.sleep(1)
   if (out1 == 0):
    print "data sent"
   print "push the data"
   ser.write('1e\r')
   time.sleep(2)
   if (conn_type == 'connect'):
    recdata = conn.recv(100)
    time.sleep(2)
   elif (conn_type == 'accept'):
     recdata = sock.recv(100)
     time.sleep(2)
   print "data received", recdata
   ser.write('1\r')
   time.sleep(2)
   out2 = childid.expect(['D','FG'])
   if (out2 == 0):
    print "connection ended"
   else:
    print "failed to end connection" 
   
   if (out == 0) and (out1 == 0) and (recdata == '12345678') and (out2 == 0):
     sendbinary_result = 1
     print "test case: send binary passed"
   else:
     print "failed to send binary data"

######################################################################
 
   #print "test case mux http"
   #try:
    # run this block of code with timeout.refer to class timeout() for details
     #with Timeout(60):
      #print "here"
      #mux_http()
   #except Timeout.Timeout:
      #print "Timeout"
   #ser = serial.Serial(serial_port)
   #childid = pexpect.fdpexpect.fdspawn(ser)
   #ser.write("\r")
   #time.sleep(5)
   #out = childid.expect(['user=s&email=pat'])
   #time.sleep(2)
   #ser.write("1k\r")
   #time.sleep(2)
   #if (out == 0) and (out1 == 0):
    #print "test case: mux http passed"
    #muxHttp_result = 1
   #else:
    #print "test case: mux http failed"
    #muxHttp_result = 0

   
###########################################################

 
  print "muxrec_result is ", muxrec_result
  print "hexsend_result is", hexsend_result
  print "sendbinary_result is", sendbinary_result
  print "readbinary_result is", readbinary_result
  #print "muxhttp_result is",muxHttp_result
 
  
  if (muxrec_result == 1) and (hexsend_result == 1) and (sendbinary_result == 1)and (readbinary_result == 1):
   result = 1
 
  ser.close()
  sock.close()
  return result
 except Exception as e:
  print(str(e))

def mux_udp():
 print "mux udp tests begin"
 if (serial_line == '1') or (serial_line == '2'):
  ser = serial.Serial(serial_port, '{0}'.format(baudrate), timeout=0, parity='{0}'.format(parity), stopbits = int('{0}'.format(stopbits)), bytesize = int('{0}'.format(databits)), rtscts = True)
 else:
  ser = serial.Serial(serial_port)
 childid = pexpect.fdpexpect.fdspawn(ser)
 ser.close()
 ser.open()
 sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
 udpport = 3001
 udp_port = int(udpport)
 sock.bind((remote_ip,udp_port))
 time.sleep(5)
 tunport = int(tunnel_port)
 result = 0
 muxrec_result = 0
 hexsend_result = 0
 sendbinary_result = 0
 readbinary_result = 0
 time.sleep(5)
 try:
  if ser.isOpen():
   ser.flushInput()
   ser.flushOutput()
   if (conn_type == 'accept') and (protocol == 'udp'):
    if (network == 'wlan0'):
     ser.write('1awlan0:10002udp\r')
    elif network == 'eth0':
     ser.write('1aeth0:10002udp\r')
    elif network == 'ap0':
     ser.write('1aap0:10002udp\r')
    time.sleep(10)
    mes = 'hello'
    sock.sendto(mes,(device_ip,tunport))
    time.sleep(10)
    out = childid.expect(['g','K'])
    print "out is", out
    ser.write('1sx\r')
    time.sleep(5)
    ser.write('31\r')
    time.sleep(5)
    ser.write('1p\r')
    time.sleep(5)
    serdata = ser.read(10)
    print serdata
    udprecv = sock.recv(100)
    print "udp recv is", udprecv
    if (serdata == '1496KKK') and (udprecv == '1'):
     print "vut received data"
     result = 1
    else:
     print "failed to receive data from vut"
   else:
     print "conn_type must be accept if protocol is udp"
     print "failed to run mux udp test"
     result = 0
   
  ser.close()
  sock.close()
  return result
 except Exception as e:
  print(str(e))
   
def device_config(port):

  print "configure device"
  pexpect.run("curl --digest -u admin:PASSWORD http://"+device_ip+"/fs/http -X MKCOL")
  pexpect.run("curl --digest -u admin:PASSWORD http://"+device_ip+"/fs/http/ -T form.html")
  time.sleep(5)
  clientid = pexpect.spawn('telnet '+device_ip)
  clientid.sendline('\r')
  clientid.sendline('\r')
  time.sleep(3)
  clientid.sendline('config\r')
  clientid.expect('config')
  clientid.sendline('http server\r')
  clientid.expect('config HTTP Server')
  clientid.sendline('security\r')
  clientid.expect('config HTTP Server Security')
  clientid.sendline('access control 1\r')
  clientid.sendline('uri /')
  time.sleep(8)
  clientid.sendline('authtype none')
  time.sleep(8)
  clientid.sendline('write\r')
  clientid.sendline('exit')
  clientid.sendline('exit')
  clientid.sendline('exit')
  clientid.sendline('exit')
  
  clientid.sendline('status\r')
  clientid.expect('status')
  clientid.sendline('device\r')
  clientid.expect('status Device')
  clientid.sendline('reboot')
  clientid.expect('okay/cancel')
  clientid.sendline('okay\r')
  print ("Rebooting")
  #clientid.expect('Rebooting')
  time.sleep(40)
  clientid = pexpect.spawn('telnet '+device_ip)
  clientid.sendline('\r')
  clientid.sendline('\r')
  print "configuring device"
  clientid.sendline('config\r')
  clientid.expect('config')
  print "line host_acm"
  clientid.sendline('line host_cdc_acm')
  time.sleep(3)
  #clientid.expect('config Line {0}'.format(serial_line))
  if (serial_line == '1') or (serial_line == '2'):
   clientid.sendline('baud rate {0}'.format(baudrate))
   #clientid.expect('config Line {0}'.format(serial_line))
   clientid.sendline('data bits {0}'.format(databits))
   #clientid.expect('config Line {0}'.format(serial_line))
   clientid.sendline('parity {0}'.format(parity))
   #clientid.expect('config Line {0}'.format(serial_line))
   clientid.sendline('stop bits {0}'.format(stopbits))
   #clientid.expect('config Line {0}'.format(serial_line))
   clientid.sendline('flow control hardware\r')
   #clientid.expect('config Line {0}'.format(serial_line))
  clientid.sendline('protocol mux\r')
  clientid.sendline('exit\r')
  clientid.expect('config')
  clientid.sendline('write\r')
  clientid.expect('config')
  clientid.sendline('write\r')
  clientid.expect('config')
  clientid.sendline('exit\r')
  clientid.expect('>')
  print "end of device configuration"
  print "testing mux"
  if (protocol == 'tcp'):
   result = mux_tcp()
   print "result is", result
  else:
   result = mux_udp()
  if result == 1:
   print "TEST CASE PASSED"
  else:
   print "test case mux failed"

# main program
device_config(tunnel_port)

sys.exit()

