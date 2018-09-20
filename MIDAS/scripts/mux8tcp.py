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
#import mechanize,re
import threading, time
import signal

print "Test MUX"
print "========="

#syntax

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <serial_port>" + " <baudrate>" + " <databits>" + " <parity>" + " <stopbits>" + " <device_ip>" + " <tunnel_port>" +  " <line>" + " <remote pc/vut>" + " <conn_type>" + " <protocol>" + "<restricted>" + " <interface>")
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
line = sys.argv[8]
remote_ip = sys.argv[9] #must be linux pc
conn_type = sys.argv[10]
protocol = sys.argv[11] # tcp or udp
restricted = sys.argv[12] # values 1 or 0
interface = sys.argv[13]

xml_path = '/home/lantronix/MIDAS/xml/'

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

def importxml():
  print "import xml to add tcpaes credential"
  xml = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"muxtcpaes.xml")
  xml_res = re.search('completed',xml)
  if xml_res:
    print "xml import completed."
  else:
    print "xml import failed"

def sock_mul():
   sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   sock2.bind((remote_ip,4002))
   sock2.listen(1)
   sock3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   sock3.bind((remote_ip,4003))
   sock3.listen(1)
   sock4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   sock4.bind((remote_ip,4004))
   sock4.listen(1)
   sock5 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   sock5.bind((remote_ip,4005))
   sock5.listen(1)
   sock6 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   sock6.bind((remote_ip,4006))
   sock6.listen(1)
   sock7 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   sock7.bind((remote_ip,4007))
   sock7.listen(1)
   sock8 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   sock8.bind((remote_ip,4008))
   sock8.listen(1)


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
  
  br = mechanize.Browser()
  br.set_handle_robots(False)   # ignore robots
  br.set_handle_refresh(False)
  req = br.open('http://172.19.100.68/form.html')
  print req
  br.select_form('f')
  br['user'] = 's'
  br['email'] = 'pat'
  ser.write("1rb.100\r")
  time.sleep(10)
  print "ser write command written"
   #req = br.click(type="submit")
  req = br.submit()
  print req
  time.sleep(10)
  print "submitted"
  ser.close()

