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
import ssl,socket

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

xml_path = "/home/lantronix/MIDAS/xml/"

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
  req = br.open('http://192.168.51.132/form.html')
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

def importxml():
  print "import xml to add tls credential"
  xml = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"muxtls.xml")
  xml_res = re.search('completed',xml)
  if xml_res:
    print "xml import completed."
  else:
    print "xml import failed"

def mux_tls():
 importxml()
 print "mux outgoing connection tests begin"
 if (line == '1'):
  ser = serial.Serial(serial_port, '{0}'.format(baudrate), timeout=0, parity='{0}'.format(parity), stopbits = int('{0}'.format(stopbits)), bytesize = int('{0}'.format(databits)), rtscts = True)
 else:
  ser = serial.Serial(serial_port,xonxoff=True)
 childid = pexpect.fdpexpect.fdspawn(ser)
 ser.close()
 ser.open()
 sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 tunport1 = int(30001)
 tunport2 = int(30002)
 tunport3 = int(30003)
 tunport4 = int(30004)
 sock.settimeout(20)
 if (conn_type == 'connect'):
  sock.bind((remote_ip,4001))
  sock.listen(1) 
 result = 0
 muxrec_result = 0
 hexsend_result = 0
 sendbinary_result = 0
 readbinary_result = 0
 time.sleep(5)
 try:
  if ser.isOpen():
   print "Test Mux instance 1"
   print "serial opened"
   ser.flushInput()
   ser.flushOutput()
   time.sleep(10)
   print 'test case 1: mux receive'
   print "connect to remote host"
   if (conn_type == 'connect'): 
    ser.write('1c192.168.51.25:20001tls,client\r')
    time.sleep(8)
    if (line == 'CDC_ACM'):
     time.sleep(60)
   elif (conn_type == 'accept') and (restricted == '0'):
    if interface == 'eth0':
     ser.write('1aeth0:10001tls,server\r')
    elif interface == 'wlan0':
     ser.write('1awlan0:10001tls,server\r')
    print "check listening sockets"
    time.sleep(3)
    sock.connect((remote_ip,tunport1))
   elif (conn_type == 'accept') and (restricted == '1'):
    if interface == 'eth0':
     ser.write('1aeth0:10001tls,server\r')
    elif interface == 'wlan0':
     ser.write('1awlan0:10001tls,server\r')
    print "check listening sockets"
    time.sleep(10)
    sock.connect((remote_ip,tunport1))
   print "verify connection"
   ser.write("1\r")
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
    recdata = conn.recv(100)
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
   print "start listener"
   sock2.bind((remote_ip,4002))
   sock2.listen(1)

  print 'test case 1: mux receive'
  print "connect to remote host"
  if (conn_type == 'connect'): 
    ser.write('2c192.168.51.25:20002tls,client\r')
    time.sleep(5)
    if (line == 'CDC_ACM'):
     time.sleep(60)
  elif (conn_type == 'accept') and (restricted == '0'):
    if interface == 'eth0':
     ser.write('2aeth0:10002tls,server\r')
    elif interface == 'wlan0':
     ser.write('2awlan0:10002tls,server\r')
    print "check listening sockets"
    time.sleep(3)
    sock2.connect((remote_ip,tunport2))
  elif (conn_type == 'accept') and (restricted == '1'):
    if interface == 'eth0':
     ser.write('2aeth0:10002tls,server\r')
    elif interface == 'wlan0':
     ser.write('2awlan0:10002tls,server\r')
    print "check listening sockets"
    time.sleep(3)
    sock2.connect((remote_ip,tunport2))
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
    conn2,addr = sock2.accept()
    print 'connected by',addr
    print "sending"
    print "waiting for receiving event/data"
    ser.write('W2r\r')
    time.sleep(5)
    print "send data"
    conn2.send('abcde')
   #ser.write('W1r\r')
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
  if (conn_type == 'connect'):
    recdata = conn2.recv(100)
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
    conn2.send('abcd')
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
    recdata = conn2.recv(100)
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

  print "Test mux instance 3"
  sock3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  if conn_type == 'connect':
   print "start listener"
   sock3.bind((remote_ip,4003))
   sock3.listen(1)

  print 'test case 1: mux receive'
  print "connect to remote host"
  if (conn_type == 'connect'): 
    ser.write('3c192.168.51.25:20003tls,client\r')
    time.sleep(5)
    if (line == 'CDC_ACM'):
     time.sleep(60)
  elif (conn_type == 'accept') and (restricted == '0'):
    if interface == 'eth0':
     ser.write('3aeth0:10003tls,server\r')
    elif interface == 'wlan0':
     ser.write('3awlan0:10003tls,server\r')
    print "check listening sockets"
    time.sleep(3)
    sock3.connect((remote_ip,tunport3))
  elif (conn_type == 'accept') and (restricted == '1'):
    if interface == 'eth0':
     ser.write('3aeth0:10003tls,server\r')
    elif interface == 'wlan0':
     ser.write('3awlan0:10003tls,server\r')
    print "check listening sockets"
    time.sleep(3)
    sock3.connect((remote_ip,tunport3))
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
    conn3,addr = sock3.accept()
    print 'connected by',addr
    print "sending"
    print "waiting for receiving event/data"
    ser.write('W3r\r')
    time.sleep(5)
    print "send data"
    conn3.send('abcde')
   #ser.write('W1r\r')
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
    recdata = conn3.recv(100)
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
    conn3.send('abcd')
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
    recdata = conn3.recv(100)
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
   print "start listener"
   sock4.bind((remote_ip,4004))
   sock4.listen(1)
  
  print 'test case 1: mux receive'
  print "connect to remote host"
  if (conn_type == 'connect'): 
    ser.write('4c192.168.51.25:20004tls,client\r')
    time.sleep(5)
    if (line == 'CDC_ACM'):
     time.sleep(60)
  elif (conn_type == 'accept') and (restricted == '0'):
    if interface == 'eth0':
     ser.write('4aeth0:10004tls,server\r')
    elif interface == 'wlan0':
     ser.write('4awlan0:10004tls,server\r')
    print "check listening sockets"
    time.sleep(3)
    sock4.connect((remote_ip,tunport4))
  elif (conn_type == 'accept') and (restricted == '1'):
    if interface == 'eth0':
     ser.write('4aeth0:10004tls,server\r')
    elif interface == 'wlan0':
     ser.write('4awlan0:10004tls,server\r')
    print "check listening sockets"
    time.sleep(3)
    sock4.connect((remote_ip,tunport4))
  print "verify connection"
  ser.write("4\r")
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
    conn4,addr = sock4.accept()
    print 'connected by',addr
    print "sending"
    print "waiting for receiving event/data"
    ser.write('W4r\r')
    time.sleep(5)
    print "send data"
    conn4.send('abcde')
   #ser.write('W1r\r')
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
    recdata = conn4.recv(100)
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
    conn4.send('abcd')
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
  if (conn_type == 'connect'):
    recdata = conn4.recv(100)
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
     sendbinary_result = 0

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
  else:
   print "mux receive test case instance 4 failed"
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
  

  if end1 == 0 and end2 == 0 and end3 == 0 and end4 == 0:
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
  clientid.sendline('authtype digest')
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
  clientid.sendline('line {0}'.format(line))
  clientid.expect('config Line {0}'.format(line))
  if (line == '1') or (line == '2'):
   clientid.sendline('baud rate {0}'.format(baudrate))
   clientid.expect('config Line {0}'.format(line))
   clientid.sendline('data bits {0}'.format(databits))
   clientid.expect('config Line {0}'.format(line))
   clientid.sendline('parity {0}'.format(parity))
   clientid.expect('config Line {0}'.format(line))
   clientid.sendline('stop bits {0}'.format(stopbits))
   clientid.expect('config Line {0}'.format(line))
   if line == '1':
    clientid.sendline('flow control hardware\r')
   elif line == '2':
    clientid.sendline('flow control software\r')
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
  print "end of device configuration"
  print "testing mux"
  if (protocol == 'tls'):
   result = mux_tls()
   print "result is", result
   if result == 1:
    print "TCP MUX TLS TEST CASE PASSED"
   else:
    print "TCP MUX TLS TEST CASE FAILED"

# main program
device_config(tunnel_port)

sys.exit()

