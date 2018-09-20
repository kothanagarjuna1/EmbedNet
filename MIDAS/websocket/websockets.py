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

print "Test Web Sockets" 
print "================"

#syntax

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <serial_port>"  + " <device_ip>" + " <tunnel_port>" +  " <line>" + " <remote pc/vut>" + " <conn_type>" + " <protocol>" + "<restricted>" + " <interface>" + "<hardware>" + " <instance>"  + "<secure flag>")
 return

if len(sys.argv) < 12:
    script_usage()
    sys.exit()

serial_port = sys.argv[1]
device_ip = sys.argv[2]
tunnel_port = sys.argv[3]
line = sys.argv[4]
remote_ip = sys.argv[5] #must be linux pc
conn_type = sys.argv[6]
protocol = sys.argv[7] # tcp or udp
restricted = sys.argv[8] # values 1 or 0
interface = sys.argv[9]
hardware = sys.argv[10]
instance = sys.argv[11]
secure_flag = sys.argv[12]

xml_path = '/home/lantronix/MIDAS/'
secure_flag = int(secure_flag)
print secure_flag

def webSockets():

 if secure_flag == 0:
   print "test websocket secure disable"
 elif secure_flag == 1:
   print "test websocket secure enable"

 print "Start echo server"
 if secure_flag == 0:
  cmd1 = 'python SimpleExampleServer_8001.py'
 elif secure_flag == 1:
  cmd1 = 'python SimpleExampleServer_8001.py --example echo --ssl 1 --cert ./cert.pem'
 p1 = subprocess.Popen("exec " + cmd1, stdout=subprocess.PIPE, shell=True)
 time.sleep(2)
 
 if secure_flag == 0:
  cmd2 = 'python SimpleExampleServer_8002.py'
 elif secure_flag == 1:
  cmd2 = 'python SimpleExampleServer_8002.py --example echo --ssl 1 --cert ./cert.pem'
 p2 = subprocess.Popen("exec " + cmd2, stdout=subprocess.PIPE, shell=True)
 time.sleep(2)
 
 if secure_flag == 0:
  cmd3 = 'python SimpleExampleServer_8003.py'
 elif secure_flag == 1:
  cmd3 = 'python SimpleExampleServer_8003.py --example echo --ssl 1 --cert ./cert.pem'
 p3 = subprocess.Popen("exec " + cmd3, stdout=subprocess.PIPE, shell=True)
 time.sleep(2)
 
 if secure_flag == 0:
  cmd4 = 'python SimpleExampleServer_8004.py'
 elif secure_flag == 1:
  cmd4 = 'python SimpleExampleServer_8004.py --example echo --ssl 1 --cert ./cert.pem'
 p4 = subprocess.Popen("exec " + cmd4, stdout=subprocess.PIPE, shell=True)
 time.sleep(2)

 if secure_flag == 0: 
  cmd5 = 'python SimpleExampleServer_8005.py'
 elif secure_flag == 1:
  cmd5 = 'python SimpleExampleServer_8005.py --example chat --ssl 1 --cert ./cert.pem'
 p5 = subprocess.Popen("exec " + cmd5, stdout=subprocess.PIPE, shell=True)
 time.sleep(2)

 if secure_flag == 0:
  cmd6 = 'python SimpleExampleServer_8006.py'
 elif secure_flag == 1:
  cmd6 = 'python SimpleExampleServer_8006.py --example chat --ssl 1 --cert ./cert_echo.pem'
 p6 = subprocess.Popen("exec " + cmd6, stdout=subprocess.PIPE, shell=True)
 time.sleep(2)

 if secure_flag == 0:
  cmd7 = 'python SimpleExampleServer_8007.py'
 elif secure_flag == 1:
  cmd7 = 'python SimpleExampleServer.py_8007 --example chat --ssl 1 --cert ./cert_echo.pem'
 p7 = subprocess.Popen("exec " + cmd7, stdout=subprocess.PIPE, shell=True)
 time.sleep(2)

 if secure_flag == 0:
  cmd8 = 'python SimpleExampleServer_8008.py'
 elif secure_flag == 1:
  cmd8 = 'python SimpleExampleServer.py_8008 --example chat --ssl 1 --cert ./cert_echo.pem'
 p8 = subprocess.Popen("exec " + cmd8, stdout=subprocess.PIPE, shell=True)
 time.sleep(2)
 

 if (line == '1'):
  ser = serial.Serial(serial_port,rtscts = True)
 elif line == '2':
  ser = serial.Serial(serial_port,xonxoff=True)
 elif line == 'cdc_acm':
  ser = serial.Serial(serial_port)
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

 tc = 0 
 print "Test Mux instance 1"
 try:
  if ser.isOpen():
   print "serial opened"
   ser.flushInput()
   ser.flushOutput()
   time.sleep(4)
   #print "connect to remote host"
   if (conn_type == 'connect') and protocol == 'tcp': 
    ser.write('1c'+remote_ip+':8001websocket,wb\r')
   time.sleep(5)
   if (conn_type == 'accept') and (restricted == '0'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('1aeth0:10001tcp\r')
     elif protocol == 'tcp aes':
      ser.write('1aeth0:10001tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('1awlan0:10001tcp\r')
     elif protocol == 'tcp aes':
      ser.write('1awlan0:10001tcp aes,aes\r')
    time.sleep(15)
    if protocol == 'tcp':
     sock.connect((device_ip, tunport1))
    elif protocol == 'tcp aes':
     sock.connect(('172.19.245.7',10001))
   elif (conn_type == 'accept') and (restricted == '1'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('1aeth0:10001tcp\r')
     elif protocol == 'tcp aes':
      ser.write('1aeth0:10001tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('1awlan0:10001tcp\r')
     elif protocol == 'tcp aes':
      ser.write('1awlan0:10001tcp aes,aes\r')
    #print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
     sock.connect((device_ip, tunport1))
    elif protocol == 'tcp aes':
     sock.connect(('172.19.245.7',10001))
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
   ser.write('1rb.10\r')
   time.sleep(5)
   recdata = childid.expect('123')
   print recdata
   if (recdata == 0):
    print "data received", recdata
    print "test case: hex data send passed"
    tc = 1
   else:
    print "failed to receive data"
    print "test case: hex data send failed"
 
###############################################

   print "test case : send binary data and end the connection"
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
   ser.write('1rb.20\r')
   time.sleep(5)
   if (conn_type == 'connect'):
     recdata = childid.expect('12345678')
   elif (conn_type == 'accept'):
     recdata = sock.recv(100)
     time.sleep(2)
   print "data received", recdata
   
   if recdata == 0:
     print "test case: send binary passed"
     tc = 1
   else:
     print "failed to send binary data"

 
  if tc == 0:
   print "mux instance 1 test case failed"
  else:
   print "mux instance 1 test case passed"

  print "Test instance 2"
  sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  if conn_type == 'connect':
   if protocol == 'tcp':
    print "start listener"
    sock2.bind((remote_ip,4002))
    sock2.listen(1)

  print "connect to remote host"
  if (conn_type == 'connect'): 
   if protocol == 'tcp':
    ser.write('2c'+remote_ip+':8002websocket,wb\r')
   time.sleep(5)
  elif (conn_type == 'accept') and (restricted == '0'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('2aeth0:10002tcp\r')
     elif protocol == 'tcp aes':
      print "instance 2 tcp aes"
      ser.write('2aeth0:10002tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('2awlan0:10002tcp\r')
     elif protocol == 'tcp aes':
      ser.write('2awlan0:10002tcp aes,aes\r')
    print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
     sock2.connect((device_ip, tunport2))
    elif protocol == 'tcp aes':
     sock2.connect(('172.19.245.7',10002))
  elif (conn_type == 'accept') and (restricted == '1'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('2aeth0:10002tcp\r')
     elif protocol == 'tcp aes':
      print "instance 2 tcp aes"
      ser.write('2aeth0:10002tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('2awlan0:10002tcp\r')
     elif protocol == 'tcp aes':
      ser.write('2awlan0:10002tcp aes,aes\r')
    print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
     sock2.connect((device_ip, tunport2))
    elif protocol == 'tcp aes':
     print "connect to 10002"
     sock2.connect(('172.19.245.7',10002))
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
  
  print "test case : send and push Hex data"
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
  ser.write('2rb.10\r')
  time.sleep(5)
  recdata = childid.expect('123')
  print recdata
  if (recdata == 0):
    print "data received", recdata
    tc = 1
  else:
    print "failed to receive data"
 
###############################################


  print "test case : send binary data and end the connection"
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
  ser.write('2rb.20\r')
  time.sleep(5)
  recdata = childid.expect('12345678')

  if (recdata == 0):
     print "test case: send binary passed"
     tc = 1
  else:
     print "failed to send binary data"

  if tc == 0:
   print "mux instance 2 failed"
  else:
   print "mux instance 2 passed"

  print "Test mux instance 3"
  if conn_type == 'connect':
   ser.write('3c'+remote_ip+':8003websocket,wb\r')
   time.sleep(5)
  elif (conn_type == 'accept') and (restricted == '0'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('3eth0:10003tcp\r')
     elif protocol == 'tcp aes':
      ser.write('3aeth0:10003tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('3awlan0:10003tcp\r')
     elif protocol == 'tcp aes':
      ser.write('3awlan0:10003tcp aes,aes\r')
    #print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
     sock3.connect((device_ip, tunport3))
    elif protocol == 'tcp aes':
     sock3.connect(('172.19.245.7',10003))
  elif (conn_type == 'accept') and (restricted == '1'):
   if interface == 'eth0':
    if protocol == 'tcp':
      ser.write('3eth0:10003tcp\r')
      print "check"
      time.sleep(10)
    elif protocol == 'tcp aes':
      ser.write('3aeth0:10003tcp aes,aes\r')
   elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('3awlan0:10003tcp\r')
     elif protocol == 'tcp aes':
      ser.write('3awlan0:10003tcp aes,aes\r')
   print "check listening sockets"
   time.sleep(15)
   if protocol == 'tcp':
     sock3.connect((device_ip, tunport3))
   elif protocol == 'tcp aes':
      sock3.connect(('172.19.245.7',10003))
  print "verify connection"
  ser.write("3\r")
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
  
  print "test case 2: send and push Hex data"
  print "initiate hex data send"
  ser.write('3sx\r')
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
  ser.write('3rb.10\r')
  time.sleep(5)
  recdata = childid.expect('123')
  if (recdata == 0):
    print "data received", recdata
    print "test case: hex data send passed"
    tc = 1
  else:
    print "test case: hex data send failed"
 
  print "test case : send binary data and end the connection"
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
  ser.write('3rb.20\r')
  time.sleep(5)
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    recdata = childid.expect('12345678')
  elif (conn_type == 'accept'):
     recdata = sock3.recv(100)
     time.sleep(2)

  if recdata == 0:
     print "test case: send binary passed"
     tc = 1
  else:
     print "failed to send binary data"

  if tc == 0:
   print "mux instance 3 failed"
  else:
   print "mux instance 3 passed"
  

  print "Test instance 4"
  sock4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  if conn_type == 'connect':
   if protocol == 'tcp':
    print "start listener"
    sock4.bind((remote_ip,4004))
    sock4.listen(1)
  
  print "connect to remote host"
  if (conn_type == 'connect'):
   if protocol == 'tcp': 
    ser.write('4c'+remote_ip+':8004websocket,wb\r')
   time.sleep(5)
  elif (conn_type == 'accept') and (restricted == '0'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('4aeth0:10004tcp\r')
     elif protocol == 'tcp aes':
      ser.write('4aeth0:10004tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('4awlan0:10004tcp\r')
     elif protocol == 'tcp aes':
      ser.write('4awlan0:10004tcp aes,aes\r')
    print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
     sock4.connect((device_ip, tunport4))
    elif protocol == 'tcp aes':
     sock4.connect(('172.19.245.7',10004))
  elif (conn_type == 'accept') and (restricted == '1'):
    if interface == 'eth0':
     if protocol == 'tcp':
      ser.write('4aeth0:10004tcp\r')
     elif protocol == 'tcp aes':
      ser.write('4aeth0:10004tcp aes,aes\r')
    elif interface == 'wlan0':
     if protocol == 'tcp':
      ser.write('4awlan0:10004tcp\r')
     elif protocol == 'tcp aes':
      ser.write('4awlan0:10004tcp aes,aes\r')
    print "check listening sockets"
    time.sleep(15)
    if protocol == 'tcp':
      sock4.connect((device_ip, tunport4))
    elif protocol == 'tcp aes':
      sock4.connect(('172.19.245.7',10004))
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
  ser.write('4rb.10\r')
  time.sleep(5)
  if (conn_type == 'connect'):
     recdata = childid.expect('123')
     time.sleep(3)
  elif (conn_type == 'accept'):
    recdata = sock4.recv(100)
    time.sleep(3)
    print recdata
  if (recdata == 0):
    print "data received", recdata
    tc = 1
  else:
    print "failed to receive data"
  if recdata == 0:  
    print "test case: hex data send passed"
    tc = 1
  else:
    print "test case: hex data send failed"
 

  print "test case : send binary data and end the connection"
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
  ser.write('4rb.20\r')
  time.sleep(4)
  if (conn_type == 'connect'):
   if protocol == 'tcp':
    recdata = childid.expect('12345678')
  elif (conn_type == 'accept'):
     recdata = sock4.recv(100)
     time.sleep(2)
  print "data received", recdata

  if recdata == 0:
     print "test case: send binary passed"
     tc = 1
  else:
     print "failed to send binary data"

 
  if instance == '8' and secure_flag == 0:
   print "Test instance 5"
   sock5 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   if conn_type == 'connect':
    if protocol == 'tcp':
     print "start listener"
     sock5.bind((remote_ip,4005))
     sock5.listen(1)
  
   if (conn_type == 'connect'): 
    if protocol == 'tcp':
     ser.write('5c'+remote_ip+':8005websocket,wb\r')
    time.sleep(8)
   elif (conn_type == 'accept') and (restricted == '0'):
     if interface == 'eth0':
      if protocol == 'tcp':
       ser.write('5awlan0:10005tcp\r')
     elif interface == 'wlan0':
      if protocol == 'tcp':
       ser.write('5awlan0:10005tcp\r')
      elif protocol == 'tcp aes':
       ser.write('5awlan0:10005tcp aes,aes\r')
     print "check listening sockets"
     time.sleep(15)
     if protocol == 'tcp':
      sock5.connect((device_ip, tunport5))
     elif protocol == 'tcp aes':
      sock5.connect(('172.19.245.7',10005))
   elif (conn_type == 'accept') and (restricted == '1'):
     if interface == 'eth0':
      if protocol == 'tcp':
       ser.write('5aeth0:10005tcp\r')
      elif protocol == 'tcp aes':
       ser.write('5aeth0:10005tcp aes,aes\r')
     elif interface == 'wlan0':
      if protocol == 'tcp':
       ser.write('5awlan0:10005tcp\r')
      elif protocol == 'tcp aes':
       ser.write('5awlan0:10005tcp aes,aes\r')
     print "check listening sockets"
     time.sleep(15)
     if protocol == 'tcp':
      sock5.connect((device_ip, tunport5))
     elif protocol == 'tcp aes':
      sock5.connect(('172.19.245.7',10005))
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
  
 
   print "test case: send and push Hex data"
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
   ser.write('5rb.20\r')
   if (conn_type == 'connect'):
    if protocol == 'tcp':
     recdata = childid.expect('123')
    time.sleep(3)
    print recdata
   elif (conn_type == 'accept'):
     recdata = sock5.recv(100)
     time.sleep(3)
     print recdata
   if (recdata == 0):
     print "hex data received"
   else:
     print "failed to receive hex data"
 
   print "test case: send binary data and end the connection"
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
   ser.write('5rb.20\r')
   time.sleep(5)
   if (conn_type == 'connect'):
    if protocol == 'tcp':
      recdata = childid.expect('12345678')
    time.sleep(2)
   elif (conn_type == 'accept'):
      recdata = sock5.recv(100)
      time.sleep(2)
   print "data received", recdata

   if recdata == 0:
      print "test case: send binary passed"
      tc = 1
   else:
      print "test case: send bindary failed"

   if tc == 0:
    print "mux instance 5 test case failed"
   else:
    print "mux instance 5 test case passed"
 

   print "Test instance 6"
   sock6 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   if conn_type == 'connect':
    if protocol == 'tcp':
     print "start listener"
     sock6.bind((remote_ip,4006))
     sock6.listen(1)
  
   print "connect to remote host"
   if (conn_type == 'connect'):
    if protocol == 'tcp': 
     ser.write('6c'+remote_ip+':8006websocket,wb\r')
    time.sleep(8)
   elif (conn_type == 'accept') and (restricted == '0'):
     if interface == 'eth0':
      if protocol == 'tcp':
       ser.write('6aeth0:10006tcp\r')
      elif protocol == 'tcp aes':
       ser.write('6aeth0:10006tcp aes,aes\r')
     elif interface == 'wlan0':
      if protocol == 'tcp':
       ser.write('6awlan0:10006tcp\r')
      elif protocol == 'tcp aes':
       ser.write('6awlan0:10006tcp aes,aes\r')
     print "check listening sockets"
     time.sleep(15)
     if protocol == 'tcp':
      sock6.connect((device_ip, tunport6))
     elif protocol == 'tcp aes':
      sock6.connect(('172.19.245.7',10006))
   elif (conn_type == 'accept') and (restricted == '1'):
     if interface == 'eth0':
      if protocol == 'tcp':
       ser.write('6aeth0:10006tcp\r')
      elif protocol == 'tcp aes':
       ser.write('6aeth0:10006tcp aes,aes\r')
     elif interface == 'wlan0':
      if protocol == 'tcp':
       ser.write('6awlan0:10006tcp\r')
      elif protocol == 'tcp aes':
       ser.write('6awlan0:10006tcp aes,aes\r')
     print "check listening sockets"
     time.sleep(15)
     if protocol == 'tcp':
      sock6.connect((device_ip, tunport6))
     elif protocol == 'tcp aes':
      sock6.connect(('172.19.245.7',10006))
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
   ser.write('6rb.20\r')
   time.sleep(5)
   if (conn_type == 'connect'):
    if protocol == 'tcp':
     recdata = childid.expect('123')
    time.sleep(3)
    print recdata
   elif (conn_type == 'accept'):
     recdata = sock6.recv(100)
     time.sleep(3)
     print recdata
   if (recdata == 0):
     print "test case: hex data send passed"
     tc = 1
   else:
     print "test case: hex data send failed"
  

   print "test case : send binary data and end the connection"
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
   ser.write('6rb.20\r')
   time.sleep(5)
   if (conn_type == 'connect'):
    if protocol == 'tcp':
     recdata = childid.expect('12345678')
    time.sleep(2)
   elif (conn_type == 'accept'):
      recdata = sock6.recv(100)
      time.sleep(2)
   print "data received", recdata

   if recdata == 0:
      print "test case: send binary passed"
      tc = 1
   else:
      print "failed to send binary data"

   if tc == 0:
    print "mux instance 6 failed"
   else:
    print "mux instance 6 passed"


  
   print "Test instance 7"
   sock7 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   if conn_type == 'connect':
    if protocol == 'tcp':
     print "start listener"
     sock7.bind((remote_ip,4007))
     sock7.listen(1)
    elif protocol == 'tcp aes':
     sock7.connect(('172.19.245.7',10007))
  
   if (conn_type == 'connect'):
    if protocol == 'tcp': 
     ser.write('7c'+remote_ip+':8007websocket,wb\r')
    elif protocol == 'tcp aes':
     ser.write('7c'+remote_ip+':10007tcp aes,aes\r')
     time.sleep(5)
     if (line == 'CDC_ACM'):
      time.sleep(60)
   elif (conn_type == 'accept') and (restricted == '0'):
     if interface == 'eth0':
      if protocol == 'tcp':
       ser.write('7aeth0:10007tcp\r')
      elif protocol == 'tcp aes':
       ser.write('7aeth0:10007tcp aes,aes\r')
     elif interface == 'wlan0':
      if protocol == 'tcp':
       ser.write('7awlan0:10007tcp\r')
      elif protocol == 'tcp aes':
       ser.write('7awlan0:10007tcp aes,aes\r')
     print "check listening sockets"
     time.sleep(15)
     if protocol == 'tcp':
      sock7.connect((device_ip, tunport7))
     elif protocol == 'tcp aes': 
      sock7.connect(('172.19.245.7',10007))
   elif (conn_type == 'accept') and (restricted == '1'):
     if interface == 'eth0':
      if protocol == 'tcp':
       ser.write('7aeth0:10007tcp\r')
      elif protocol == 'tcp aes':
       ser.write('7aeth0:10007tcp aes,aes\r')
     elif interface == 'wlan0':
      if protocol == 'tcp':
       ser.write('7awlan0:10007tcp\r')
      elif protocol == 'tcp aes':
       ser.write('7awlan0:10007tcp aes,aes\r')
     print "check listening sockets"
     time.sleep(15)
     if protocol == 'tcp':
      sock7.connect((device_ip, tunport7))
     elif protocol == 'tcp aes':
      sock7.connect(('172.19.245.7',10007))
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
  
 
   print "test case : send and push Hex data"
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
   ser.write('7rb.20\r')
   time.sleep(5)
   if (conn_type == 'connect'):
    if protocol == 'tcp':
     recdata = childid.expect('123')
    time.sleep(3)
   elif (conn_type == 'accept'):
     recdata = sock7.recv(100)
     time.sleep(3)
     print recdata
   if (recdata == 0):
     print "hex data received", recdata
     tc = 1
   else:
     print "failed to hex receive data"
 

   print "test case : send binary data and end the connection"
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
   ser.write('7rb.20\r')
   if (conn_type == 'connect'):
    if protocol == 'tcp':
     recdata = childid.expect('12345678')
    time.sleep(2)
   elif (conn_type == 'accept'):
      recdata = sock7.recv(100)
      time.sleep(2)
   print "data received", recdata

   if (recdata == 0):
      print "test case: send binary passed"
      tc = 1
   else:
      print "failed to send binary data"

   if tc == 0: 
    print "mux instance 7 failed"
   else:
    print "mux instance 7 passed"
  
##################################################################################

   print "Test instance 8"
   sock8 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   if conn_type == 'connect':
    if protocol == 'tcp':
     print "start listener"
     sock8.bind((remote_ip,4008))
     sock8.listen(1)
  
   if (conn_type == 'connect'): 
    if protocol == 'tcp':
     ser.write('8c'+remote_ip+':8008websocket,wb\r')
    elif protocol == 'tcp aes':
     ser.write('8c'+remote_ip+':10008tcp aes,aes\r')
    time.sleep(5)
   elif (conn_type == 'accept') and (restricted == '0'):
     if interface == 'eth0':
      if protocol == 'tcp':
       ser.write('8aeth0:10008tcp\r')
      elif protocol == 'tcp aes':
       ser.write('8aeth0:10008tcp aes,aes\r')
     elif interface == 'wlan0':
      if protocol == 'tcp':
       ser.write('8awlan0:10008tcp\r')
      elif protocol == 'tcp aes':
       ser.write('8awlan0:10008tcp aes,aes\r')
     print "check listening sockets"
     time.sleep(15)
     if protocol == 'tcp':
      sock8.connect((device_ip, tunport8))
     elif protocol == 'tcp aes':
      sock8.connect(('172.19.245.7',10008))
   elif (conn_type == 'accept') and (restricted == '1'):
     if interface == 'eth0':
      if protocol == 'tcp':
       ser.write('8aeth0:10008tcp\r')
      elif protocol == 'tcp aes':
       ser.write('8aeth0:10008tcp aes,aes\r')
     elif interface == 'wlan0':
      if protocol =='tcp':
       ser.write('8awlan0:10008tcp\r')
      elif protocol == 'tcp aes':
       ser.write('8awlan0:10008tcp aes,aes\r')
     print "check listening sockets"
     time.sleep(15)
     if protocol == 'tcp':
      sock8.connect((device_ip, tunport8))
     elif protocol == 'tcp aes': 
      sock8.connect(('172.19.245.7',10008))
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
  

 
   print "test case: send and push Hex data"
   print "initiate hex data send"
   ser.write('8sx\r')
    #print "check"
   time.sleep(3)
   print ser.read()
   out = childid.expect(['K','hello'])
  # time.sleep(3)
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
   ser.write('8rb.20\r')
   time.sleep(5)
   if (conn_type == 'connect'):
    if protocol == 'tcp':
     recdata = childid.expect('123')
    time.sleep(3)
    print recdata
   elif (conn_type == 'accept'):
     recdata = sock8.recv(100)
     time.sleep(3)
     print recdata
   if (recdata == 0):
     print "hex data received"
     tc = 1
   else:
     print "failed to receive hex data"
 
   print "test case : send binary data and end the connection"
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
   ser.write('8rb.20\r')
   if (conn_type == 'connect'): 
    if protocol == 'tcp': 
     recdata = childid.expect('12345678')
    time.sleep(2)
   elif (conn_type == 'accept'):
      recdata = sock8.recv(100)
      time.sleep(2)
   print "data received", recdata
 
   if (recdata == 0):
      print "test case: send binary passed"
      tc = 1
   else:
      print "failed to send binary data"


   if tc == 0:
    print "mux instance 8 failed"
   else:
    print "mux instance 8 passed"


  print "send and read data from different instances"
  ser.write('1sb.\r')
  time.sleep(3)
  ser.write('abcd.\r')
  time.sleep(3)
  ser.write('2sb.\r')
  time.sleep(3)
  ser.write('1234567890.\r')
  time.sleep(3)
  ser.write('3sx\r')
  time.sleep(3)
  ser.write('313232\r')
  time.sleep(3)
 
  print "read data from instance 1 , instance 3" 
  ser.write('1p\r')
  time.sleep(3)
  ser.write('1rb.10\r')
  time.sleep(3)
  inst_1 = childid.expect('abcd')
  ser.write('3p\r')
  time.sleep(3)
  ser.write('3rb.10\r')
  time.sleep(3)
  inst_3 = childid.expect('122')
  print "inst_1",inst_1
  print "inst_3",inst_3

  if secure_flag == 0:
   ser.write('4sx.\r')
   time.sleep(3)
   ser.write('343536.\r')
   time.sleep(3)
   ser.write('6sb.\r')
   time.sleep(3)
   ser.write('1234.\r')
   time.sleep(3)
   ser.write('8sx\r')
   time.sleep(3)
   ser.write('373839\r')
   time.sleep(3)

   print "read data from instance 6, instance 8"
   ser.write('8p\r')
   time.sleep(3)
   ser.write('8rb.10\r')
   time.sleep(3)
   inst_8 = childid.expect('789')
   print "inst_8",inst_8
   ser.write('6p\r')
   time.sleep(3)
   ser.write('6rb.10\r')
   time.sleep(3)
   inst_6 = childid.expect('1234')
   if inst_1 == 0 and inst_3 == 0 and inst_6 == 0 and inst_8 == 0:
    print "instance 1,3,6,8 data read correctly"
    tc = 1
   else:
    print "instance 1,3,6,8 data not read correctly"
  
  elif secure_flag == 1:
   if inst_1 == 0 and inst_3 == 0:
     print "instance 1,3 data read correctly"
     tc = 1
   else:
     print "instance 1,3 data not read correctly"

  print "end connection"
  ser.write('1e\r')
  time.sleep(2)
  end1 = childid.expect(['K','FG'])
  ser.write('2e\r')
  time.sleep(2)
  end2 = childid.expect(['K','FG'])
  ser.write('3e\r')
  time.sleep(3)
  end3 = childid.expect(['K','F'])
  ser.write('4e\r')
  time.sleep(3)
  end4 = childid.expect(['K','F'])
  ser.write('5e\r')
  time.sleep(3)
  if instance == '8':
    ser.write('5e\r')
    time.sleep(3)
    end5 = childid.expect(['K','F'])
    ser.write('6e\r')
    time.sleep(2)
    end6 = childid.expect('K')
    ser.write('7e\r')
    time.sleep(2)
    end7 = childid.expect('K')
    ser.write('8e\r')
    time.sleep(2)
    end8 = childid.expect('K')
  if instance == '8':
     if end1 == 0 and end2 == 0 and end3 == 0 and end4 == 0 and end5 == 0 and end6 == 0 and end7 ==0 and end8 == 0:
      print "connection ended"
  elif instance == '4':
     if end1 == 0 and end2 == 0 and end3 == 0 and end4 == 0:
      tc = 1
     else:
      print "connection did not end" 
      tc = 0


  ser.close()
  sock.close()
  sock2.close()
  #sock3.close()
  sock4.close()
  if instance == '8':
   sock5.close()
   sock6.close()
   sock7.close()
   sock8.close()
  return tc
 except Exception as e:
  print(str(e))


def device_config(port):
  print "import xml to configure web sockets and tls credential"
  x = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"websocket.xml")
  print x
  print "reboot device"
  pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")
  time.sleep(40)
  clientid = pexpect.spawn('telnet '+device_ip)
  clientid.sendline('\r')
  clientid.sendline('\r')
  print "configuring device"
  clientid.sendline('config\r')
  clientid.expect('config')
  clientid.sendline('line {0}'.format(line))
  #clientid.expect('config Line {0}'.format(line))
  if (line == '1') or (line == '2'):
   if line == '1':
    clientid.sendline('flow control hardware\r')
   elif line == '2':
    clientid.sendline('flow control software\r')
   clientid.expect('config Line {0}'.format(line))
  clientid.sendline('protocol mux\r')
  clientid.sendline('exit\r')
  clientid.expect('config')
  if secure_flag == 1:
   print "here"
   clientid.sendline('websocket credential wb\r')
   time.sleep(2)
   clientid.sendline('secure enable\r')
   time.sleep(3)
   clientid.sendline('write\r')
   time.sleep(3)
   clientid.sendline('tls credential websocket\r')
   time.sleep(3)
   clientid.sendline('exit\r')
  clientid.sendline('exit\r')
  clientid.expect('>')
  print "end of device configuration"
  tc_result = webSockets()
  if tc_result == 0:
    print "WebSocket TEST CASE FAILED"
  else:
    print "WebSocket TEST CASE PASSED"
 

# main program
device_config(tunnel_port)

sys.exit()