def mux_tcp():
 if protocol == 'tcpaes':
   importxml()

 if (line == '1'):
  ser = serial.Serial(serial_port, '{0}'.format(baudrate), timeout=0, parity='{0}'.format(parity), stopbits = int('{0}'.format(stopbits)), bytesize = int('{0}'.format(databits)), rtscts = True)
 else:
  ser = serial.Serial(serial_port,xonxoff=True)
 childid = pexpect.fdpexpect.fdspawn(ser)
 ser.close()
 ser.open()
 sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 tunport1 = int(10001)
 tunport2 = int(10002)
 tunport3 = int(10003)
 tunport4 = int(10004)
 tunport5 = int(10005)
 tunport6 = int(10006)
 tunport7 = int(10007)
 tunport8 = int(10008)
 sock.settimeout(20)
 if (conn_type == 'connect'):
  if protocol == 'tcp':
   sock.bind((remote_ip,4001))
   sock.listen(1)
  elif protocol == 'tcpaes':
   sock.connect(('192.168.51.87',10001))
 
 #tunport = int(tunnel_port)
 result = 0
 muxrec_result = 0
 hexsend_result = 0
 sendbinary_result = 0
 readbinary_result = 0
 time.sleep(5)

 print "Test Mux instance 1"
 try:
  if ser.isOpen():
   print "serial opened"
   ser.flushInput()
   ser.flushOutput()
   time.sleep(4)
   print 'test case 1: mux receive'
   print "connect to remote host"
   if (conn_type == 'connect') and protocol == 'tcp': 
    ser.write('1c'+remote_ip+':4001tcp\r')
   elif conn_type == 'connect' and protocol == 'tcpaes':
    ser.write('1c'+remote_ip+':10001tcp aes,aes\r')
   time.sleep(5)
   if (conn_type == 'accept') and (restricted == '0'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('1aeth0:10001tcp\r')
     elif protocol == 'tcpaes':
      ser.write('1aeth0:10001tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('1awlan0:10001tcp\r')
     elif protocol == 'tcpaes':
      ser.write('1awlan0:10001tcp aes,aes\r')
    time.sleep(15)
    if protocol == 'tcp':
     sock.connect((device_ip, tunport1))
    elif protocol == 'tcpaes':
     sock.connect(('192.168.51.87',10001))
   elif (conn_type == 'accept') and (restricted == '1'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('1aeth0:10001tcp\r')
     elif protocol == 'tcpaes':
      ser.write('1aeth0:10001tcp aes,aes\r')
      time.sleep(15)
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('1awlan0:10001tcp\r')
     elif protocol == 'tcpaes':
      ser.write('1awlan0:10001tcp aes,aes\r')
    #print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
     sock.connect((device_ip, tunport1))
    elif protocol == 'tcpaes':
     sock.connect(('192.168.51.87',10001))
   print "verify connection"
   ser.write("1\r")
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
    if protocol == 'tcp': 
     conn,addr = sock.accept()
     print 'connected by',addr
    print "sending"
    print "waiting for receiving event/data"
    ser.write('W1r\r')
    time.sleep(5)
    print "send data"
    if protocol == 'tcp':
     conn.send('abcde')
    elif protocol == 'tcpaes':
     sock.send('abcde')
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
    if (line == 'CDC_ACM'):
     time.sleep(60)
    else:
     time.sleep(5)
    if line == '1':
     serdata = ser.read(10)
    elif line == '2':
     bytesToRead = ser.inWaiting()
     serdata = ser.read(bytesToRead)
    print "serdata",serdata 
    time.sleep(5)
    print "reading data from serial"
    if (line == 'CDC_ACM'):
     time.sleep(60)
    else:
     time.sleep(10)
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
   out = childid.expect(['K','hello'])
   #time.sleep(3)
   if (out == 0):
    print "hex data send initiated"
   else:
    print "failed to initiate hex data send"

   print "send data"
   if (line == 'CDC_ACM'):
    time.sleep(5)
   ser.write('313233\r')
   time.sleep(5)
   if (line == 'CDC_ACM'):
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
    if protocol == 'tcp':
     recdata = conn.recv(100)
    elif protocol == 'tcpaes':
     recdata = sock.recv(100)
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
    if protocol == 'tcp':
     conn.send('abcd')
    elif protocol == 'tcpaes':
     sock.send('abcd')
   elif (conn_type == 'accept'):
    sock.send('abcd')
   print "binary data sent"
   time.sleep(2)
   if line == '1':
    serdata = ser.read(20)
   elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
   time.sleep(2)
   print "data read from serial is", serdata
   serdata = re.search('abcd',serdata)
   if (out == 0) and serdata:
    print "test case: binary data receive passed"
    readbinary_result = 1
   else:
    print "failed to receive binary data"
    readbinary_result = 0
###############################################

   print "test case 4: send binary data and end the connection"
   ser.write('1sb.\r')
   time.sleep(3)
   out = childid.expect(['K','xyz'])
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
   ser.write('1p\r')
   time.sleep(4)
   if (conn_type == 'connect'):
    if protocol == 'tcp':
     recdata = conn.recv(100)
    elif protocol == 'tcpaes':
     recdata = sock.recv(100)
    time.sleep(2)
   elif (conn_type == 'accept'):
     recdata = sock.recv(100)
     time.sleep(2)
   print "data received", recdata
   
   if (out == 0) and (out1 == 0) and (recdata == '12345678'):
     sendbinary_result = 1
     print "test case: send binary passed"
   else:
     print "failed to send binary data"

######################################################################
 
   print "test case mux http"

   
###########################################################

 
  print "muxrec_result is ", muxrec_result
  print "hexsend_result is", hexsend_result
  print "sendbinary_result is", sendbinary_result
  print "readbinary_result is", readbinary_result
  #print "muxhttp_result is",muxHttp_result
 
  
  if (muxrec_result == 1) and (hexsend_result == 1) and (sendbinary_result == 1)and (readbinary_result == 1):
   print "TCP MUX instance 1 test case passed"
   result = 1
  else:
   print "TCP MUX instance 1 test case failed"
   result = 0

  print "Test instance 2"
  sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  if conn_type == 'connect':
   if protocol == 'tcp':
    print "start listener"
    sock2.bind((remote_ip,4002))
    sock2.listen(1)
   elif protocol == 'tcpaes':
    sock2.connect(('192.168.51.87',10002))

  print 'test case 1: mux receive'
  print "connect to remote host"
  if (conn_type == 'connect'): 
   if protocol == 'tcp':
    ser.write('2c'+remote_ip+':4002tcp\r')
   elif protocol == 'tcpaes':
    ser.write('2c'+remote_ip+':10002tcp aes,aes\r')
   time.sleep(5)
  elif (conn_type == 'accept') and (restricted == '0'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('2aeth0:10002tcp\r')
     elif protocol == 'tcpaes':
      print "instance 2 tcpaes"
      ser.write('2aeth0:10002tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('2awlan0:10002tcp\r')
     elif protocol == 'tcpaes':
      ser.write('2awlan0:10002tcp aes,aes\r')
    print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
     sock2.connect((device_ip, tunport2))
    elif protocol == 'tcpaes':
     sock2.connect(('192.168.51.87',10002))
  elif (conn_type == 'accept') and (restricted == '1'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('2aeth0:10002tcp\r')
     elif protocol == 'tcpaes':
      print "instance 2 tcpaes"
      ser.write('2aeth0:10002tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('2awlan0:10002tcp\r')
     elif protocol == 'tcpaes':
      ser.write('2awlan0:10002tcp aes,aes\r')
    print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
     sock2.connect((device_ip, tunport2))
    elif protocol == 'tcpaes':
     print "connect to 10002"
     sock2.connect(('192.168.51.87',10002))
     time.sleep(3)
  print "verify connection"
  ser.write("2\r")
   #time.sleep(2)
  out = childid.expect(['123','K'])
   #time.sleep(2)
  if (out == 1):
    print "connection established. received K"
  else:
    print "failed to establish the connection"
  if (conn_type == 'accept') and (restricted == '1') or restricted == '0':
     if (out == 1):
      print "test case: tcp mux receive passed"
      muxrec_result = 1
     else:
      print "test case: tcp mux receive failed"
  
  if (conn_type == 'connect'):
    if protocol == 'tcp': 
     conn2,addr = sock2.accept()
     print 'connected by',addr
    print "sending"
    print "waiting for receiving event/data"
    ser.write('W2r\r')
    time.sleep(5)
    print "send data"
    if protocol == 'tcp':
     conn2.send('abcde')
   #ser.write('W1r\r')
    elif protocol == 'tcpaes':
     sock2.send('abcde')
    time.sleep(5)

    print "check whether is data waiting"
    out1 = childid.expect(['3','2r'])
    if (out1 == 1):
     print "data is waiting. received 2r"
    else:
     print "there is no data"

    print "read and check data"
    ser.write('2rb.80\r')
    time.sleep(5)
    if (line == 'CDC_ACM'):
     time.sleep(60)
    else:
     time.sleep(5)
    if line == '1':
     serdata = ser.read(10)
    elif line == '2':
     bytesToRead = ser.inWaiting()
     serdata = ser.read(bytesToRead)
    print "serdata",serdata 
    time.sleep(5)
    print "reading data from serial"
    if (line == 'CDC_ACM'):
     time.sleep(60)
    else:
     time.sleep(10)
    if (serdata == "Kabcde"):
     print "data read from serial"
    else:
     print "failed to read data from serial"

    if (out == 1) and (out1 == 1) and (serdata == 'Kabcde'):
     print "tcp mux receive instance 2 passed"
     muxrec_result = 1
    else:
     print "tcp mux receive instance 2 failed"
   
############################################

 
  print "test case 2: send and push Hex data"
  print "initiate hex data send"
  ser.write('2sx\r')
   #print "check"
  time.sleep(5)
  print ser.read()
  out = childid.expect(['K','hello'])
   #time.sleep(3)
  if (out == 0):
    print "hex data send initiated"
  else:
    print "failed to initiate hex data send"

  print "send data"
  if (line == 'CDC_ACM'):
    time.sleep(5)
  ser.write('313233\r')
  time.sleep(5)
  if (line == 'CDC_ACM'):
    time.sleep(60)
  out1 = childid.expect(['hello','K'])
  time.sleep(3)
  if (out1 == 1):
   print "data sent"
  else:
   print "failed to send data"

  print "push data from mux and verify remote host receives data"
  ser.write('2p\r')
  time.sleep(5)
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    recdata = conn2.recv(100)
   elif protocol == 'tcpaes':
    recdata = sock2.recv(100)
   time.sleep(3)
   print recdata
  elif (conn_type == 'accept'):
    recdata = sock2.recv(100)
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
  ser.write('2rb.80\r')
  time.sleep(3)
  out = childid.expect(['K'])
  time.sleep(3)
  if (out == 0):
    print "binary data read initiated"
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    conn2.send('abcd')
   elif protocol == 'tcpaes':
    sock2.send('abcd')
  elif (conn_type == 'accept'):
    sock2.send('abcd')
  print "binary data sent"
  time.sleep(2)
  if line == '1':
    serdata = ser.read(20)
  elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
  time.sleep(2)
  print "data read from serial is", serdata
  serdata = re.search('abcd',serdata)
  if (out == 0) and serdata:
    print "test case: binary data receive passed"
    readbinary_result = 1
  else:
    print "failed to receive binary data"
    readbinary_result = 0

###############################################

  print "test case 4: send binary data and end the connection"
  ser.write('2sb.\r')
  time.sleep(3)
  out = childid.expect(['K','xyz'])
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
  ser.write('2p\r')
  time.sleep(5)
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    recdata = conn2.recv(100)
   elif protocol == 'tcpaes':
    recdata = sock2.recv(100)
   time.sleep(2)
  elif (conn_type == 'accept'):
     recdata = sock2.recv(100)
     time.sleep(2)
  print "data received", recdata

   
  if (out == 0) and (out1 == 0) and (recdata == '12345678'):
     sendbinary_result = 1
     print "test case: send binary passed"
  else:
     print "failed to send binary data"

######################################################################
 
  print "test case mux http"

   
###########################################################

 
  print "muxrec_result is ", muxrec_result
  print "hexsend_result is", hexsend_result
  print "sendbinary_result is", sendbinary_result
  print "readbinary_result is", readbinary_result
  #print "muxhttp_result is",muxHttp_result
 
  
  if (muxrec_result == 1) and (hexsend_result == 1) and (sendbinary_result == 1)and (readbinary_result == 1):
   result = 1
   print "mux tcp test instance 2 passed"
  else:
   print "mux receive instance 2 failed"
   result = 0 

  print "Test instance 3"
  sock3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  if conn_type == 'connect':
   if protocol == 'tcp':
    print "start listener"
    sock3.bind((remote_ip,4003))
    sock3.listen(1)
   elif protocol == 'tcpaes':
    sock3.connect(('192.168.51.87',10003))

  print 'test case 1: mux receive'
  print "connect to remote host"
  if (conn_type == 'connect'): 
   if protocol == 'tcp':
    ser.write('3c'+remote_ip+':4003tcp\r')
   elif protocol == 'tcpaes':
    ser.write('3c'+remote_ip+':10003tcp aes,aes\r')
   time.sleep(5)
  elif (conn_type == 'accept') and (restricted == '0'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('3aeth0:10003tcp\r')
     elif protocol == 'tcpaes':
      print "instance 3 tcpaes"
      ser.write('3aeth0:10003tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('3awlan0:10003tcp\r')
     elif protocol == 'tcpaes':
      ser.write('3awlan0:10003tcp aes,aes\r')
    print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
     sock3.connect((device_ip, tunport3))
    elif protocol == 'tcpaes':
     sock2.connect(('192.168.51.87',10003))
  elif (conn_type == 'accept') and (restricted == '1'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('3aeth0:10003tcp\r')
     elif protocol == 'tcpaes':
      print "instance 3 tcpaes"
      ser.write('3aeth0:10003tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('3awlan0:10003tcp\r')
     elif protocol == 'tcpaes':
      ser.write('3awlan0:10003tcp aes,aes\r')
    print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
     sock3.connect((device_ip, tunport3))
    elif protocol == 'tcpaes':
     print "connect to 10003"
     sock3.connect(('192.168.51.87',10003))
     time.sleep(3)
  print "verify connection"
  ser.write("3\r")
   #time.sleep(2)
  out = childid.expect(['123','K'])
   #time.sleep(2)
  if (out == 1):
    print "connection established. received K"
  else:
    print "failed to establish the connection"
  if (conn_type == 'accept') and (restricted == '1') or restricted == '0':
     if (out == 1):
      print "test case: tcp mux receive passed"
      muxrec_result = 1
     else:
      print "test case: tcp mux receive failed"
  
  if (conn_type == 'connect'): 
    if protocol == 'tcp':
     conn3,addr = sock3.accept()
     print 'connected by',addr
    print "sending"
    print "waiting for receiving event/data"
    ser.write('W3r\r')
    time.sleep(5)
    print "send data"
    if protocol == 'tcp':
     conn3.send('abcde')
    elif protocol == 'tcpaes':
     sock3.send('abcde')
    time.sleep(5)

    print "check whether is data waiting"
    out1 = childid.expect(['4','3r'])
    if (out1 == 1):
     print "data is waiting. received 3r"
    else:
     print "there is no data"

    print "read and check data"
    ser.write('3rb.80\r')
    time.sleep(5)
    if (line == 'CDC_ACM'):
     time.sleep(60)
    else:
     time.sleep(5)
    if line == '1':
     serdata = ser.read(10)
    elif line == '2':
     bytesToRead = ser.inWaiting()
     serdata = ser.read(bytesToRead)
    print "serdata",serdata 
    time.sleep(5)
    print "reading data from serial"
    if (line == 'CDC_ACM'):
     time.sleep(60)
    else:
     time.sleep(10)
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
  ser.write('3sx\r')
   #print "check"
  time.sleep(3)
  print ser.read()
  out = childid.expect(['K','hello'])
   #time.sleep(3)
  if (out == 0):
    print "hex data send initiated"
  else:
    print "failed to initiate hex data send"

  print "send data"
  if (line == 'CDC_ACM'):
    time.sleep(5)
  ser.write('313233\r')
  time.sleep(5)
  if (line == 'CDC_ACM'):
    time.sleep(60)
  out1 = childid.expect(['hello','K'])
  time.sleep(3)
  if (out1 == 1):
   print "data sent"
  else:
   print "failed to send data"

  print "push data from mux and verify remote host receives data"
  ser.write('3p\r')
  time.sleep(5)
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    recdata = conn3.recv(100)
   elif protocol == 'tcpaes':
    recdata = sock3.recv(100)
   time.sleep(3)
   print recdata
  elif (conn_type == 'accept'):
    recdata = sock3.recv(100)
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
  ser.write('3rb.80\r')
  time.sleep(3)
  out = childid.expect(['K'])
  time.sleep(3)
  if (out == 0):
    print "binary data read initiated"
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    conn3.send('abcd')
   elif protocol == 'tcpaes':
    sock3.send('abcd')
  elif (conn_type == 'accept'):
    sock3.send('abcd')
  print "binary data sent"
  time.sleep(2)
  if line == '1':
    serdata = ser.read(20)
  elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
  time.sleep(2)
  print "data read from serial is", serdata
  serdata = re.search('abcd',serdata)
  if (out == 0) and serdata:
    print "test case: binary data receive passed"
    readbinary_result = 1
  else:
    print "failed to receive binary data"
    readbinary_result = 0
###############################################

  print "test case 4: send binary data and end the connection"
  ser.write('3sb.\r')
  time.sleep(3)
  out = childid.expect(['K','xyz'])
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
  ser.write('3p\r')
  time.sleep(4)
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    recdata = conn3.recv(100)
   elif protocol == 'tcpaes':
    recdata = sock3.recv(100)
   time.sleep(2)
  elif (conn_type == 'accept'):
     recdata = sock3.recv(100)
     time.sleep(2)
  print "data received", recdata

  if (out == 0) and (out1 == 0) and (recdata == '12345678'):
     sendbinary_result = 1
     print "test case: send binary passed"
  else:
     print "failed to send binary data"

######################################################################
 
  print "test case mux http"

   
###########################################################

 
  print "muxrec_result is ", muxrec_result
  print "hexsend_result is", hexsend_result
  print "sendbinary_result is", sendbinary_result
  print "readbinary_result is", readbinary_result
  #print "muxhttp_result is",muxHttp_result
 
  
  if (muxrec_result == 1) and (hexsend_result == 1) and (sendbinary_result == 1)and (readbinary_result == 1):
   result = 1
   print "mux receive test case instance 3 passed"
  else:
   print "mux receive test case instance 3 failed"
   result = 0
  

  print "Test instance 4"
  sock4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  if conn_type == 'connect':
   if protocol == 'tcp':
    print "start listener"
    sock4.bind((remote_ip,4004))
    sock4.listen(1)
   elif protocol == 'tcpaes':
    sock4.connect(('192.168.51.87',10004))
  
  print 'test case 1: mux receive'
  print "connect to remote host"
  if (conn_type == 'connect'):
   if protocol == 'tcp': 
    ser.write('4c'+remote_ip+':4004tcp\r')
   elif protocol == 'tcpaes':
    ser.write('4c'+remote_ip+':10004tcp aes,aes\r')
   time.sleep(5)
  elif (conn_type == 'accept') and (restricted == '0'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('4aeth0:10004tcp\r')
     elif protocol == 'tcpaes':
      ser.write('4aeth0:10004tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('4awlan0:10004tcp\r')
     elif protocol == 'tcpaes':
      ser.write('4awlan0:10004tcp aes,aes\r')
    print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
     sock4.connect((device_ip, tunport4))
    elif protocol == 'tcpaes':
     sock4.connect(('192.168.51.87',10004))
  elif (conn_type == 'accept') and (restricted == '1'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('4aeth0:10004tcp\r')
     elif protocol == 'tcpaes':
      ser.write('4aeth0:10004tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('4awlan0:10004tcp\r')
     elif protocol == 'tcpaes':
      ser.write('4awlan0:10004tcp aes,aes\r')
    print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
      sock4.connect((device_ip, tunport4))
    elif protocol == 'tcpaes':
      sock4.connect(('192.168.51.87',10004))
  print "verify connection"
  ser.write("4\r")
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
    if protocol == 'tcp':
     conn4,addr = sock4.accept()
     print 'connected by',addr
    print "sending"
    print "waiting for receiving event/data"
    ser.write('W4r\r')
    time.sleep(5)
    print "send data"
    if protocol == 'tcp':
     conn4.send('abcde')
    elif protocol == 'tcpaes':
     sock4.send('abcde')
    time.sleep(5)

    print "check whether is data waiting"
    out1 = childid.expect(['5','4r'])
    if (out1 == 1):
     print "data is waiting. received 4r"
    else:
     print "there is no data"

    print "read and check data"
    ser.write('4rb.80\r')
    time.sleep(5)
    if (line == 'CDC_ACM'):
     time.sleep(60)
    else:
     time.sleep(5)
    if line == '1':
     serdata = ser.read(10)
    elif line == '2':
     bytesToRead = ser.inWaiting()
     serdata = ser.read(bytesToRead)
    print "serdata",serdata 
    time.sleep(5)
    print "reading data from serial"
    if (line == 'CDC_ACM'):
     time.sleep(60)
    else:
     time.sleep(10)
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
  ser.write('4sx\r')
   #print "check"
  time.sleep(3)
  print ser.read()
  out = childid.expect(['K','hello'])
   #time.sleep(3)
  if (out == 0):
    print "hex data send initiated"
  else:
    print "failed to initiate hex data send"

  print "send data"
  if (line == 'CDC_ACM'):
    time.sleep(5)
  ser.write('313233\r')
  time.sleep(5)
  if (line == 'CDC_ACM'):
    time.sleep(60)
  out1 = childid.expect(['hello','K'])
  time.sleep(3)
  if (out1 == 1):
   print "data sent"
  else:
   print "failed to send data"

  print "push data from mux and verify remote host receives data"
  ser.write('4p\r')
  time.sleep(5)
  if (conn_type == 'connect'):
   if protocol == 'tcp':
     recdata = conn4.recv(100)
   elif protocol == 'tcpaes':
     recdata = sock4.recv(100)
   time.sleep(3)
   print recdata
  elif (conn_type == 'accept'):
    recdata = sock4.recv(100)
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
  ser.write('4rb.80\r')
  time.sleep(3)
  out = childid.expect(['K'])
  time.sleep(3)
  if (out == 0):
    print "binary data read initiated"
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    conn4.send('abcd')
   elif protocol == 'tcpaes':
    sock4.send('abcd')
  elif (conn_type == 'accept'):
    sock4.send('abcd')
  print "binary data sent"
  time.sleep(2)
  if line == '1':
    serdata = ser.read(20)
  elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
  time.sleep(2)
  print "data read from serial is", serdata
  serdata = re.search('abcd',serdata)
  if (out == 0) and serdata:
    print "test case: binary data receive passed"
    readbinary_result = 1
  else:
    print "failed to receive binary data"

###############################################

  print "test case 4: send binary data and end the connection"
  ser.write('4sb.\r')
  time.sleep(3)
  out = childid.expect(['K','xyz'])
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
  ser.write('4p\r')
  time.sleep(4)
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    recdata = conn4.recv(100)
   elif protocol == 'tcpaes':
    recdata = sock4.recv(100)
   time.sleep(2)
  elif (conn_type == 'accept'):
     recdata = sock4.recv(100)
     time.sleep(2)
  print "data received", recdata

  if (out == 0) and (out1 == 0) and (recdata == '12345678'):
     sendbinary_result = 1
     print "test case: send binary passed"
  else:
     print "failed to send binary data"

######################################################################
 
  print "test case mux http"

   
###########################################################

 
  print "muxrec_result is ", muxrec_result
  print "hexsend_result is", hexsend_result
  print "sendbinary_result is", sendbinary_result
  print "readbinary_result is", readbinary_result
  #print "muxhttp_result is",muxHttp_result
 
  
  if (muxrec_result == 1) and (hexsend_result == 1) and (sendbinary_result == 1)and (readbinary_result == 1):
   result = 1
   print "mux receive test case instance 4 passed"
   result = 1
  else:
   print "mux receive test case instance 4 failed"
   result = 0

  print "Test instance 5"
  sock5 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  if conn_type == 'connect':
   if protocol == 'tcp':
    print "start listener"
    sock5.bind((remote_ip,4005))
    sock5.listen(1)
   elif protocol == 'tcpaes':
    sock5.connect(('192.168.51.87',10005))
  
  print 'test case 1: mux receive'
  print "connect to remote host"
  if (conn_type == 'connect'): 
   if protocol == 'tcp':
    ser.write('5c'+remote_ip+':4005tcp\r')
   elif protocol == 'tcpaes':
    ser.write('5c'+remote_ip+':10005tcp aes,aes\r')  
   time.sleep(8)
  elif (conn_type == 'accept') and (restricted == '0'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('5awlan0:10005tcp\r')
     elif protocol == 'tcpaes':
      ser.write('5aeth0:10005tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('5awlan0:10005tcp\r')
     elif protocol == 'tcpaes':
      ser.write('5awlan0:10005tcp aes,aes\r')
    print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
     sock5.connect((device_ip, tunport5))
    elif protocol == 'tcpaes':
     sock5.connect(('192.168.51.87',10005))
  elif (conn_type == 'accept') and (restricted == '1'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('5aeth0:10005tcp\r')
     elif protocol == 'tcpaes':
      ser.write('5aeth0:10005tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('5awlan0:10005tcp\r')
     elif protocol == 'tcpaes':
      ser.write('5awlan0:10005tcp aes,aes\r')
    print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
     sock5.connect((device_ip, tunport5))
    elif protocol == 'tcpaes':
     sock5.connect(('192.168.51.87',10005))
  print "verify connection"
  ser.write("5\r")
   #time.sleep(2)
  out = childid.expect('K')
   #time.sleep(2)
  if (out == 0):
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
    if protocol == 'tcp':
     conn5,addr = sock5.accept()
     print 'connected by',addr
    print "sending"
    print "waiting for receiving event/data"
    ser.write('W5r\r')
    time.sleep(5)
    print "send data"
    if protocol == 'tcp':
     conn5.send('abcde')
    elif protocol == 'tcpaes':
     sock5.send('abcde')
    time.sleep(5)

    print "check whether is data waiting"
    out1 = childid.expect('5r')
    if (out1 == 0):
     print "data is waiting. received 5r"
    else:
     print "there is no data"

    print "read and check data"
    ser.write('5rb.80\r')
    time.sleep(5)
    if (line == 'CDC_ACM'):
     time.sleep(60)
    else:
     time.sleep(5)
    if line == '1':
     serdata = ser.read(10)
    elif line == '2':
     bytesToRead = ser.inWaiting()
     serdata = ser.read(bytesToRead)
    print "serdata",serdata 
    time.sleep(5)
    print "reading data from serial"
    if (line == 'CDC_ACM'):
     time.sleep(60)
    else:
     time.sleep(10)
    if (serdata == "Kabcde"):
     print "data read from serial"
    else:
     print "failed to read data from serial"

    if (out == 0) and (out1 == 0) and (serdata == 'Kabcde'):
     print "test case: tcp mux receive passed"
     muxrec_result = 1
    else:
     print "test case: tcp mux receive failed"
   
############################################

 
  print "test case 2: send and push Hex data"
  print "initiate hex data send"
  ser.write('5sx\r')
   #print "check"
  time.sleep(3)
  print ser.read()
  out = childid.expect(['K','hello'])
   #time.sleep(3)
  if (out == 0):
    print "hex data send initiated"
  else:
    print "failed to initiate hex data send"

  print "send data"
  if (line == 'CDC_ACM'):
    time.sleep(5)
  ser.write('313233\r')
  time.sleep(5)
  if (line == 'CDC_ACM'):
    time.sleep(60)
  out1 = childid.expect(['hello','K'])
  time.sleep(3)
  if (out1 == 1):
   print "data sent"
  else:
   print "failed to send data"

  print "push data from mux and verify remote host receives data"
  ser.write('5p\r')
  time.sleep(5)
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    recdata = conn5.recv(100)
   elif protocol == 'tcpaes':
    recdata = sock5.recv(100)
   time.sleep(3)
   print recdata
  elif (conn_type == 'accept'):
    recdata = sock5.recv(100)
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
  ser.write('5rb.80\r')
  time.sleep(3)
  out = childid.expect(['K'])
  time.sleep(3)
  if (out == 0):
    print "binary data read initiated"
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    conn5.send('abcd')
   elif protocol == 'tcpaes':
    sock5.send('abcd')
  elif (conn_type == 'accept'):
    sock5.send('abcd')
  print "binary data sent"
  time.sleep(2)
  if line == '1':
    serdata = ser.read(20)
  elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
  time.sleep(2)
  print "data read from serial is", serdata
  serdata = re.search('abcd',serdata)
  if (out == 0) and serdata:
    print "test case: binary data receive passed"
    readbinary_result = 1
  else:
    print "failed to receive binary data"
    readbinary_result = 0
###############################################

  print "test case 4: send binary data and end the connection"
  ser.write('5sb.\r')
  time.sleep(3)
  out = childid.expect(['K','xyz'])
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
  ser.write('5p\r')
  time.sleep(4)
  if (conn_type == 'connect'):
   if protocol == 'tcp':
     recdata = conn5.recv(100)
   elif protocol == 'tcpaes':
     recdata = sock5.recv(100)
   time.sleep(2)
  elif (conn_type == 'accept'):
     recdata = sock5.recv(100)
     time.sleep(2)
  print "data received", recdata

  if (out == 0) and (out1 == 0) and (recdata == '12345678'):
     sendbinary_result = 1
     print "test case: send binary passed"
  else:
     print "failed to send binary data"

######################################################################
 
  print "test case mux http"

   
###########################################################

 
  print "muxrec_result is ", muxrec_result
  print "hexsend_result is", hexsend_result
  print "sendbinary_result is", sendbinary_result
  print "readbinary_result is", readbinary_result
  #print "muxhttp_result is",muxHttp_result
 
  
  if (muxrec_result == 1) and (hexsend_result == 1) and (sendbinary_result == 1)and (readbinary_result == 1):
   result = 1
   print "mux receive test case instance 5 passed"
  else:
   print "mux receive test case instance 5 failed"
   result = 0
  

  print "Test instance 6"
  sock6 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  if conn_type == 'connect':
   if protocol == 'tcp':
    print "start listener"
    sock6.bind((remote_ip,4006))
    sock6.listen(1)
   elif protocol == 'tcpaes':
    sock6.connect(('192.168.51.87',10006))
  
  print 'test case 1: mux receive'
  print "connect to remote host"
  if (conn_type == 'connect'):
   if protocol == 'tcp': 
    ser.write('6c'+remote_ip+':4006tcp\r')
   elif protocol == 'tcpaes':
    ser.write('6c'+remote_ip+':10006tcp aes,aes\r')
   time.sleep(8)
  elif (conn_type == 'accept') and (restricted == '0'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('6aeth0:10006tcp\r')
     elif protocol == 'tcpaes':
      ser.write('6aeth0:10006tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('6awlan0:10006tcp\r')
     elif protocol == 'tcpaes':
      ser.write('6awlan0:10006tcp aes,aes\r')
    print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
     sock6.connect((device_ip, tunport6))
    elif protocol == 'tcpaes':
     sock6.connect(('192.168.51.87',10006))
  elif (conn_type == 'accept') and (restricted == '1'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('6aeth0:10006tcp\r')
     elif protocol == 'tcpaes':
      ser.write('6aeth0:10006tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('6awlan0:10006tcp\r')
     elif protocol == 'tcpaes':
      ser.write('6awlan0:10006tcp aes,aes\r')
    print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
     sock6.connect((device_ip, tunport6))
    elif protocol == 'tcpaes':
     sock6.connect(('192.168.51.87',10006))
  print "verify connection"
  ser.write("6\r")
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
    if protocol == 'tcp':
     conn6,addr = sock6.accept()
     print 'connected by',addr
    print "sending"
    print "waiting for receiving event/data"
    ser.write('W6r\r')
    time.sleep(5)
    print "send data"
    if protocol == 'tcp':
     conn6.send('abcde')
    elif protocol == 'tcpaes':
     sock6.send('abcde')
    time.sleep(5)

    print "check whether is data waiting"
    out1 = childid.expect(['5','6r'])
    if (out1 == 1):
     print "data is waiting. received 6r"
    else:
     print "there is no data"

    print "read and check data"
    ser.write('6rb.80\r')
    time.sleep(5)
    if (line == 'CDC_ACM'):
     time.sleep(60)
    else:
     time.sleep(5)
    if line == '1':
     serdata = ser.read(10)
    elif line == '2':
     bytesToRead = ser.inWaiting()
     serdata = ser.read(bytesToRead)
    print "serdata",serdata 
    time.sleep(5)
    print "reading data from serial"
    if (line == 'CDC_ACM'):
     time.sleep(60)
    else:
     time.sleep(10)
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
  ser.write('6sx\r')
   #print "check"
  time.sleep(3)
  print ser.read()
  out = childid.expect(['K','hello'])
   #time.sleep(3)
  if (out == 0):
    print "hex data send initiated"
  else:
    print "failed to initiate hex data send"

  print "send data"
  if (line == 'CDC_ACM'):
    time.sleep(5)
  ser.write('313233\r')
  time.sleep(5)
  if (line == 'CDC_ACM'):
    time.sleep(60)
  out1 = childid.expect(['hello','K'])
  time.sleep(3)
  if (out1 == 1):
   print "data sent"
  else:
   print "failed to send data"

  print "push data from mux and verify remote host receives data"
  ser.write('6p\r')
  time.sleep(5)
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    recdata = conn6.recv(100)
   elif protocol == 'tcpaes':
    recdata = sock6.recv(100)
   time.sleep(3)
   print recdata
  elif (conn_type == 'accept'):
    recdata = sock6.recv(100)
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
  ser.write('6rb.80\r')
  time.sleep(3)
  out = childid.expect(['K'])
  time.sleep(3)
  if (out == 0):
    print "binary data read initiated"
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    conn6.send('abcd')
   elif protocol == 'tcpaes':
    sock6.send('abcd')
  elif (conn_type == 'accept'):
    sock6.send('abcd')
  print "binary data sent"
  time.sleep(2)
  if line == '1':
    serdata = ser.read(20)
  elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
  time.sleep(2)
  print "data read from serial is", serdata
  serdata = re.search('abcd',serdata)
  if (out == 0) and serdata:
    print "test case: binary data receive passed"
    readbinary_result = 1
  else:
    print "failed to receive binary data"
    readbinary_result = 0
###############################################

  print "test case 4: send binary data and end the connection"
  ser.write('6sb.\r')
  time.sleep(3)
  out = childid.expect(['K','xyz'])
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
  ser.write('6p\r')
  time.sleep(4)
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    recdata = conn6.recv(100)
   elif protocol == 'tcpaes':
    recdata = sock6.recv(100)
   time.sleep(2)
  elif (conn_type == 'accept'):
     recdata = sock6.recv(100)
     time.sleep(2)
  print "data received", recdata

  if (out == 0) and (out1 == 0) and (recdata == '12345678'):
     sendbinary_result = 1
     print "test case: send binary passed"
  else:
     print "failed to send binary data"

######################################################################
 
  print "test case mux http"

   
###########################################################

 
  print "muxrec_result is ", muxrec_result
  print "hexsend_result is", hexsend_result
  print "sendbinary_result is", sendbinary_result
  print "readbinary_result is", readbinary_result
  #print "muxhttp_result is",muxHttp_result
 
  
  if (muxrec_result == 1) and (hexsend_result == 1) and (sendbinary_result == 1)and (readbinary_result == 1):
   result = 1
   print "mux receive test case instance 6 passed"
  else:
   print "mux receive test case instance 6 failed"
   result = 0
##################################################################################
  
  print "Test instance 7"
  sock7 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  if conn_type == 'connect':
   if protocol == 'tcp':
    print "start listener"
    sock7.bind((remote_ip,4007))
    sock7.listen(1)
   elif protocol == 'tcpaes':
    sock7.connect(('192.168.51.87',10007))
  
  print 'test case 1: mux receive'
  print "connect to remote host"
  if (conn_type == 'connect'):
   if protocol == 'tcp': 
    ser.write('7c'+remote_ip+':4007tcp\r')
   elif protocol == 'tcpaes':
    ser.write('7c'+remote_ip+':10007tcp aes,aes\r')
    time.sleep(5)
    if (line == 'CDC_ACM'):
     time.sleep(60)
  elif (conn_type == 'accept') and (restricted == '0'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('7aeth0:10007tcp\r')
     elif protocol == 'tcpaes':
      ser.write('7aeth0:10007tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('7awlan0:10007tcp\r')
     elif protocol == 'tcpaes':
      ser.write('7awlan0:10007tcp aes,aes\r')
    print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
     sock7.connect((device_ip, tunport7))
    elif protocol == 'tcpaes': 
     sock7.connect(('192.168.51.87',10007))
  elif (conn_type == 'accept') and (restricted == '1'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('7aeth0:10007tcp\r')
     elif protocol == 'tcpaes':
      ser.write('7aeth0:10007tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('7awlan0:10007tcp\r')
     elif protocol == 'tcpaes':
      ser.write('7awlan0:10007tcp aes,aes\r')
    print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
     sock7.connect((device_ip, tunport7))
    elif protocol == 'tcpaes':
     sock7.connect(('192.168.51.87',10007))
  print "verify connection"
  ser.write("7\r")
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
    if protocol == 'tcp':
     conn7,addr = sock7.accept()
     print 'connected by',addr
    print "sending"
    print "waiting for receiving event/data"
    ser.write('W7r\r')
    time.sleep(5)
    print "send data"
    if protocol == 'tcp':
     conn7.send('abcde')
    elif protocol == 'tcpaes':
     sock7.send('abcde')
    time.sleep(5)

    print "check whether is data waiting"
    out1 = childid.expect(['5','7r'])
    if (out1 == 1):
     print "data is waiting. received 7r"
    else:
     print "there is no data"

    print "read and check data"
    ser.write('7rb.80\r')
    time.sleep(5)
    if (line == 'CDC_ACM'):
     time.sleep(60)
    else:
     time.sleep(5)
    if line == '1':
     serdata = ser.read(10)
    elif line == '2':
     bytesToRead = ser.inWaiting()
     serdata = ser.read(bytesToRead)
    print "serdata",serdata 
    time.sleep(5)
    print "reading data from serial"
    if (line == 'CDC_ACM'):
     time.sleep(60)
    else:
     time.sleep(10)
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
  ser.write('7sx\r')
   #print "check"
  time.sleep(3)
  print ser.read()
  out = childid.expect(['K','hello'])
   #time.sleep(3)
  if (out == 0):
    print "hex data send initiated"
  else:
    print "failed to initiate hex data send"

  print "send data"
  if (line == 'CDC_ACM'):
    time.sleep(5)
  ser.write('313233\r')
  time.sleep(5)
  if (line == 'CDC_ACM'):
    time.sleep(60)
  out1 = childid.expect(['hello','K'])
  time.sleep(3)
  if (out1 == 1):
   print "data sent"
  else:
   print "failed to send data"

  print "push data from mux and verify remote host receives data"
  ser.write('7p\r')
  time.sleep(5)
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    recdata = conn7.recv(100)
   elif protocol == 'tcpaes':
    recdata = sock7.recv(100)
   time.sleep(3)
   print recdata
  elif (conn_type == 'accept'):
    recdata = sock7.recv(100)
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
  ser.write('7rb.80\r')
  time.sleep(3)
  out = childid.expect(['K'])
  time.sleep(3)
  if (out == 0):
    print "binary data read initiated"
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    conn7.send('abcd')
   elif protocol == 'tcpaes':
    sock7.send('abcd')
  elif (conn_type == 'accept'):
    sock7.send('abcd')
  print "binary data sent"
  time.sleep(2)
  if line == '1':
    serdata = ser.read(20)
  elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
  time.sleep(2)
  print "data read from serial is", serdata
  serdata = re.search('abcd',serdata)
  if (out == 0) and serdata:
    print "test case: binary data receive passed"
    readbinary_result = 1
  else:
    print "failed to receive binary data"
    readbinary_result = 0
###############################################

  print "test case 4: send binary data and end the connection"
  ser.write('7sb.\r')
  time.sleep(3)
  out = childid.expect(['K','xyz'])
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
  ser.write('7p\r')
  time.sleep(4)
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    recdata = conn7.recv(100)
   elif protocol == 'tcpaes':
    recdata = sock7.recv(100)
   time.sleep(2)
  elif (conn_type == 'accept'):
     recdata = sock7.recv(100)
     time.sleep(2)
  print "data received", recdata

  if (out == 0) and (out1 == 0) and (recdata == '12345678'):
     sendbinary_result = 1
     print "test case: send binary passed"
  else:
     print "failed to send binary data"

######################################################################
 
  print "test case mux http"

   
###########################################################

 
  print "muxrec_result is ", muxrec_result
  print "hexsend_result is", hexsend_result
  print "sendbinary_result is", sendbinary_result
  print "readbinary_result is", readbinary_result
  #print "muxhttp_result is",muxHttp_result
 
  
  if (muxrec_result == 1) and (hexsend_result == 1) and (sendbinary_result == 1) and (readbinary_result == 1):
   result = 1
   print "mux receive test case instance 7 passed"
  else:
   print "mux receive test case instance 7 failed"
   result = 0
  
##################################################################################

  print "Test instance 8"
  sock8 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  if conn_type == 'connect':
   if protocol == 'tcp':
    print "start listener"
    sock8.bind((remote_ip,4008))
    sock8.listen(1)
   elif protocol == 'tcpaes':
    sock8.connect(('192.168.51.87',10008))
  
  print 'test case 1: mux receive'
  print "connect to remote host"
  if (conn_type == 'connect'): 
   if protocol == 'tcp':
    ser.write('8c'+remote_ip+':4008tcp\r')
   elif protocol == 'tcpaes':
    ser.write('8c'+remote_ip+':10008tcp aes,aes\r')
   time.sleep(5)
  elif (conn_type == 'accept') and (restricted == '0'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('8aeth0:10008tcp\r')
     elif protocol == 'tcpaes':
      ser.write('8aeth0:10008tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':     
      ser.write('8awlan0:10008tcp\r')
     elif protocol == 'tcpaes':
      ser.write('8awlan0:10008tcp aes,aes\r')
    print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
     sock8.connect((device_ip, tunport8))
    elif protocol == 'tcpaes':
     sock8.connect(('192.168.51.87',10008))      
  elif (conn_type == 'accept') and (restricted == '1'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('8aeth0:10008tcp\r')
     elif protocol == 'tcpaes':
      ser.write('8aeth0:10008tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol =='tcp':
      ser.write('8awlan0:10008tcp\r')
     elif protocol == 'tcpaes':
      ser.write('8awlan0:10008tcp aes,aes\r')
    print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
     sock8.connect((device_ip, tunport8))
    elif protocol == 'tcpaes': 
     sock8.connect(('192.168.51.87',10008))
  print "verify connection"
  ser.write("8\r")
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
    if protocol == 'tcp':
     conn8,addr = sock8.accept()
     print 'connected by',addr
    print "sending"
    print "waiting for receiving event/data"
    ser.write('W8r\r')
    time.sleep(5)
    print "send data"
    if protocol == 'tcp':
     conn8.send('abcde')
    elif protocol == 'tcpaes':
     sock8.send('abcde')
    time.sleep(5)

    print "check whether is data waiting"
    out1 = childid.expect(['5','8r'])
    if (out1 == 1):
     print "data is waiting. received 8r"
    else:
     print "there is no data"

    print "read and check data"
    ser.write('8rb.80\r')
    time.sleep(5)
    if (line == 'CDC_ACM'):
     time.sleep(60)
    else:
     time.sleep(5)
    if line == '1':
     serdata = ser.read(10)
    elif line == '2':
     bytesToRead = ser.inWaiting()
     serdata = ser.read(bytesToRead)
    print "serdata",serdata 
    time.sleep(5)
    print "reading data from serial"
    if (line == 'CDC_ACM'):
     time.sleep(60)
    else:
     time.sleep(10)
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
  ser.write('8sx\r')
   #print "check"
  time.sleep(3)
  print ser.read()
  out = childid.expect(['K','hello'])
   #time.sleep(3)
  if (out == 0):
    print "hex data send initiated"
  else:
    print "failed to initiate hex data send"

  print "send data"
  if (line == 'CDC_ACM'):
    time.sleep(5)
  ser.write('313233\r')
  time.sleep(5)
  if (line == 'CDC_ACM'):
    time.sleep(60)
  out1 = childid.expect(['hello','K'])
  time.sleep(3)
  if (out1 == 1):
   print "data sent"
  else:
   print "failed to send data"

  print "push data from mux and verify remote host receives data"
  ser.write('8p\r')
  time.sleep(5)
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    recdata = conn8.recv(100)
   elif protocol == 'tcpaes':
    recdata = sock8.recv(100)
   time.sleep(3)
   print recdata
  elif (conn_type == 'accept'):
    recdata = sock8.recv(100)
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
  ser.write('8rb.80\r')
  time.sleep(3)
  out = childid.expect(['K'])
  time.sleep(3)
  if (out == 0):
    print "binary data read initiated"
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    conn8.send('abcd')
   elif protocol == 'tcpaes':
    sock8.send('abcd')
  elif (conn_type == 'accept'):
    sock8.send('abcd')
  print "binary data sent"
  time.sleep(2)
  if line == '1':
    serdata = ser.read(20)
  elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
  time.sleep(2)
  print "data read from serial is", serdata
  serdata = re.search('abcd',serdata)
  if (out == 0) and serdata:
    print "test case: binary data receive passed"
    readbinary_result = 1
  else:
    print "failed to receive binary data"
    readbinary_result = 0
###############################################

  print "test case 4: send binary data and end the connection"
  ser.write('8sb.\r')
  time.sleep(3)
  out = childid.expect(['K','xyz'])
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
  ser.write('8p\r')
  time.sleep(4)
  if (conn_type == 'connect'): 
   if protocol == 'tcp': 
    recdata = conn8.recv(100)
   elif protocol == 'tcpaes':
    recdata = sock8.recv(100)
   time.sleep(2)
  elif (conn_type == 'accept'):
     recdata = sock8.recv(100)
     time.sleep(2)
  print "data received", recdata

  if (out == 0) and (out1 == 0) and (recdata == '12345678'):
     sendbinary_result = 1
     print "test case: send binary passed"
  else:
     print "failed to send binary data"

######################################################################
 
  print "test case mux http"

   
###########################################################

 
  print "muxrec_result is ", muxrec_result
  print "hexsend_result is", hexsend_result
  print "sendbinary_result is", sendbinary_result
  print "readbinary_result is", readbinary_result
  #print "muxhttp_result is",muxHttp_result
 
  
  if (muxrec_result == 1) and (hexsend_result == 1) and (sendbinary_result == 1)and (readbinary_result == 1):
   result = 1
   print "mux receive test case instance 8 passed"
  else:
   print "mux receive test case instance 8 failed"
   result = 0
  

  print "end connection"
  ser.write('1e\r')
  time.sleep(10)
  end1 = childid.expect(['K','FG'])
  print "end connection1"
  ser.write('2e\r')
  time.sleep(10)
  end2 = childid.expect(['K','FG'])
  print "end connection2"
  ser.write('3e\r')
  time.sleep(10)
  end3 = childid.expect(['K','F'])
  print "end connection3"
  ser.write('4e\r')
  time.sleep(10)
  end4 = childid.expect(['K','F'])
  print "end connection4"
  ser.write('5e\r')
  time.sleep(10)
  end5 = childid.expect(['K','F'])
  print "end connection5"
  ser.write('6e\r')
  time.sleep(10)
  end6 = childid.expect('K')
  print "end connection6"
  ser.write('7e\r')
  time.sleep(10)
  end7 = childid.expect('K')
  print "end connection7"
  ser.write('8e\r')
  time.sleep(10)
  end8 = childid.expect('K')
  print "end connection8"

  if end1 == 0 and end2 == 0 and end3 == 0 and end4 == 0 and end5 == 0 and end6 == 0 and end7 ==0 and end8 == 0:
   print "connection ended"
   result = 1
  else:
   print "connection did not end" 
   result = 0

  ser.close()
  sock.close()
  sock2.close()
  sock3.close()
  sock4.close()
  sock5.close()
  sock6.close()
  sock7.close()
  sock8.close()
  return result
 except Exception as e:
  print(str(e))

def mux_udp():
 print "Test MUX UDP"
 if (line == '1'):
  ser = serial.Serial(serial_port, '{0}'.format(baudrate), timeout=0, parity='{0}'.format(parity), stopbits = int('{0}'.format(stopbits)), bytesize = int('{0}'.format(databits)), rtscts = True)
 elif line == '2':
  ser = serial.Serial(serial_port,xonxoff=True)
 childid = pexpect.fdpexpect.fdspawn(ser)
 ser.close()
 ser.open()

 sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
 sock2 = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
 sock3 = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
 sock4 = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
 sock5 = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
 sock6 = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
 sock7 = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
 sock8 = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
 udpport = 3001
 udp_port = int(udpport)
 sock.bind((remote_ip,udp_port))
 time.sleep(5)
 tunport1 = int(10001)
 tunport2 = int(10002)
 tunport3 = int(10003)
 tunport4 = int(10004)
 tunport5 = int(10005)
 tunport6 = int(10006)
 tunport7 = int(10007)
 tunport8 = int(10008)
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
   print "Test mux instance 1"
   if (conn_type == 'accept') and (protocol == 'udp'):
    if (interface == 'eth0'):
     ser.write('1aeth0:10001udp\r')
    elif interface == 'wlan0':
     ser.write('1awlan0:10001udp\r')
    elif network == 'ap0':
     ser.write('1aap0:10001udp\r')
    time.sleep(3)
    mes = 'hello'
    sock.sendto(mes,(device_ip,tunport1))
    time.sleep(3)
    out = childid.expect(['g','K'])
    print "out is", out
    if out ==  1:
     print "mux udp is listening"
    ser.write('1sx\r')
    time.sleep(5)
    ser.write('3132\r')
    time.sleep(5)
    ser.write('1p\r')
    time.sleep(5)
    if line == '1':
     serdata = ser.read(10)
    elif line == '2':
     bytesToRead = ser.inWaiting()
     serdata = ser.read(bytesToRead)
    print "serial data is",serdata
    udprecv = sock.recv(100)
    print "udp recv is", udprecv
    if (serdata == '1460KKK') and (udprecv == '12'):
     print "vut received data"
     result = 1
    else:
     print "failed to receive data from vut"
   
    print "Test mux instance 2"
    if (interface == 'eth0'):
     ser.write('2aeth0:10002udp\r')
    elif interface == 'wlan0':
     ser.write('2awlan0:10002udp\r')
    elif network == 'ap0':
     ser.write('2aap0:10002udp\r')
    time.sleep(3)
    mes = 'hello'
    sock2.sendto(mes,(device_ip,tunport2))
    time.sleep(3)
    out = childid.expect(['g','K'])
    print "out is", out
    if out ==  1:
     print "mux udp is listening"
    ser.write('2sx\r')
    time.sleep(5)
    ser.write('3132\r')
    time.sleep(5)
    ser.write('2p\r')
    time.sleep(5)
    if line == '1':
     serdata = ser.read(10)
    elif line == '2':
     bytesToRead = ser.inWaiting()
     serdata = ser.read(bytesToRead)
    print "serial data is",serdata
    udprecv = sock2.recv(100)
    print "udp recv is", udprecv
    if (serdata == '1460KKK') and (udprecv == '12'):
     print "vut received data"
     result = 1
    else:
     print "failed to receive data from vut"

    print "Test mux instance 3"
    if (interface == 'eth0'):
     ser.write('3aeth0:10003udp\r')
    elif interface == 'wlan0':
     ser.write('3awlan0:10003udp\r')
    elif network == 'ap0':
     ser.write('3aap0:10003udp\r')
    time.sleep(3)
    mes = 'hello'
    sock3.sendto(mes,(device_ip,tunport3))
    time.sleep(3)
    out = childid.expect(['g','K'])
    print "out is", out
    if out ==  1:
     print "mux udp is listening"
    ser.write('3sx\r')
    time.sleep(5)
    ser.write('3132\r')
    time.sleep(5)
    ser.write('3p\r')
    time.sleep(5)
    if line == '1':
     serdata = ser.read(10)
    elif line == '2':
     bytesToRead = ser.inWaiting()
     serdata = ser.read(bytesToRead)
    print "serial data is",serdata
    udprecv = sock3.recv(100)
    print "udp recv is", udprecv
    if (serdata == '1460KKK') and (udprecv == '12'):
     print "vut received data"
     result = 1
    else:
     print "failed to receive data from vut"

   
    print "Test mux instance 4"
    if (interface == 'eth0'):
     ser.write('4aeth0:10004udp\r')
    elif interface == 'wlan0':
     ser.write('4awlan0:10004udp\r')
    elif network == 'ap0':
     ser.write('4aap0:10004udp\r')
    time.sleep(3)
    mes = 'hello'
    sock4.sendto(mes,(device_ip,tunport4))
    time.sleep(3)
    out = childid.expect(['g','K'])
    print "out is", out
    if out ==  1:
     print "mux udp is listening"
    ser.write('4sx\r')
    time.sleep(5)
    ser.write('3132\r')
    time.sleep(5)
    ser.write('4p\r')
    time.sleep(5)
    if line == '1':
     serdata = ser.read(10)
    elif line == '2':
     bytesToRead = ser.inWaiting()
     serdata = ser.read(bytesToRead)
    print "serial data is",serdata
    udprecv = sock4.recv(100)
    print "udp recv is", udprecv
    if (serdata == '1460KKK') and (udprecv == '12'):
     print "vut received data"
     result = 1
    else:
     print "failed to receive data from vut"


    print "Test mux instance 5"
    if (interface == 'eth0'):
     ser.write('5aeth0:10005udp\r')
    elif interface == 'wlan0':
     ser.write('5awlan0:10005udp\r')
    elif network == 'ap0':
     ser.write('5aap0:10005udp\r')
    time.sleep(3)
    mes = 'hello'
    sock5.sendto(mes,(device_ip,tunport5))
    time.sleep(3)
    out = childid.expect(['g','K'])
    print "out is", out
    if out ==  1:
     print "mux udp is listening"
    ser.write('5sx\r')
    time.sleep(5)
    ser.write('3132\r')
    time.sleep(5)
    ser.write('5p\r')
    time.sleep(5)
    if line == '1':
     serdata = ser.read(10)
    elif line == '2':
     bytesToRead = ser.inWaiting()
     serdata = ser.read(bytesToRead)
    print "serial data is",serdata
    udprecv = sock5.recv(100)
    print "udp recv is", udprecv
    if (serdata == '1460KKK') and (udprecv == '12'):
     print "vut received data"
     result = 1
    else:
     print "failed to receive data from vut"

    print "Test mux instance 6"
    if (interface == 'eth0'):
     ser.write('6aeth0:10006udp\r')
    elif interface == 'wlan0':
     ser.write('6awlan0:10006udp\r')
    elif network == 'ap0':
     ser.write('6aap0:10006udp\r')
    time.sleep(3)
    mes = 'hello'
    sock6.sendto(mes,(device_ip,tunport6))
    time.sleep(3)
    out = childid.expect(['g','K'])
    print "out is", out
    if out ==  1:
     print "mux udp is listening"
    ser.write('6sx\r')
    time.sleep(5)
    ser.write('3132\r')
    time.sleep(5)
    ser.write('6p\r')
    time.sleep(5)
    if line == '1':
     serdata = ser.read(10)
    elif line == '2':
     bytesToRead = ser.inWaiting()
     serdata = ser.read(bytesToRead)
    print "serial data is",serdata
    udprecv = sock6.recv(100)
    print "udp recv is", udprecv
    if (serdata == '1460KKK') and (udprecv == '12'):
     print "vut received data"
     result = 1
    else:
     print "failed to receive data from vut"

    print "Test mux instance 7"
    if (interface == 'eth0'):
     ser.write('7aeth0:10007udp\r')
    elif interface == 'wlan0':
     ser.write('7awlan0:10007udp\r')
    elif network == 'ap0':
     ser.write('7aap0:10007udp\r')
    time.sleep(3)
    mes = 'hello'
    sock7.sendto(mes,(device_ip,tunport7))
    time.sleep(3)
    out = childid.expect(['g','K'])
    print "out is", out
    if out ==  1:
     print "mux udp is listening"
    ser.write('7sx\r')
    time.sleep(5)
    ser.write('3132\r')
    time.sleep(5)
    ser.write('7p\r')
    time.sleep(5)
    if line == '1':
     serdata = ser.read(10)
    elif line == '2':
     bytesToRead = ser.inWaiting()
     serdata = ser.read(bytesToRead)
    print "serial data is",serdata
    udprecv = sock7.recv(100)
    print "udp recv is", udprecv
    if (serdata == '1460KKK') and (udprecv == '12'):
     print "vut received data"
     result = 1
    else:
     print "failed to receive data from vut"

    print "Test mux instance 8"
    if (interface == 'eth0'):
     ser.write('8aeth0:10008udp\r')
    elif interface == 'wlan0':
     ser.write('8awlan0:10008udp\r')
    elif network == 'ap0':
     ser.write('8aap0:10008udp\r')
    time.sleep(3)
    mes = 'hello'
    sock8.sendto(mes,(device_ip,tunport8))
    time.sleep(3)
    out = childid.expect(['g','K'])
    print "out is", out
    if out ==  1:
     print "mux udp is listening"
    ser.write('8sx\r')
    time.sleep(5)
    ser.write('3132\r')
    time.sleep(5)
    ser.write('8p\r')
    time.sleep(5)
    if line == '1':
     serdata = ser.read(10)
    elif line == '2':
     bytesToRead = ser.inWaiting()
     serdata = ser.read(bytesToRead)
    print "serial data is",serdata
    udprecv = sock8.recv(100)
    print "udp recv is", udprecv
    if (serdata == '1460KKK') and (udprecv == '12'):
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
  sock2.close()
  sock3.close()
  sock4.close()
  sock5.close()
  sock6.close()
  sock7.close()
  sock8.close()
  return result
 except Exception as e:
  print(str(e))


def mux_tcp_connect_accept():
 print "Test MUX TCP Connect And Accept"
 if (line == '1'):
  ser = serial.Serial(serial_port, '{0}'.format(baudrate), timeout=0, parity='{0}'.format(parity), stopbits = int('{0}'.format(stopbits)), bytesize = int('{0}'.format(databits)), rtscts = True)
 else:
  ser = serial.Serial(serial_port,xonxoff=True)
 childid = pexpect.fdpexpect.fdspawn(ser)
 ser.close()
 ser.open()
 sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 tunport1 = int(10001)
 tunport2 = int(10002)
 tunport3 = int(10003)
 tunport4 = int(10004)
 tunport5 = int(10005)
 tunport6 = int(10006)
 tunport7 = int(10007)
 tunport8 = int(10008)
 sock.settimeout(20)

 if protocol == 'tcp':
  sock.bind((remote_ip,4001))
  sock.listen(1)
 elif protocol =='tcpaes':
  importxml()
  sock.connect(('192.168.51.87',10001))
 result = 0
 muxrec_result = 0
 hexsend_result = 0
 sendbinary_result = 0
 readbinary_result = 0
 time.sleep(5)
 print "Test Mux connect instance 1"
 try:
  if ser.isOpen():
   print "serial opened"
   ser.flushInput()
   ser.flushOutput()
   time.sleep(10)
   print 'test case 1: mux receive'
   print "connect to remote host"
   if protocol == 'tcp':
    ser.write('1c'+remote_ip+':4001tcp\r')
   elif protocol == 'tcpaes':
    ser.write('1c'+remote_ip+':10001tcp aes,aes\r')
   time.sleep(5)
   if (line == 'CDC_ACM'):
     time.sleep(60)
   print "verify connection"
   ser.write("1\r")
   #time.sleep(2)
   connect_out = childid.expect(['123','K'])
   if (connect_out == 1):
    print "connection established. received K"
    print "test case: tcp mux receive passed"
    muxrec_result = 1
   else:
    print "failed to establish the connection"
    print "test case: tcp mux receive failed"
    muxrec_result = 0
  
   if protocol == 'tcp': 
    conn,addr = sock.accept()
    print 'connected by',addr
   print "sending"
   print "waiting for receiving event/data"
   ser.write('W1r\r')
   time.sleep(5)
   print "send data"
   if protocol =='tcp':
    conn.send('abcde')
   elif protocol == 'tcpaes':
    sock.send('abcde')
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
   if (line == 'CDC_ACM'):
    time.sleep(60)
   else:
    time.sleep(5)
   if line == '1':
    serdata = ser.read(10)
   elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
   print "serdata",serdata 
   time.sleep(5)
   print "reading data from serial"
   if (line == 'CDC_ACM'):
    time.sleep(60)
   else:
    time.sleep(10)
   if (serdata == "Kabcde"):
    print "data read from serial"
   else:
    print "failed to read data from serial"

   if (connect_out == 1) and (out1 == 1) and (serdata == 'Kabcde'):
     print "test case: tcp mux receive passed"
     muxrec_result = 1
   else:
     print "test case: tcp mux receive failed"
   
 
   print "test case 2: send and push Hex data"
   print "initiate hex data send"
   ser.write('1sx\r')
   #print "check"
   time.sleep(3)
   print ser.read()
   out = childid.expect(['K','hello'])
   #time.sleep(3)
   if (out == 0):
    print "hex data send initiated"
   else:
    print "failed to initiate hex data send"

   print "send data"
   if (line == 'CDC_ACM'):
    time.sleep(5)
   ser.write('313233\r')
   time.sleep(5)
   if (line == 'CDC_ACM'):
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
   if protocol == 'tcp':
    connect_recdata = conn.recv(100)
   elif protocol == 'tcpaes':
    connect_recdata = sock.recv(100)
   time.sleep(3)
   if (connect_recdata == '123'):
    print "data received"
    recdata = 1
   else:
    print "failed to receive data"
   if (out == 0) and (out1 == 1) and (recdata == 1):
    print "test case: hex data send passed"
    hexsend_result = 1
   else:
    print "test case: hex data send failed"


   print "test case 3: read binary data"
   ser.write('1rb.80\r')
   time.sleep(3)
   out = childid.expect(['K'])
   time.sleep(3)
   if (out == 0):
    print "binary data read initiated"
   if protocol == 'tcp':
    conn.send('abcd')
   elif protocol == 'tcpaes':
    sock.send('abcd')
   print "binary data sent"
   time.sleep(2)
   if line == '1':
    serdata = ser.read(20)
   elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
   time.sleep(2)
   print "data read from serial is", serdata
   serdata = re.search('abcd',serdata)
   if (out == 0) and serdata:
    print "test case: binary data receive passed"
    readbinary_result = 1
   else:
    print "failed to receive binary data"
    readbinary_result = 0
###############################################

   print "test case 4: send binary data and end the connection"
   ser.write('1sb.\r')
   time.sleep(3)
   out = childid.expect(['K','xyz'])
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
   ser.write('1p\r')
   time.sleep(4)
   if protocol == 'tcp':
    recdata = conn.recv(100)
   elif protocol == 'tcpaes':
    recdata = sock.recv(100)
   time.sleep(2)
   print "data received", recdata
   
   if (out == 0) and (out1 == 0) and (recdata == '12345678'):
     sendbinary_result = 1
     print "test case: send binary passed"
   else:
     print "failed to send binary data"

   
   
   print "muxrec_result is ", muxrec_result
   print "hexsend_result is", hexsend_result
   print "sendbinary_result is", sendbinary_result
   print "readbinary_result is", readbinary_result
  #print "muxhttp_result is",muxHttp_result
  
   if muxrec_result == 1 and hexsend_result == 1 and sendbinary_result == 1 and readbinary_result == 1:
    connect_inst = 1
   else:
    connect_inst = 0

   print "Test mux connect and accept instance 1" 
   print "Test mux accept instance 1"
   if interface == 'eth0':
    if protocol == 'tcp':
     ser.write('5aeth0:10005tcp\r')
    elif protocol == 'tcpaes':
     ser.write('5aeth0:10005tcp aes,aes\r')
   elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('5awlan0:10005tcp\r')
     elif protocol == 'tcpaes':
      ser.write('5awlan0:10005tcp aes,aes\r')
   print "check listening sockets"
   time.sleep(15)
   if protocol == 'tcp':
    sock1.connect((device_ip,tunport5))
   elif protocol == 'tcpaes':
    sock1.connect(('192.168.51.87',10005))
   print "verify connection"
   ser.write("5\r")
   #time.sleep(2)
   out = childid.expect(['123','K'])
   #time.sleep(2)
   if (out == 1):
    print "connection established. received K"
    print "test case: tcp mux receive passed"
    muxrec_result = 1
   else:
    print "failed to establish the connection"
    print "test case: tcp mux receive failed"
    muxrec_result = 0
  

   print "test case 2: send and push Hex data"
   print "initiate hex data send"
   ser.write('5sx\r')
   #print "check"
   time.sleep(3)
   print ser.read()
   out = childid.expect(['K','hello'])
   #time.sleep(3)
   if (out == 0):
    print "hex data send initiated"
   else:
    print "failed to initiate hex data send"

   print "send data"
   if (line == 'CDC_ACM'):
    time.sleep(5)
   ser.write('313233\r')
   time.sleep(5)
   if (line == 'CDC_ACM'):
    time.sleep(60)
   out1 = childid.expect(['hello','K'])
   time.sleep(3)
   if (out1 == 1):
    print "data sent"
   else:
    print "failed to send data"

   print "push data from mux and verify remote host receives data"
   ser.write('5p\r')
   time.sleep(5)
   accept_recdata = sock1.recv(100)
   time.sleep(3)
   print accept_recdata
   if accept_recdata == '123':
    print "data received"
    recdata = 1
   else:
    print "failed to receive data"
   if (out == 0) and (out1 == 1) and (recdata == 1):
    print "test case: hex data send passed"
    hexsend_result = 1
   else:
    print "test case: hex data send failed"
 
###############################################

   print "test case 3: read binary data"
   ser.write('5rb.80\r')
   time.sleep(3)
   out = childid.expect(['K'])
   time.sleep(3)
   if (out == 0):
    print "binary data read initiated"
   sock1.send('abcd')
   print "binary data sent"
   time.sleep(2)
   if line == '1':
    serdata = ser.read(20)
   elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
   time.sleep(2)
   print "data read from serial is", serdata
   serdata = re.search('abcd',serdata)
   if (out == 0) and serdata:
    print "test case: binary data receive passed"
    readbinary_result = 1
   else:
    print "failed to receive binary data"
    readbinary_result = 0
###############################################

   print "test case 4: send binary data and end the connection"
   ser.write('5sb.\r')
   time.sleep(3)
   out = childid.expect(['K','xyz'])
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
   ser.write('5p\r')
   time.sleep(4)
   accept_recdata = sock1.recv(100)
   time.sleep(2)
   print "data received", recdata
   
   if (out == 0) and (out1 == 0) and (accept_recdata == '12345678'):
     sendbinary_result = 1
     print "test case: send binary passed"
   else:
     print "failed to send binary data"
   
   print "muxrec_result is ", muxrec_result
   print "hexsend_result is", hexsend_result
   print "sendbinary_result is", sendbinary_result
   print "readbinary_result is", readbinary_result
  #print "muxhttp_result is",muxHttp_result

   if muxrec_result == 1 and hexsend_result == 1 and sendbinary_result == 1 and readbinary_result == 1:
    accept_inst = 1
   else:
    accept_inst = 0

 
   if connect_inst == 1 and accept_inst  == 1:
     print "mux connect and accept instance 1 passed"
     inst1_result = 1
   else:
     print "mux connect and accept instance 1 failed"
     inst1_result = 0

   print "Test mux connect and accept instance 2"
   print "Test mux connect instance 2"
   sock3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   if protocol == 'tcp':   
    sock3.bind((remote_ip,4002))
    sock3.listen(1)
   elif protocol == 'tcpaes':
    sock3.connect(('192.168.51.87',10002))
   sock4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   print 'test case 1: mux receive'
   print "connect to remote host"
   if protocol == 'tcp':
    ser.write('2c'+remote_ip+':4002tcp\r')
   elif protocol == 'tcpaes':
    ser.write('2c'+remote_ip+':10002tcp aes,aes\r')
   time.sleep(5)
   if (line == 'CDC_ACM'):
     time.sleep(60)
   print "verify connection"
   ser.write("2\r")
   #time.sleep(2)
   connect_out = childid.expect(['123','K'])
   if (connect_out == 1):
    print "connection established. received K"
    print "test case: tcp mux receive passed"
    muxrec_result = 1
   else:
    print "failed to establish the connection"
    print "test case: tcp mux receive failed"
    muxrec_result = 0
   
   if protocol == 'tcp': 
    conn3,addr = sock3.accept()
    print 'connected by',addr
   print "sending"
   print "waiting for receiving event/data"
   ser.write('W2r\r')
   time.sleep(5)
   print "send data"
   if protocol == 'tcp':
    conn3.send('abcde')
   elif protocol == 'tcpaes':
    sock3.send('abcde')
   time.sleep(5)

   print "check whether is data waiting"
   out1 = childid.expect(['3','2r'])
   if (out1 == 1):
    print "data is waiting. received 2r"
   else:
    print "there is no data"

   print "read and check data"
   ser.write('2rb.80\r')
   time.sleep(5)
   if (line == 'CDC_ACM'):
    time.sleep(60)
   else:
    time.sleep(5)
   if line == '1':
    serdata = ser.read(10)
   elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
   print "serdata",serdata 
   time.sleep(5)
   print "reading data from serial"
   if (line == 'CDC_ACM'):
    time.sleep(60)
   else:
    time.sleep(10)
   if (serdata == "Kabcde"):
    print "data read from serial"
   else:
    print "failed to read data from serial"

   if (connect_out == 1) and (out1 == 1) and (serdata == 'Kabcde'):
     print "test case: tcp mux receive passed"
     muxrec_result = 1
   else:
     print "test case: tcp mux receive failed"
   
 
   print "test case 2: send and push Hex data"
   print "initiate hex data send"
   ser.write('2sx\r')
   #print "check"
   time.sleep(3)
   print ser.read()
   out = childid.expect(['K','hello'])
   #time.sleep(3)
   if (out == 0):
    print "hex data send initiated"
   else:
    print "failed to initiate hex data send"

   print "send data"
   if (line == 'CDC_ACM'):
    time.sleep(5)
   ser.write('313233\r')
   time.sleep(5)
   if (line == 'CDC_ACM'):
    time.sleep(60)
   out1 = childid.expect(['hello','K'])
   time.sleep(3)
   if (out1 == 1):
    print "data sent"
   else:
    print "failed to send data"

   print "push data from mux and verify remote host receives data"
   ser.write('2p\r')
   time.sleep(5)
   if protocol == 'tcp':
    connect_recdata = conn3.recv(100)
   elif protocol == 'tcpaes':
    connect_recdata = sock3.recv(100)
   time.sleep(3)
   if (connect_recdata == '123'):
    print "data received"
    recdata = 1
   else:
    print "failed to receive data"
   if (out == 0) and (out1 == 1) and (recdata == 1):
    print "test case: hex data send passed"
    hexsend_result = 1
   else:
    print "test case: hex data send failed"


   print "test case 3: read binary data"
   ser.write('2rb.80\r')
   time.sleep(3)
   out = childid.expect(['K'])
   time.sleep(3)
   if (out == 0):
    print "binary data read initiated"
   if protocol == 'tcp':
    conn3.send('abcd')
   elif protocol == 'tcpaes':
    sock3.send('abcd')
   print "binary data sent"
   time.sleep(2)
   if line == '1':
    serdata = ser.read(20)
   elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
   time.sleep(2)
   print "data read from serial is", serdata
   serdata = re.search('abcd',serdata)
   if (out == 0) and serdata:
    print "test case: binary data receive passed"
    readbinary_result = 1
   else:
    print "failed to receive binary data"
    readbinary_result = 0
###############################################

   print "test case 4: send binary data and end the connection"
   ser.write('2sb.\r')
   time.sleep(3)
   out = childid.expect(['K','xyz'])
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
   ser.write('2p\r')
   time.sleep(4)
   if protocol == 'tcp':
    recdata = conn3.recv(100)
   elif protocol == 'tcpaes':
    recdata = sock3.recv(100)
   time.sleep(2)
   print "data received", recdata
   
   if (out == 0) and (out1 == 0) and (recdata == '12345678'):
     sendbinary_result = 1
     print "test case: send binary passed"
   else:
     print "failed to send binary data"

   
   
   print "muxrec_result is ", muxrec_result
   print "hexsend_result is", hexsend_result
   print "sendbinary_result is", sendbinary_result
   print "readbinary_result is", readbinary_result
  #print "muxhttp_result is",muxHttp_result
  
   if muxrec_result == 1 and hexsend_result == 1 and sendbinary_result == 1 and readbinary_result == 1:
    connect_inst = 1
   else:
    connect_inst = 0

  
   print "Test mux connect and accept instance 2" 
   print "Test mux accept instance 2"
   if interface == 'eth0':
    if protocol == 'tcp':
     ser.write('6aeth0:10006tcp\r')
    elif protocol == 'tcpaes':
     ser.write('6aeth0:10006tcp aes,aes\r')
   elif interface == 'wlan0':
    if protocol == 'tcp':
     ser.write('6awlan0:10006tcp\r')
    elif protocol == 'tcpaes':
     ser.write('6awlan0:10006tcp aes,aes\r')
    #print "check listening sockets"
   time.sleep(15)
   if protocol == 'tcp':
    sock4.connect((device_ip, tunport6))
   elif protocol == 'tcpaes':
    sock4.connect(('192.168.51.87',10006))
   print "verify connection"
   ser.write("6\r")
   #time.sleep(2)
   out = childid.expect(['123','K'])
   #time.sleep(2)
   if (out == 1):
    print "connection established. received K"
    print "test case: tcp mux receive passed"
    muxrec_result = 1
   else:
    print "failed to establish the connection"
    print "test case: tcp mux receive failed"
    muxrec_result = 0
  

   print "test case 2: send and push Hex data"
   print "initiate hex data send"
   ser.write('6sx\r')
   #print "check"
   time.sleep(3)
   print ser.read()
   out = childid.expect(['K','hello'])
   #time.sleep(3)
   if (out == 0):
    print "hex data send initiated"
   else:
    print "failed to initiate hex data send"

   print "send data"
   if (line == 'CDC_ACM'):
    time.sleep(5)
   ser.write('313233\r')
   time.sleep(5)
   if (line == 'CDC_ACM'):
    time.sleep(60)
   out1 = childid.expect(['hello','K'])
   time.sleep(3)
   if (out1 == 1):
    print "data sent"
   else:
    print "failed to send data"

   print "push data from mux and verify remote host receives data"
   ser.write('6p\r')
   time.sleep(5)
   accept_recdata = sock4.recv(100)
   time.sleep(3)
   print accept_recdata
   if accept_recdata == '123':
    print "data received"
    recdata = 1
   else:
    print "failed to receive data"
   if (out == 0) and (out1 == 1) and (recdata == 1):
    print "test case: hex data send passed"
    hexsend_result = 1
   else:
    print "test case: hex data send failed"
 
###############################################

   print "test case 3: read binary data"
   ser.write('6rb.80\r')
   time.sleep(3)
   out = childid.expect(['K'])
   time.sleep(3)
   if (out == 0):
    print "binary data read initiated"
   sock4.send('abcd')
   print "binary data sent"
   time.sleep(2)
   if line == '1':
    serdata = ser.read(20)
   elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
   time.sleep(2)
   print "data read from serial is", serdata
   serdata = re.search('abcd',serdata)
   if (out == 0) and serdata:
    print "test case: binary data receive passed"
    readbinary_result = 1
   else:
    print "failed to receive binary data"
    readbinary_result = 0
###############################################

   print "test case 4: send binary data and end the connection"
   ser.write('6sb.\r')
   time.sleep(3)
   out = childid.expect(['K','xyz'])
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
   ser.write('6p\r')
   time.sleep(4)
   accept_recdata = sock4.recv(100)
   time.sleep(2)
   print "data received", recdata
   
   if (out == 0) and (out1 == 0) and (accept_recdata == '12345678'):
     sendbinary_result = 1
     print "test case: send binary passed"
   else:
     print "failed to send binary data"
   
   print "muxrec_result is ", muxrec_result
   print "hexsend_result is", hexsend_result
   print "sendbinary_result is", sendbinary_result
   print "readbinary_result is", readbinary_result
  #print "muxhttp_result is",muxHttp_result

   if muxrec_result == 1 and hexsend_result == 1 and sendbinary_result == 1 and readbinary_result == 1:
    accept_inst = 1
   else:
    accept_inst = 0

 
   if connect_inst == 1 and accept_inst  == 1:
     print "mux connect and accept instance 2 passed"
     inst2_result = 1
   else:
     print "mux connect and accept instance 2 failed"
     inst2_result = 0

   
   print "Test mux connect and accept instance 3"
   print "Test mux connect instance 3"
   sock4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   if protocol == 'tcp':
    sock4.bind((remote_ip,4003))
    sock4.listen(1)
   elif protocol == 'tcpaes':
    sock4.connect(('192.168.51.87',10003))
   sock5 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   print 'test case 1: mux receive'
   print "connect to remote host"
   if protocol == 'tcp':
    ser.write('3c'+remote_ip+':4003tcp\r')
   elif protocol == 'tcpaes':
    ser.write('3c'+remote_ip+':10003tcp aes,aes\r')
   time.sleep(5)
   if (line == 'CDC_ACM'):
     time.sleep(60)
   print "verify connection"
   ser.write("3\r")
   connect_out = childid.expect(['123','K'])
   if (connect_out == 1):
    print "connection established. received K"
    print "test case: tcp mux receive passed"
    muxrec_result = 1
   else:
    print "failed to establish the connection"
    print "test case: tcp mux receive failed"
    muxrec_result = 0
 
   if protocol == 'tcp': 
    conn4,addr = sock4.accept()
    print 'connected by',addr
   print "sending"
   print "waiting for receiving event/data"
   ser.write('W3r\r')
   time.sleep(5)
   print "send data"
   if protocol == 'tcp':
    conn4.send('abcde')
   elif protocol == 'tcpaes':
    sock4.send('abcde')
   time.sleep(5)

   print "check whether is data waiting"
   out1 = childid.expect('3r')
   if (out1 == 0):
    print "data is waiting. received 3r"
   else:
    print "there is no data"

   print "read and check data"
   ser.write('3rb.80\r')
   time.sleep(5)
   if (line == 'CDC_ACM'):
    time.sleep(60)
   else:
    time.sleep(5)
   if line == '1':
    serdata = ser.read(10)
   elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
   print "serdata",serdata 
   time.sleep(5)
   print "reading data from serial"
   if (line == 'CDC_ACM'):
    time.sleep(60)
   else:
    time.sleep(10)
   if (serdata == "Kabcde"):
    print "data read from serial"
   else:
    print "failed to read data from serial"

   if (connect_out == 1) and (out1 == 0) and (serdata == 'Kabcde'):
     print "test case: tcp mux receive passed"
     muxrec_result = 1
   else:
     print "test case: tcp mux receive failed"
     muxrec_result = 0
   
 
   print "test case 2: send and push Hex data"
   print "initiate hex data send"
   ser.write('3sx\r')
   #print "check"
   time.sleep(3)
   print ser.read()
   out = childid.expect(['K','hello'])
   #time.sleep(3)
   if (out == 0):
    print "hex data send initiated"
   else:
    print "failed to initiate hex data send"

   print "send data"
   if (line == 'CDC_ACM'):
    time.sleep(5)
   ser.write('313233\r')
   time.sleep(5)
   if (line == 'CDC_ACM'):
    time.sleep(60)
   out1 = childid.expect(['hello','K'])
   time.sleep(3)
   if (out1 == 1):
    print "data sent"
   else:
    print "failed to send data"

   print "push data from mux and verify remote host receives data"
   ser.write('3p\r')
   time.sleep(5)
   if protocol == 'tcp':
    connect_recdata = conn4.recv(100)
   elif protocol == 'tcpaes':
    connect_recdata = sock4.recv(100)
   time.sleep(3)
   if (connect_recdata == '123'):
    print "data received"
    recdata = 1
   else:
    print "failed to receive data"
   if (out == 0) and (out1 == 1) and (recdata == 1):
    print "test case: hex data send passed"
    hexsend_result = 1
   else:
    print "test case: hex data send failed"


   print "test case 3: read binary data"
   ser.write('3rb.80\r')
   time.sleep(3)
   out = childid.expect(['K'])
   time.sleep(3)
   if (out == 0):
    print "binary data read initiated"
   if protocol == 'tcp':
    conn4.send('abcd')
   elif protocol == 'tcpaes':
    sock4.send('abcd')
   print "binary data sent"
   time.sleep(2)
   if line == '1':
    serdata = ser.read(20)
   elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
   time.sleep(2)
   print "data read from serial is", serdata
   serdata = re.search('abcd',serdata)
   if (out == 0) and serdata:
    print "test case: binary data receive passed"
    readbinary_result = 1
   else:
    print "failed to receive binary data"
    readbinary_result = 0
###############################################

   print "test case 4: send binary data and end the connection"
   ser.write('3sb.\r')
   time.sleep(3)
   out = childid.expect(['K','xyz'])
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
   ser.write('3p\r')
   time.sleep(4)
   if protocol == 'tcp':
    recdata = conn4.recv(100)
   elif protocol == 'tcpaes':
    recdata = sock4.recv(100)
   time.sleep(2)
   print "data received", recdata
   
   if (out == 0) and (out1 == 0) and (recdata == '12345678'):
     sendbinary_result = 1
     print "test case: send binary passed"
   else:
     print "failed to send binary data"

   
   
   print "muxrec_result is ", muxrec_result
   print "hexsend_result is", hexsend_result
   print "sendbinary_result is", sendbinary_result
   print "readbinary_result is", readbinary_result
  #print "muxhttp_result is",muxHttp_result
  
   if muxrec_result == 1 and hexsend_result == 1 and sendbinary_result == 1 and readbinary_result == 1:
    connect_inst = 1
   else:
    connect_inst = 0

  
   print "Test mux connect and accept instance 3" 
   print "Test mux accept instance 3"
   if interface == 'eth0':
    if protocol == 'tcp':
     ser.write('7aeth0:10007tcp\r')
    elif protocol == 'tcpaes':
     ser.write('7aeth0:10007tcp aes,aes\r')
   elif interface == 'wlan0':
    if protocol == 'tcp':
     ser.write('7awlan0:10007tcp\r')
    elif protocol == 'tcpaes':
     ser.write('7awlan0:10007tcp aes,aes\r')
   print "check listening sockets"
   time.sleep(12)
   if protocol == 'tcp':
    sock5.connect((device_ip, tunport7))
   elif protocol == 'tcpaes':
    sock5.connect(('192.168.51.87',10007))
   print "verify connection"
   ser.write("7\r")
   #time.sleep(2)
   out = childid.expect(['123','K'])
   #time.sleep(2)
   if (out == 1):
    print "connection established. received K"
    print "test case: tcp mux receive passed"
    muxrec_result = 1
   else:
    print "failed to establish the connection"
    print "test case: tcp mux receive failed"
    muxrec_result = 0
  

   print "test case 2: send and push Hex data"
   print "initiate hex data send"
   ser.write('7sx\r')
   #print "check"
   time.sleep(3)
   print ser.read()
   out = childid.expect(['K','hello'])
   #time.sleep(3)
   if (out == 0):
    print "hex data send initiated"
   else:
    print "failed to initiate hex data send"

   print "send data"
   if (line == 'CDC_ACM'):
    time.sleep(5)
   ser.write('313233\r')
   time.sleep(10)
   if (line == 'CDC_ACM'):
    time.sleep(60)
   out1 = childid.expect(['hello','K'])
   time.sleep(3)
   if (out1 == 1):
    print "data sent"
   else:
    print "failed to send data"

   print "push data from mux and verify remote host receives data"
   ser.write('7p\r')
   time.sleep(5)
   accept_recdata = sock5.recv(100)
   time.sleep(3)
   print accept_recdata
   if accept_recdata == '123':
    print "data received"
    recdata = 1
   else:
    print "failed to receive data"
   if (out == 0) and (out1 == 1) and (recdata == 1):
    print "test case: hex data send passed"
    hexsend_result = 1
   else:
    print "test case: hex data send failed"
 
###############################################

   print "test case 3: read binary data"
   ser.write('7rb.80\r')
   time.sleep(3)
   out = childid.expect(['K'])
   time.sleep(3)
   if (out == 0):
    print "binary data read initiated"
   sock5.send('abcd')
   print "binary data sent"
   time.sleep(2)
   if line == '1':
    serdata = ser.read(20)
   elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
   time.sleep(2)
   print "data read from serial is", serdata
   serdata = re.search('abcd',serdata)
   if (out == 0) and serdata:
    print "test case: binary data receive passed"
    readbinary_result = 1
   else:
    print "failed to receive binary data"
    readbinary_result = 0
###############################################

   print "test case 4: send binary data and end the connection"
   ser.write('7sb.\r')
   time.sleep(3)
   out = childid.expect(['K','xyz'])
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
   ser.write('7p\r')
   time.sleep(4)
   accept_recdata = sock5.recv(100)
   time.sleep(2)
   print "data received", recdata
   
   if (out == 0) and (out1 == 0) and (accept_recdata == '12345678'):
     sendbinary_result = 1
     print "test case: send binary passed"
   else:
     print "failed to send binary data"
   
   print "muxrec_result is ", muxrec_result
   print "hexsend_result is", hexsend_result
   print "sendbinary_result is", sendbinary_result
   print "readbinary_result is", readbinary_result
  #print "muxhttp_result is",muxHttp_result

   if muxrec_result == 1 and hexsend_result == 1 and sendbinary_result == 1 and readbinary_result == 1:
    accept_inst = 1
   else:
    accept_inst = 0

 
   if connect_inst == 1 and accept_inst  == 1:
     print "mux connect and accept instance 3 passed"
     inst3_result = 1
   else:
     print "mux connect and accept instance 3 failed"
     inst3_result = 0
   

   print "Test mux connect and accept instance 4 "
   print "Test mux connect instance 4"
   sock7 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   if protocol == 'tcp':
    sock7.bind((remote_ip,4004))
    sock7.listen(1)
   elif protocol == 'tcpaes':
    sock7.connect(('192.168.51.87',10004))
   sock8 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   print 'test case 1: mux receive'
   print "connect to remote host"
   if protocol == 'tcp':
    ser.write('4c'+remote_ip+':4004tcp\r')
   elif protocol == 'tcpaes':
    ser.write('4c'+remote_ip+':10004tcp aes,aes\r')
   time.sleep(5)
   if (line == 'CDC_ACM'):
     time.sleep(60)
   print "verify connection"
   ser.write("4\r")
   #time.sleep(2)
   connect_out = childid.expect(['123','K'])
   if (connect_out == 1):
    print "connection established. received K"
    print "test case: tcp mux receive passed"
    muxrec_result = 1
   else:
    print "failed to establish the connection"
    print "test case: tcp mux receive failed"
    muxrec_result = 0
 
   if protocol == 'tcp': 
    conn7,addr = sock7.accept()
    print 'connected by',addr
   print "sending"
   print "waiting for receiving event/data"
   ser.write('W4r\r')
   time.sleep(5)
   print "send data"
   if protocol == 'tcp':
    conn7.send('abcde')
   elif protocol == 'tcpaes':
    sock7.send('abcde')
   time.sleep(3)

   print "check whether is data waiting"
   out1 = childid.expect('4r')
   if (out1 == 0):
    print "data is waiting. received 4r"
   else:
    print "there is no data"

   print "read and check data"
   ser.write('4rb.80\r')
   time.sleep(5)
   if (line == 'CDC_ACM'):
    time.sleep(60)
   else:
    time.sleep(5)
   if line == '1':
    serdata = ser.read(10)
   elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
   print "serdata",serdata 
   time.sleep(5)
   print "reading data from serial"
   if (line == 'CDC_ACM'):
    time.sleep(60)
   else:
    time.sleep(10)
   if (serdata == "Kabcde"):
    print "data read from serial"
   else:
    print "failed to read data from serial"

   if (connect_out == 1) and (out1 == 0) and (serdata == 'Kabcde'):
     print "test case: tcp mux receive passed"
     muxrec_result = 1
   else:
     print "test case: tcp mux receive failed"
     muxrec_result = 0 
 
   print "test case 2: send and push Hex data"
   print "initiate hex data send"
   ser.write('4sx\r')
   #print "check"
   time.sleep(3)
   print ser.read()
   out = childid.expect(['K','hello'])
   #time.sleep(3)
   if (out == 0):
    print "hex data send initiated"
   else:
    print "failed to initiate hex data send"

   print "send data"
   if (line == 'CDC_ACM'):
    time.sleep(5)
   ser.write('313233\r')
   time.sleep(5)
   if (line == 'CDC_ACM'):
    time.sleep(60)
   out1 = childid.expect(['hello','K'])
   time.sleep(3)
   if (out1 == 1):
    print "data sent"
   else:
    print "failed to send data"

   print "push data from mux and verify remote host receives data"
   ser.write('4p\r')
   time.sleep(5)
   if protocol == 'tcp':
    connect_recdata = conn7.recv(100)
   elif protocol == 'tcpaes':
    connect_recdata = sock7.recv(100)
   time.sleep(3)
   if (connect_recdata == '123'):
    print "data received"
    recdata = 1
   else:
    print "failed to receive data"
   if (out == 0) and (out1 == 1) and (recdata == 1):
    print "test case: hex data send passed"
    hexsend_result = 1
   else:
    print "test case: hex data send failed"


   print "test case 3: read binary data"
   ser.write('4rb.80\r')
   time.sleep(3)
   out = childid.expect(['K'])
   time.sleep(3)
   if (out == 0):
    print "binary data read initiated"
   if protocol == 'tcp':
    conn7.send('abcd')
   elif protocol == 'tcpaes':
    sock7.send('abcd')
   print "binary data sent"
   time.sleep(2)
   if line == '1':
    serdata = ser.read(20)
   elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
   time.sleep(2)
   print "data read from serial is", serdata
   serdata = re.search('abcd',serdata)
   if (out == 0) and serdata:
    print "test case: binary data receive passed"
    readbinary_result = 1
   else:
    print "failed to receive binary data"
    readbinary_result = 0
###############################################

   print "test case 4: send binary data and end the connection"
   ser.write('4sb.\r')
   time.sleep(3)
   out = childid.expect(['K','xyz'])
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
   ser.write('4p\r')
   time.sleep(4)
   if protocol == 'tcp':
    recdata = conn7.recv(100)
   elif protocol == 'tcpaes':
    recdata = sock7.recv(100)
   time.sleep(2)
   print "data received", recdata
   
   if (out == 0) and (out1 == 0) and (recdata == '12345678'):
     sendbinary_result = 1
     print "test case: send binary passed"
   else:
     print "failed to send binary data"

   
   
   print "muxrec_result is ", muxrec_result
   print "hexsend_result is", hexsend_result
   print "sendbinary_result is", sendbinary_result
   print "readbinary_result is", readbinary_result
  #print "muxhttp_result is",muxHttp_result
  
   if muxrec_result == 1 and hexsend_result == 1 and sendbinary_result == 1 and readbinary_result == 1:
    connect_inst = 1
   else:
    connect_inst = 0

  
   print "Test mux connect and accept instance 4" 
   print "Test mux accept instance 4"
   if interface == 'eth0':
    if protocol == 'tcp':
     ser.write('8aeth0:10008tcp\r')
    elif protocol == 'tcpaes':
     ser.write('8aeth0:10008tcp aes,aes\r')
   elif interface == 'wlan0':
    if protocol == 'tcp':
     ser.write('8awlan0:10008tcp\r')
    elif protocol == 'tcpaes':
     ser.write('8awlan0:10008tcp aes,aes\r')
   print "check listening sockets"
   time.sleep(15)
   if protocol == 'tcp':
    sock8.connect((device_ip,tunport8))
   elif protocol == 'tcpaes':
    sock8.connect(('192.168.51.87',10008))
   print "verify connection"
   ser.write("8\r")
   #time.sleep(2)
   out = childid.expect(['123','K'])
   #time.sleep(2)
   if (out == 1):
    print "connection established. received K"
    print "test case: tcp mux receive passed"
    muxrec_result = 1
   else:
    print "failed to establish the connection"
    print "test case: tcp mux receive failed"
    muxrec_result = 0
  

   print "test case 2: send and push Hex data"
   print "initiate hex data send"
   ser.write('8sx\r')
   #print "check"
   time.sleep(3)
   print ser.read()
   out = childid.expect(['K','hello'])
   #time.sleep(3)
   if (out == 0):
    print "hex data send initiated"
   else:
    print "failed to initiate hex data send"

   print "send data"
   if (line == 'CDC_ACM'):
    time.sleep(5)
   ser.write('313233\r')
   time.sleep(5)
   if (line == 'CDC_ACM'):
    time.sleep(60)
   out1 = childid.expect(['hello','K'])
   time.sleep(3)
   if (out1 == 1):
    print "data sent"
   else:
    print "failed to send data"

   print "push data from mux and verify remote host receives data"
   ser.write('8p\r')
   time.sleep(5)
   accept_recdata = sock8.recv(100)
   time.sleep(3)
   print accept_recdata
   if accept_recdata == '123':
    print "data received"
    recdata = 1
   else:
    print "failed to receive data"
   if (out == 0) and (out1 == 1) and (recdata == 1):
    print "test case: hex data send passed"
    hexsend_result = 1
   else:
    print "test case: hex data send failed"
 
###############################################

   print "test case 3: read binary data"
   ser.write('8rb.80\r')
   time.sleep(3)
   out = childid.expect(['K'])
   time.sleep(3)
   if (out == 0):
    print "binary data read initiated"
   sock8.send('abcd')
   print "binary data sent"
   time.sleep(2)
   if line == '1':
    serdata = ser.read(20)
   elif line == '2':
    bytesToRead = ser.inWaiting()
    serdata = ser.read(bytesToRead)
   time.sleep(2)
   print "data read from serial is", serdata
   serdata = re.search('abcd',serdata)
   if (out == 0) and serdata:
    print "test case: binary data receive passed"
    readbinary_result = 1
   else:
    print "failed to receive binary data"
    readbinary_result = 0
###############################################

   print "test case 4: send binary data and end the connection"
   ser.write('8sb.\r')
   time.sleep(3)
   out = childid.expect(['K','xyz'])
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
   ser.write('8p\r')
   time.sleep(4)
   accept_recdata = sock8.recv(100)
   time.sleep(2)
   print "data received", recdata
   
   if (out == 0) and (out1 == 0) and (accept_recdata == '12345678'):
     sendbinary_result = 1
     print "test case: send binary passed"
   else:
     print "failed to send binary data"
   
   print "muxrec_result is ", muxrec_result
   print "hexsend_result is", hexsend_result
   print "sendbinary_result is", sendbinary_result
   print "readbinary_result is", readbinary_result
  #print "muxhttp_result is",muxHttp_result

   if muxrec_result == 1 and hexsend_result == 1 and sendbinary_result == 1 and readbinary_result == 1:
    accept_inst = 1
   else:
    accept_inst = 0

 
   if connect_inst == 1 and accept_inst  == 1:
     print "mux connect and accept instance 4 passed"
     inst4_result = 1
   else:
     print "mux connect and accept instance 4 failed"
     inst4_result = 0

  print "end connection"
  ser.write('1e\r')
  time.sleep(10)
  end1 = childid.expect(['K','FG'])
  print "end connection1"
  ser.write('2e\r')
  time.sleep(10)
  end2 = childid.expect(['K','FG'])
  print "end connection2"
  ser.write('3e\r')
  time.sleep(10)
  end3 = childid.expect(['K','F'])
  print "end connection3"
  ser.write('4e\r')
  time.sleep(10)
  end4 = childid.expect(['K','F'])
  print "end connection4"
  ser.write('5e\r')
  time.sleep(10)
  end5 = childid.expect(['K','F'])
  print "end connection5"
  ser.write('6e\r')
  time.sleep(10)
  end6 = childid.expect('K')
  print "end connection6"
  ser.write('7e\r')
  time.sleep(10)
  end7 = childid.expect('K')
  print "end connection7"
  ser.write('8e\r')
  time.sleep(10)
  end8 = childid.expect('K')
  print "end connection8"

  if end1 == 0 and end2 == 0 and end3 == 0 and end4 == 0 and end5 == 0 and end6 == 0 and end7 ==0 and end8 == 0:
   print "connection ended"
   endconn_result = 1
  else:
   print "connection did not end"
   endconn_result = 0

  if inst1_result == 1 and inst2_result == 1 and inst3_result == 1 and inst4_result == 1 and endconn_result == 1:
   print "mux tcp connect and accept mode test case passed"
   result = 1
  else:
   print "mux tcp connect and accept mode test case failed"
   result = 0

 except Exception as e:
  print(str(e))
 return result

 
###############################################


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
  clientid.expect('Rebooting')
  time.sleep(40)
  clientid = pexpect.spawn('telnet '+device_ip)
  clientid.sendline('\r')
  clientid.sendline('\r')
  print "configuring device"
  clientid.sendline('config\r')
  clientid.expect('config')
  if (line == '1'):
    clientid.sendline('line {0}'.format(line))
    clientid.expect('config Line {0}'.format(line))
  #if (line == '1') or (line == '2'):
    clientid.sendline('baud rate {0}'.format(baudrate))
    clientid.expect('config Line {0}'.format(line))
    clientid.sendline('data bits {0}'.format(databits))
    clientid.expect('config Line {0}'.format(line))
    clientid.sendline('parity {0}'.format(parity))
    clientid.expect('config Line {0}'.format(line))
    clientid.sendline('stop bits {0}'.format(stopbits))
    clientid.expect('config Line {0}'.format(line))
   #if line == '1':
    clientid.sendline('flow control hardware\r')
   #elif line == '2':
    #clientid.sendline('flow control software\r')
    clientid.expect('config Line {0}'.format(line))
    clientid.sendline('protocol mux\r')
    clientid.sendline('exit\r')
    clientid.expect('config')
    clientid.sendline('write\r')
    clientid.expect('config')
    clientid.sendline('write\r')
    clientid.expect('config')
    clientid.sendline('exit\r')
    clientid.expect('>')
  else:
    clientid.sendline('line CDC_ACM')    
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
  if conn_type == 'connect' or conn_type == 'accept': 
   if protocol == 'tcp' or protocol == 'tcpaes':
    result = mux_tcp()
   elif protocol == 'udp':
    result = mux_udp()
  if conn_type == 'both':
   result = mux_tcp_connect_accept()
  print "result is", result
  if result == 1:
    print "MUX "+protocol+" 8 instances TEST CASE PASSED"
  else:
    print "MUX "+protocol+" 8 instances TEST CASE FAILED"

# main program
device_config(tunnel_port)

sys.exit()

