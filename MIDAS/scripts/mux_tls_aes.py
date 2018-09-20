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
import ftplib

print "Test MUX_TLS MUX_TCP_AES"
print "========="

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>" + " <serial_port>" + "<tunnel_port>" + " <vut_ip>" + " <vut_serial_port>" + " <conn_type>" + " <protocol>")

if len(sys.argv) < 7:
    script_usage()
    sys.exit()
     
device_ip = sys.argv[1]          #xpico240 ip address
serial_port = sys.argv[2]        #xpico240 serial port
tunnel_port = sys.argv[3]        #tunnel port
vut_ip = sys.argv[4]             #must be eds4100
vut_serial_port = sys.argv[5]    #eds4100 serial port
conn_type = sys.argv[6]          #accept or connect
protocol = sys.argv[7]           # tls or tcp aes

script_path = "/home/lantronix/MIDAS/xml/"
def reboot():
 print "reboot device"
 pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")
 time.sleep(40)
 

#eds4100 accept mode settings both tcp_aes and tls
def ftp():
 print "upload xml in file system"
 
 tcpaes_accept = ""+script_path+"tunnel_tcpaes_accept_host.xml"
 tcpaes_connect = ""+script_path+"tunnel_tcpaes_connect_host.xml"
 tls_accept = ""+script_path+"tunnel_tls_accept_host.xml"
 tls_connect = ""+script_path+"tunnel_tls_connect_host.xml"
 ftp = ftplib.FTP("192.168.51.55")
 ftp.login("admin", "PASS")
 time.sleep(5)
 if protocol == 'tcp aes' and conn_type == 'connect':   
  ftp.storbinary("STOR " + tcpaes_accept, open(tcpaes_accept, 'rb'))
  time.sleep(3)
  print "tcp aes accept xml uploaded"
 elif protocol == 'tcp aes' and conn_type == 'accept':
  print "upload xml file",tcpaes_connect
  ftp.storbinary("STOR " + tcpaes_connect, open(tcpaes_connect, 'rb'))
  time.sleep(3)
  print "tcp aes connect xml uploaded"
 elif protocol == 'tls' and conn_type == 'connect':
  ftp.storbinary("STOR " + tls_accept, open(tls_accept, 'rb'))
  time.sleep(3)
  print "tls accept xml uploaded"
 elif protocol == 'tls' and conn_type == 'accept':
  ftp.storbinary("STOR " + tls_connect, open(tls_connect, 'rb'))
  time.sleep(3)
  print "tls accept xml uploaded"
 ftp.quit()
 ftp.close()
 print "ftp closed"


def vut_tls_xml():
   print "uploading eds4100 accept mode settings:"
   clientid = pexpect.spawn('telnet '+vut_ip)
   clientid.sendline('\r')
   clientid.sendline('\r')
   time.sleep(3)
   clientid.sendline('enable\r')
   clientid.expect('enable')
   clientid.sendline('xml\r')
   clientid.expect('xml')
   if (conn_type == 'connect') and protocol == 'tls':
    clientid.sendline('xcr import tunnel_tls_accept_host.xml\r')
    print "here"
   elif conn_type == 'accept' and protocol == 'tls':
    clientid.sendline('xcr import tunnel_tls_connect_host.xml\r')
   clientid.expect('xml')
   clientid.sendline('write\r')
   clientid.expect('xml')
   clientid.sendline('exit\r')
   clientid.expect('enable')
   clientid.sendline('exit\r')
   print "xml import successfully and telnet was closed",conn_type, protocol
   
def vut_tcpaes_xml():
   clientid = pexpect.spawn('telnet '+vut_ip)
   clientid.sendline('\r')
   clientid.sendline('\r')
   time.sleep(3)
   clientid.sendline('enable\r')
   clientid.expect('enable')
   clientid.sendline('xml\r')
   clientid.expect('xml')
   if conn_type == 'connect' and protocol == 'tcp aes':
     clientid.sendline('xcr import tunnel_tcpaes_accept_host.xml\r')
   elif conn_type == 'accept' and protocol == 'tcp aes':
     clientid.sendline('xcr import tunnel_tcpaes_connect_host.xml\r')
   clientid.expect('xml')
   clientid.sendline('write\r')
   clientid.expect('xml')
   clientid.sendline('exit\r')
   clientid.expect('enable')
   clientid.sendline('exit\r')
   print "print xml import successfully and telnet was closed",conn_type, protocol

def uut_tls():
  print "Configuring xpico240"
  print "xpico240:uploading tls certificates"
  tls = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+script_path+"mux_tls.xml")
  time.sleep(10)
  print "tls xml imported successfully"
  #mux_tls() 

def uut_tcp_aes(): 
  print "Configuring xpico240"
  print "xpico240:uploading tcp_aes credentials"
  mux_tcp_aes = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+script_path+"mux_tcp_aes.xml")
  time.sleep(10)
  print "tls xml imported successfully" + str(mux_tcp_aes)
 
def mux_tls():
 reboot()
 print "test mux tls"
 print "connect and accept mux commands tests begin"
 ser1 = serial.Serial(serial_port,115200)
 ser2 = serial.Serial(vut_serial_port,9600)
 childid = pexpect.fdpexpect.fdspawn(ser1)
 ser1.close()
 ser1.open()
 ser2.close()
 ser2.open()
 time.sleep(5)
 if ser1.isOpen() and ser2.isOpen():
  print ('serial opened')
  ser1.flushInput()
  ser1.flushOutput()
  ser2.flushInput()
  ser2.flushOutput()
  time.sleep(10)
  print 'test case 1: mux receive'
  print "connect to remote host"
  if (conn_type == 'connect'): 
    ser1.write('1c192.168.51.55:10001tls,test\r')
    time.sleep(5)
    print "connect mux commands test started"
  else:
    ser1.write('1aeth0:10002tls,test\r')
    #time.sleep(5)
    print "accept mux commands test started"

    print "verify connection"
    ser1.write("1\r")
    time.sleep(10)
    print "checking data K received or not"
    time.sleep(5)
  out = childid.expect(['K'])
  print "out value: " + str(out)
  time.sleep(2)
#checking connection established or not
  if (out == 0):
    print "connection established. received K"
    
  else:
    print "failed to establish the connection"
  ser1.close()
  ser2.close()
  result = data_test()
  print "tcp aes result checking:::::", result
 return result


def mux_tcp_aes():
 reboot()
 print "connect and accept mux commands tests begin"
 ser1 = serial.Serial(serial_port,115200)
 ser2 = serial.Serial(vut_serial_port,9600)
 childid = pexpect.fdpexpect.fdspawn(ser1)
 ser1.close()
 ser1.open()
 ser2.close()
 ser2.open()
 time.sleep(5)

 if ser1.isOpen() and ser2.isOpen():
  print ('serial opened')
  ser1.flushInput()
  ser1.flushOutput()
  ser2.flushInput()
  ser2.flushOutput()
  time.sleep(10)
  print 'test case 1: mux receive'
  print "connect to remote host"
  if (conn_type == 'connect'):
    print "connect tcp aes" 
    ser1.write('1c192.168.51.55:10001tcp aes,test\r')
    time.sleep(5)
    print "connect mux commands test started"
  else:
    ser1.write('1aeth0:10002tcp aes,test\r')
    time.sleep(5)
    print "accept mux commands test started"

    print "verify connection"
    ser1.write("1\r")
    time.sleep(10)
    print "checking data K received or not"
    time.sleep(3)
  out = childid.expect(['K'])
  print "out value: " + str(out)
  time.sleep(2)
#checking connection established or not
  if (out == 0):
    print "connection established. received K"
    
  else:
    print "failed to establish the connection"
  result = data_test()
  print "tcp aes result checking:::::", result
 return result
 

#sending send and push hex data
def data_test():
 ser1 = serial.Serial(serial_port,115200)
 ser2 = serial.Serial(vut_serial_port,9600)
 childid = pexpect.fdpexpect.fdspawn(ser1)
 ser1.close()
 time.sleep(2)
 ser1.open()
 ser2.close()
 ser2.open()
 time.sleep(5)
 
 hexsend_result = 0
 sendbinary_result = 0
 readbinary_result = 0
 result = 0
 time.sleep(5)
 if ser1.isOpen() and ser2.isOpen():
  print ('serial opened')
  ser1.flushInput()
  ser1.flushOutput()
  ser2.flushInput()
  ser2.flushOutput    
  print "test case 2: send and push Hex data"
  print "initiate hex data send"
  ser1.write('1sx\r')
  #print "check"
  time.sleep(5)
  print ser1.read()
  out1 = childid.expect(['K'])
  print "out1 value: " + str(out1)
   #time.sleep(3)
  if (out1 == 0):
    print "hex data send initiated"
    
  else:
    print "failed to initiate hex data send"

  print "send data"
  ser1.write('313233\r')
  time.sleep(3)
  out2 = childid.expect(['K'])
  time.sleep(3)
  print "out2 value: " + str(out2)
  if (out2 == 0):
    print "data sent"
  else:
    print "failed to send data"

  print "push data from mux and verify remote host receives data"
  ser1.write('1p\r')
  time.sleep(2)
  out3 = childid.expect(['K'])
  print "out3 value: " + str(out3)
  if (out3 == 0):
    print "data received"
  else:
    print "failed to receive data"
  if (out1 == 0) and (out2 == 0) and (out3 == 0):
    print "test case: hex data send passed"
    hexsend_result = 1
  else:
    print "test case: hex data send failed"	

  
  ###############################################

  print "test case 3: read binary data"
  ser1.write('1rb.80\r')
  time.sleep(3)
  out4 = childid.expect(['K'])
  time.sleep(3)
  if (out4 == 0):
    print "binary data read initiated"
  else:
    print "unable to read binary data"
  time.sleep(5)
  ser2.write('abcd')
  #serdata = ser2.read(20)
  time.sleep(4)
  #print "data read from serial is", serdata
  out5 = childid.expect(['abcd'])
  time.sleep(3)
  if (out5 == 0):
    print "got data from EDS4100"
  else:
    print "unable to get data from EDS4100"
  if (out4 == 0) and (out5 == 0):
    print "test case: binary data receive passed"
    readbinary_result = 1
  else:
    print "failed to receive binary data"

###############################################

  print "test case 4: send binary data"
  ser1.write('1sb.\r')
  time.sleep(3)
  out6 = childid.expect(['K'])
  time.sleep(1)
  if (out6 == 0):
   print "binary data send initiated"
  else:
   print "unable to intiated binary data"
  ser1.write('12345678.\r')
  time.sleep(4)
  out7 = childid.expect(['K'])
  time.sleep(1)
  if (out7 == 0):
    print "data sent"
  else:
    print "unable to send data"
  print "push the data"
  ser1.write('1p\r')
  time.sleep(2)
  out8 = childid.expect(['K'])
  time.sleep(1)
  if (out8 == 0):
    print "pushed the data"
   
  else:
    print "push data failed"
  
###############################################

  print "test case 5: end the connection"
  ser1.write('1e\r')
  time.sleep(2)
  ser1.write('1\r')
  time.sleep(2)
  out9 = childid.expect(['D'])
  if (out9 == 0):
    print "connection ended"
  else:
    print "failed to end connection" 
  
  if (out6 == 0) and (out7 == 0) and (out8 == 0) and (out9 == 0):
     print "test case: send binary passed"
     sendbinary_result = 1
  else:
     print "failed to send binary data"

  
  print "hexsend_result is", hexsend_result
  print "sendbinary_result is", sendbinary_result
  print "readbinary_result is", readbinary_result
   
  if (hexsend_result == 1) and (sendbinary_result == 1)and (readbinary_result == 1):
   result = 1
  ser1.close()
  return result

def device_config(port):

  print "configure device"
  
  clientid = pexpect.spawn('telnet '+device_ip)
  clientid.expect('>')
  clientid.sendline('config\r')
  clientid.expect('config')
  clientid.sendline('line host_cdc_acm\r')
  #clientid.expect('config Line 1')
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
  print "testing tls and tcp aes mux"
  ftp()
  vut_tcpaes_xml()
  vut_tls_xml()
    
  if (protocol == 'tls'):
   uut_tls()
   print "xpico240 ready to send tls commands:"
   #result1 = mux_tcp_aes()
   result1 = mux_tls()
   print "mux tls result is", result1
  else:
   uut_tcp_aes()
   print "xpico240 ready to send tcp_aes commands:"
   result1 = mux_tcp_aes()
   print "mux tcp aes result is", result1
  
  if result1 == 1:
   print "MUX TEST CASE PASSED"
  else:
   print "test case mux failed"

# main program

device_config(tunnel_port)

sys.exit()


