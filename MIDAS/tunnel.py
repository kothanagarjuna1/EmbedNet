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
import datetime



def script_usage():
  print("Usage: " + os.path.basename(sys.argv[0]) + " <serial_port>" + " <device_ip>" + "<remote_ip>" + "<connect_type>" + "<baudrate>" + "<databits>" + "<parity>" + "<stopbits>" + "<mode>" + "<protocol>")

if len(sys.argv) < 10:
    script_usage()
    sys.exit()

serial_port = sys.argv[1]
device_ip = sys.argv[2]
remote_ip = sys.argv[3]
connect_type = sys.argv[4]
baudrate = sys.argv[5]
databits = sys.argv[6]
parity = sys.argv[7]
stopbits = sys.argv[8]
mode = sys.argv[9] # always or any character or start character
protocol = sys.argv[10] # tcp,tcpaes tls

TCP_PORT = 6001
TCP_PORT = int(TCP_PORT)

def tcp_listen(): 
  ser = serial.Serial(serial_port, '{0}'.format(baudrate), timeout=0, parity='{0}'.format(parity), stopbits = int('{0}'.format(stopbits)), bytesize = int('{0}'.format(databits)), rtscts = True)
  childid = pexpect.fdpexpect.fdspawn(ser)
  ser.close()
  ser.open()
  time.sleep(5)  
  
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.settimeout(20)  
           
  s.bind((remote_ip, TCP_PORT))
  s.listen(10)

  if ser.isOpen():
    ser.flushInput()
    ser.flushOutput()
    print "serial opened"
    print "Testing TCP"
    if (mode == 'always'):
      print "send data from serial"
      conn, addr = s.accept()
      print 'Connection address:', addr
    
      ser.write('123')
      data = conn.recv(10)
      print data
   
      print "send data from Network"
      conn.send('abc')
      time.sleep(5)
      ser1 = ser.read(10)
      print ser1

      conn.close()
      time.sleep(5)
      ser.close()
      time.sleep(5)
      if (data == '123') and (ser1 == 'abc'):
        print "TEST CASE PASSED"
    
      else:
        print data
        print ser1
        print "TEST CASE FAILED"  

    elif (mode == 'any character'):
      ser.write('123') 
      print "write '123'"
      print "send data from serial"
      conn, addr = s.accept()
      print 'Connection address:', addr
    
      #ser.write('123')
      data = conn.recv(10)
      print data
   
      print "send data from Network"
      conn.send('abc')
      time.sleep(5)
      ser1 = ser.read(10)
      print ser1

      conn.close()
      time.sleep(5)
      ser.close()
      time.sleep(5)  
      if (data == '123') and (ser1 == 'abc'):
        print "TEST CASE PASSED"
    
      else:
        print data
        print ser1
        print "TEST CASE FAILED" 

    else:
      ser.write('\x02') 
      print "write 'B'"
      print "send data from serial"
      conn, addr = s.accept()
      print 'Connection address:', addr
    
      ser.write('123')
      data = conn.recv(10)
      print data
   
      print "send data from Network"
      conn.send('abc')
      time.sleep(5)
      ser1 = ser.read(10)
      print ser1

      conn.close()
      time.sleep(5)
      ser.close()
      time.sleep(5)
      if (data == '123') and (ser1 == 'abc'):
        print "TEST CASE PASSED"
    
      else:
        print data
        print ser1
        print "TEST CASE FAILED" 

def tcp_connect():
  ser = serial.Serial(serial_port, '{0}'.format(baudrate), timeout=0, parity='{0}'.format(parity), stopbits = int('{0}'.format(stopbits)), bytesize = int('{0}'.format(databits)), rtscts = True)
  childid = pexpect.fdpexpect.fdspawn(ser)
  ser.close()
  ser.open()
  time.sleep(5)  
  
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.settimeout(20)        
   

  if ser.isOpen():
    ser.flushInput()
    ser.flushOutput()
    print "serial opened"
    print "Testing TCP"
    if (mode == 'always'):
      
      s.connect((device_ip, 10001))   
      time.sleep(3)
      print "send data from serial"
           
      ser.write('123')
      time.sleep(5)
      data = s.recv(100)
      print data
      
      print "send data from Network"
      s.send('abc')
      time.sleep(5)
      ser1 = ser.read(10)
      print ser1

      s.close()
      time.sleep(5)
      ser.close()
      time.sleep(5)
      if (data == '123') and (ser1 == 'abc'):
        print "TEST CASE PASSED"
    
      else:
        print data
        print ser1
        print "TEST CASE FAILED"    


    elif (mode == 'any character'):
      #s.connect((device_ip, 10001))
      ser.write('123')
      time.sleep(2)        
      print "write '123'"
      s.connect((device_ip, 10001))
      time.sleep(10)
      print "send data from serial"
     
      #ser.write('123')
      data = s.recv(100)
      print data
   
      print "send data from Network"
      s.send('abc')
      time.sleep(5)
      ser1 = ser.read(10)
      print ser1

      #conn.close()
      time.sleep(5)
      ser.close()
      time.sleep(5)
      if (data == '123') and (ser1 == 'abc'):
        print "TEST CASE PASSED"
    
      else:
        print data
        print ser1
        print "TEST CASE FAILED"   

    else:
      
      ser.write('\x02') 
      print "write 'B'" 
      time.sleep(2)     
      s.connect((device_ip, 10001))
      time.sleep(10)    
      ser.write('123')
      data = s.recv(100)
      print data
   
      print "send data from Network"
      s.send('abc')
      time.sleep(5)
      ser1 = ser.read(10)
      print ser1

      #conn.close()
      time.sleep(5)
      ser.close()
      time.sleep(5)
      if (data == '123') and (ser1 == 'abc'):
        print "TEST CASE PASSED"
    
      else:
        print data
        print ser1
        print "TEST CASE FAILED" 

def tls_connect():
  ser = serial.Serial(serial_port, '{0}'.format(baudrate), timeout=0, parity='{0}'.format(parity), stopbits = int('{0}'.format(stopbits)), bytesize = int('{0}'.format(databits)), rtscts = True)
  childid = pexpect.fdpexpect.fdspawn(ser)
  ser.close()
  ser.open()
  time.sleep(5)  
  
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.settimeout(20)  
  os.system("/etc/init.d/stunnel4 restart")         
   

  if ser.isOpen():
    ser.flushInput()
    ser.flushOutput()
    print "serial opened"
    print "Testing TCP"
    if (mode == 'always'):
      
      s.connect((remote_ip,30001))  
      time.sleep(3)
      print "send data from serial"
           
      ser.write('123')
      time.sleep(5)
      data = s.recv(100)
      print data
      
      print "send data from Network"
      s.send('abc')
      time.sleep(5)
      ser1 = ser.read(10)
      print ser1

      s.close()
      time.sleep(5)
      ser.close()
      time.sleep(5)
      if (data == '123') and (ser1 == 'abc'):
        print "TEST CASE PASSED"
    
      else:
        print data
        print ser1
        print "TEST CASE FAILED"    


    elif (mode == 'any character'):
      #s.connect((device_ip, 10001))
      ser.write('123')
      time.sleep(2)        
      print "write '123'"
      s.connect((remote_ip,30001))
      time.sleep(10)
      print "send data from serial"
     
      #ser.write('123')
      data = s.recv(100)
      print data
   
      print "send data from Network"
      s.send('abc')
      time.sleep(5)
      ser1 = ser.read(10)
      print ser1

      #conn.close()
      time.sleep(5)
      ser.close()
      time.sleep(5)
      if (data == '123') and (ser1 == 'abc'):
        print "TEST CASE PASSED"
    
      else:
        print data
        print ser1
        print "TEST CASE FAILED"   

    else:
      
      ser.write('\x02') 
      print "write 'B'" 
      time.sleep(2)     
      s.connect((remote_ip,30001))
      time.sleep(10)    
      ser.write('123')
      data = s.recv(100)
      print data
   
      print "send data from Network"
      s.send('abc')
      time.sleep(5)
      ser1 = ser.read(10)
      print ser1

      #conn.close()
      time.sleep(5)
      ser.close()
      time.sleep(5)
      if (data == '123') and (ser1 == 'abc'):
        print "TEST CASE PASSED"
    
      else:
        print data
        print ser1
        print "TEST CASE FAILED" 


def tcpaes_listen():
  ser = serial.Serial(serial_port, '{0}'.format(baudrate), timeout=0, parity='{0}'.format(parity), stopbits = int('{0}'.format(stopbits)), bytesize = int('{0}'.format(databits)), rtscts = True)
  childid = pexpect.fdpexpect.fdspawn(ser)
  ser.close()
  ser.open()
  time.sleep(5)  
  
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.settimeout(20)  
           
  #s.connect(('192.168.51.87', 10001))
  #s.listen(10)

  if ser.isOpen():
    ser.flushInput()
    ser.flushOutput()
    print "serial opened"
    print "Testing TCP"
    if (mode == 'always'):
      s.connect(('192.168.51.87', 10001))
      time.sleep(3)
      print "send data from serial"
           
      ser.write('123')
      time.sleep(5)
      data = s.recv(100)
      print data
      
      print "send data from Network"
      s.send('abc')
      time.sleep(5)
      ser1 = ser.read(10)
      print ser1

      s.close()
      time.sleep(5)
      ser.close()
      time.sleep(5)
      if (data == '123') and (ser1 == 'abc'):
        print "TEST CASE PASSED"
    
      else:
        print data
        print ser1
        print "TEST CASE FAILED"   

    elif (mode == 'any character'):
      ser.write('123') 
      print "write '123'"
      s.connect(('192.168.51.87', 10001))
      print "send data from serial"
     
      #ser.write('123')
      data = s.recv(100)
      print data
   
      print "send data from Network"
      s.send('abc')
      time.sleep(5)
      ser1 = ser.read(10)
      print ser1

      #conn.close()
      time.sleep(5)
      ser.close()
      time.sleep(5)
      if (data == '123') and (ser1 == 'abc'):
        print "TEST CASE PASSED"
    
      else:
        print data
        print ser1
        print "TEST CASE FAILED"   

    else:
      ser.write('\x02') 
      print "write 'B'"
      s.connect(('192.168.51.87', 10001))
      print "send data from serial"
          
      ser.write('123')
      data = s.recv(100)
      print data
   
      print "send data from Network"
      s.send('abc')
      time.sleep(5)
      ser1 = ser.read(10)
      print ser1

      #conn.close()
      time.sleep(5)
      ser.close()
      time.sleep(5)
      if (data == '123') and (ser1 == 'abc'):
        print "TEST CASE PASSED"
    
      else:
        print data
        print ser1
        print "TEST CASE FAILED" 


def tls_listen():
  ser = serial.Serial(serial_port, '{0}'.format(baudrate), timeout=0, parity='{0}'.format(parity), stopbits = int('{0}'.format(stopbits)), bytesize = int('{0}'.format(databits)), rtscts = True)
  childid = pexpect.fdpexpect.fdspawn(ser)
  ser.close()
  ser.open()
  time.sleep(5)  
  
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.settimeout(20)  
  
  os.system("/etc/init.d/stunnel4 restart")
  s.bind((remote_ip,4001))
  s.listen(1)
  if ser.isOpen():
    ser.flushInput()
    ser.flushOutput()
    print "serial opened"
    print "Testing TCP"
    if (mode == 'always'):
      conn, addr = s.accept()
      print 'Connection address:', addr
     
      print "send data from serial"
      
      ser.write('123')
      data = conn.recv(10)
      print data
   
      print "send data from Network"
      conn.send('abc')
      time.sleep(5)
      ser1 = ser.readlines()
      print ser1

      conn.close()
      time.sleep(5)
      ser.close()
      time.sleep(5)
      if (data == '123') and (ser1 == 'abc'):
        print "TEST CASE PASSED"
    
      else:
        print data
        print ser1
        print "TEST CASE FAILED"  
      
    elif (mode == 'any character'):
      ser.write('123') 
      print "write '123'"
      print "send data from serial"
      conn, addr = s.accept()
      print 'Connection address:', addr
    
      #ser.write('123')
      data = conn.recv(10)
      print data
   
      print "send data from Network"
      conn.send('abc')
      time.sleep(5)
      ser1 = ser.readlines()
      print ser1

      conn.close()
      time.sleep(5)
      ser.close()
      time.sleep(5)
      if (data == '123') and (ser1 == 'abc'):
        print "TEST CASE PASSED"
    
      else:
        print data
        print ser1
        print "TEST CASE FAILED"   

    else:
      ser.write('\x02') 
      print "write 'B'"
      print "send data from serial"
      conn, addr = s.accept()
      print 'Connection address:', addr
    
      ser.write('123')
      data = conn.recv(10)
      print data
   
      print "send data from Network"
      conn.send('abc')
      time.sleep(5)
      ser1 = ser.readlines()
      print ser1

      conn.close()
      time.sleep(5)
      ser.close()
      time.sleep(5)
      if (data == '123') and (ser1 == 'abc'):
        print "TEST CASE PASSED"
    
      else:
        print data
        print ser1
        print "TEST CASE FAILED" 

def eds1():  
  print "Setting TCP AES credential in EDS32PR"

  clientid = pexpect.spawn('telnet '+remote_ip)
  clientid.expect('>')
  time.sleep(3)
  print "aaaaaa"
  clientid.sendline('enable\r')
  clientid.expect('enable')
  clientid.sendline('tunnel 1\r')
  clientid.expect('tunnel:1')
  time.sleep(2)
  clientid.sendline('connect\r')
  time.sleep(2)
  clientid.expect('tunnel-connect:1')
  clientid.sendline('connect mode always\r')
  time.sleep(4)
  clientid.expect('tunnel-connect:1')
  clientid.sendline('host 1\r')
  time.sleep(4)
  clientid.expect('tunnel-connect-host:1:1')
  print "eeeeeeee"
  clientid.sendline('address 192.168.51.61\r')
  time.sleep(4)
  clientid.sendline('port 10001\r')
  time.sleep(2)
  clientid.sendline('protocol tcp aes\r') 
  time.sleep(2)   
  clientid.sendline('aes encrypt key 11111111111111111111111111111111\r')
  time.sleep(2)
  clientid.sendline('aes decrypt key 11111111111111111111111111111111\r')
  time.sleep(2)
  clientid.sendline('exit\r')
  time.sleep(2)
  clientid.sendline('exit\r')
  time.sleep(2)
  clientid.sendline('exit\r')
  time.sleep(2)
  clientid.sendline('exit\r')

def eds():  
  print "Setting TCP AES credential in EDS32PR"

  clientid = pexpect.spawn('telnet '+remote_ip)
  clientid.expect('>')
  time.sleep(3)
  print "aaaaaa"
  clientid.sendline('enable\r')
  time.sleep(2)
  clientid.expect('enable')
  clientid.sendline('tunnel 1\r')
  time.sleep(2)
  clientid.expect('tunnel:1')
  time.sleep(2)
  clientid.sendline('accept\r')
  time.sleep(2)
  clientid.sendline('protocol tcp aes\r')
  time.sleep(2)
  clientid.sendline('aes encrypt key 11111111111111111111111111111111\r')
  time.sleep(2)
  clientid.sendline('aes decrypt key 11111111111111111111111111111111\r')
  time.sleep(2)
  clientid.sendline('exit\r')
  time.sleep(2)
  clientid.sendline('exit\r')
  clientid.sendline('exit\r')  
  
  
def device_config():
   
  print "configuring the device for Tunnel test"
  clientid = pexpect.spawn('telnet '+device_ip)
  clientid.sendline('\r')
  clientid.sendline('\r')
  time.sleep(3)
  clientid.sendline('config\r')
  clientid.expect('config')
  clientid.sendline('line 1\r')
  clientid.expect('config Line 1')
  clientid.sendline('protocol Tunnel\r')
  clientid.expect('config Line 1')
  clientid.sendline('write\r')
  clientid.sendline('flow Control hardware\r')
  print "configured device as Line -> Tunnel"
  clientid.expect('config Line 1')
  clientid.sendline('write\r')
  clientid.sendline('exit')
  clientid.sendline('Tunnel 1\r')
  if (connect_type == 'connect'): 
    clientid.sendline('connect\r')
    clientid.sendline('mode {0}'.format(mode))  
    time.sleep(2)
    clientid.sendline('write\r')
    print "mode select as {0}".format(mode)
    clientid.sendline('host 1\r')
    clientid.sendline('address {0}'.format(remote_ip))  
    time.sleep(2)
    clientid.sendline('write\r')
    print "remote ip {0}".format(remote_ip)
    if (protocol == 'tcp'):
      clientid.sendline('port {0}'.format(TCP_PORT))
      time.sleep(2)
      clientid.sendline('write\r')
      print "TCP port set as {0}".format(TCP_PORT)
      clientid.sendline('write\r')
      clientid.sendline('exit\r')
      clientid.sendline('exit\r')
      clientid.sendline('exit\r')
      clientid.sendline('exit\r')
      clientid.sendline('exit\r') 
    elif (protocol == 'tcp aes'):
      clientid.sendline('port {0}'.format(10001))
      time.sleep(2)
      clientid.sendline('write\r')
      clientid.sendline('protocol {0}'.format(protocol))
      time.sleep(2)
      clientid.sendline('write\r')
      clientid.sendline('credential test')
      time.sleep(2)
      clientid.sendline('write\r')
      clientid.sendline('exit\r')
      clientid.sendline('exit\r')
      clientid.sendline('exit\r')
      time.sleep(3)
      #clientid.sendline('config\r')
      clientid.sendline('AES Credential test\r')
      clientid.sendline('okay\r')
      clientid.sendline('write\r')
      clientid.sendline('encrypt Key 11111111111111111111111111111111\r')
      clientid.sendline('write\r')
      clientid.sendline('decrypt Key 11111111111111111111111111111111\r')
      clientid.sendline('write\r')
      clientid.sendline('exit\r')
      clientid.sendline('exit\r')
      clientid.sendline('exit\r')
    else:
      clientid.sendline('port {0}'.format(20001))
      time.sleep(2)
      clientid.sendline('write\r')
      clientid.sendline('protocol {0}'.format(protocol))
      time.sleep(2)
      clientid.sendline('write\r')
      clientid.sendline('credential test')
      time.sleep(2)
      clientid.sendline('write\r')
      clientid.sendline('exit\r')
      clientid.sendline('exit\r')
      clientid.sendline('exit\r')
      time.sleep(3)
      clientid.sendline('TLS Credential test\r')
      clientid.sendline('okay\r')
      clientid.sendline('write\r')
      clientid.sendline('Trusted Authority 1\r')
      clientid.sendline('certificate\r')
      clientid.sendline('-----BEGIN CERTIFICATE----- MIIDjTCCAnWgAwIBAgIJAJ+1RQZbaGQoMA0GCSqGSIb3DQEBCwUAMF0xCzAJBgNVBAYTAmluMQswCQYDVQQIDAJ0czEMMAoGA1UEBwwDaHliMQ0wCwYDVQQKDARsdHJ4MQwwCgYDVQQLDANwYXQxFjAUBgNVBAMMDTE5Mi4xNjguNTEuOTkwHhcNMTgwNzEyMTEwMjU3WhcNMTkwNzEyMTEwMjU3WjBdMQswCQYDVQQGEwJpbjELMAkGA1UECAwCdHMxDDAKBgNVBAcMA2h5YjENMAsGA1UECgwEbHRyeDEMMAoGA1UECwwDcGF0MRYwFAYDVQQDDA0xOTIuMTY4LjUxLjk5MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvDhjF3MfkFnh5kP97HCU6AoQk9vRiAjkhyiayNUiFV4vip1epmUzTxp4J8W0g8BR2jz+nWmUZ7jkyTV3u/vMN5GqZxhkhOm/80LX8d0HSL5mOtaFB18hOueYD7/vnyVoVROSIlerTinrKVR2CfSZfg5e15i1UiHIBdWCKX7Za0/DciWqeelEQkpE/oHNozXZliWzs3hQMH5U8dqX4X8hAPoj+bmKP8JjE13Ee5qH8UmuJJrLl6RV0tdt7JmiJrpu7cUT7UXtTeYtxK6cTIJlSMZQDt/7Ic+HfB7FnP1MnnXLsYl+XvkU/zL07jDIwq3pvnv7ZGG4YJ6gYpPGk4I9owIDAQABo1AwTjAdBgNVHQ4EFgQUaEFGwbaZigXGHEaQlRQ6VPQlEVQwHwYDVR0jBBgwFoAUaEFGwbaZigXGHEaQlRQ6VPQlEVQwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAX3X465nkaRS60zC3nsledktkFJy5RrQ7p1JQAeJMKL+7V8ClkSB8StP6NlfAa1+lpncnUrQu2/sCgwwOegnnNbB+B8bhCf5GD9/TeiBcelqLoPYCms2YMJ1d3yEADilDjqVnjl4nQ1AqZZbGla7oqW+R9uueudWX/XlFtp4XqbJsOB41/1mU2cOwUru3tjUe6kocTE5L6rLfekkie3grE8/ykha59mBmy2VQht8AOKnTv44jWNCzaQm6FCYTiogvCbg+AOJ0MWKqzPpkGqaNmGdNWMFUwgUtCTnAY8xkfgmbtOFQrUilQAeKSjwoAqr0amKSCjs7FyumCThftVGAqQ== -----END CERTIFICATE-----')
      clientid.sendline('write\r')
      clientid.sendline('exit\r')
      clientid.sendline('exit\r')
      clientid.sendline('exit\r')
  elif (connect_type == 'accept'):
    clientid.sendline('accept\r')
    clientid.sendline('mode {0}'.format(mode))  
    time.sleep(2)
    clientid.sendline('local port 10001\r')    
    clientid.sendline('write\r')
    if (protocol == 'tcp aes'):
      clientid.sendline('protocol {0}'.format(protocol))
      time.sleep(2)
      clientid.sendline('write\r')
      clientid.sendline('credential test')
      time.sleep(2)
      clientid.sendline('write\r')
      clientid.sendline('exit\r')
      clientid.sendline('exit\r')
      time.sleep(2)
      clientid.sendline('AES Credential test\r')
      clientid.sendline('okay\r')
      clientid.sendline('write\r')
      clientid.sendline('encrypt Key 11111111111111111111111111111111\r')
      clientid.sendline('write\r')
      clientid.sendline('decrypt Key 11111111111111111111111111111111\r')
      clientid.sendline('write\r')
      clientid.sendline('exit\r')
      clientid.sendline('exit\r')
      clientid.sendline('exit\r')
    elif (protocol == 'tls'):
      clientid.sendline('protocol {0}'.format(protocol))
      time.sleep(2)
      clientid.sendline('write\r')
      clientid.sendline('credential test')
      time.sleep(2)
      clientid.sendline('write\r')
      clientid.sendline('exit\r')
      clientid.sendline('exit\r')
      time.sleep(2)
      clientid.sendline('TLS Credential test\r')
      clientid.sendline('okay\r')
      clientid.sendline('write\r')
      #clientid.sendline('Trusted Authority 1\r')
      clientid.sendline('certificate\r')
      clientid.sendline('-----BEGIN CERTIFICATE----- MIIDjTCCAnWgAwIBAgIJAJ+1RQZbaGQoMA0GCSqGSIb3DQEBCwUAMF0xCzAJBgNVBAYTAmluMQswCQYDVQQIDAJ0czEMMAoGA1UEBwwDaHliMQ0wCwYDVQQKDARsdHJ4MQwwCgYDVQQLDANwYXQxFjAUBgNVBAMMDTE5Mi4xNjguNTEuOTkwHhcNMTgwNzEyMTEwMjU3WhcNMTkwNzEyMTEwMjU3WjBdMQswCQYDVQQGEwJpbjELMAkGA1UECAwCdHMxDDAKBgNVBAcMA2h5YjENMAsGA1UECgwEbHRyeDEMMAoGA1UECwwDcGF0MRYwFAYDVQQDDA0xOTIuMTY4LjUxLjk5MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvDhjF3MfkFnh5kP97HCU6AoQk9vRiAjkhyiayNUiFV4vip1epmUzTxp4J8W0g8BR2jz+nWmUZ7jkyTV3u/vMN5GqZxhkhOm/80LX8d0HSL5mOtaFB18hOueYD7/vnyVoVROSIlerTinrKVR2CfSZfg5e15i1UiHIBdWCKX7Za0/DciWqeelEQkpE/oHNozXZliWzs3hQMH5U8dqX4X8hAPoj+bmKP8JjE13Ee5qH8UmuJJrLl6RV0tdt7JmiJrpu7cUT7UXtTeYtxK6cTIJlSMZQDt/7Ic+HfB7FnP1MnnXLsYl+XvkU/zL07jDIwq3pvnv7ZGG4YJ6gYpPGk4I9owIDAQABo1AwTjAdBgNVHQ4EFgQUaEFGwbaZigXGHEaQlRQ6VPQlEVQwHwYDVR0jBBgwFoAUaEFGwbaZigXGHEaQlRQ6VPQlEVQwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAX3X465nkaRS60zC3nsledktkFJy5RrQ7p1JQAeJMKL+7V8ClkSB8StP6NlfAa1+lpncnUrQu2/sCgwwOegnnNbB+B8bhCf5GD9/TeiBcelqLoPYCms2YMJ1d3yEADilDjqVnjl4nQ1AqZZbGla7oqW+R9uueudWX/XlFtp4XqbJsOB41/1mU2cOwUru3tjUe6kocTE5L6rLfekkie3grE8/ykha59mBmy2VQht8AOKnTv44jWNCzaQm6FCYTiogvCbg+AOJ0MWKqzPpkGqaNmGdNWMFUwgUtCTnAY8xkfgmbtOFQrUilQAeKSjwoAqr0amKSCjs7FyumCThftVGAqQ== -----END CERTIFICATE-----\r')
      clientid.sendline('write\r')
      time.sleep(2)
      clientid.sendline('private Key\r')
      clientid.sendline('-----BEGIN RSA PRIVATE KEY----- MIIEpAIBAAKCAQEAvDhjF3MfkFnh5kP97HCU6AoQk9vRiAjkhyiayNUiFV4vip1epmUzTxp4J8W0g8BR2jz+nWmUZ7jkyTV3u/vMN5GqZxhkhOm/80LX8d0HSL5mOtaFB18hOueYD7/vnyVoVROSIlerTinrKVR2CfSZfg5e15i1UiHIBdWCKX7Za0/DciWqeelEQkpE/oHNozXZliWzs3hQMH5U8dqX4X8hAPoj+bmKP8JjE13Ee5qH8UmuJJrLl6RV0tdt7JmiJrpu7cUT7UXtTeYtxK6cTIJlSMZQDt/7Ic+HfB7FnP1MnnXLsYl+XvkU/zL07jDIwq3pvnv7ZGG4YJ6gYpPGk4I9owIDAQABAoIBAQCCZh5gtKV9gIf828Yj9Kt1RuPNTFGSCXcqHHuAAAko/KO7SOO2LA6sEw6Dn3k8fhU3OWK889SZN4Np0t0tI3mMViLUYhXh73/IrNqm+hZ900tIIC7xuHpxMNosrzD39RafOnvXxx0rfecqLxXIN+nPZ21VuLqGOFk3kYAn93Xx3ZSh9z5gURHCaWDayUXDt+OZmJW2YSkfyaDyXHzkYJTO4y/DnfFYX8WFuTIZYI8p4I3yCHaI7AdNi025u7tHXlGdat7ggCDARKlBS55ibYlu55rLHaX8y/JfQxN6679e+4Leh0c932ub7ih4CS0NG62Wy4SbNZUACFVHhVMarsahAoGBAOJVt4PuiQBUy01F2MNDRBYYfQzFuf7tT70wUOJw6xhfocR/HFJRV5weCZX4+StSwDQUzwnD/WpGA1BVEJjhFMm7W7gMmvTMNHkChXZsT6c21H3u2y6E6BZW9ZMUGMCF0AXmNeYUg/SlogeCKg4C8BN4ccmBmmBF7rW/CYfODltFAoGBANTjzNlZBKSdnimnJaptq335UPg3QBFujwDJJxxjwoJI2NICn0PwZT2xHO15qWkCfm1Cb8KKaGEQuhIm1FAMd0sNwpPEhvgNpo5oPJcrwGBnmGkrlgMnr0/iQqT1Mm7DCthYC6+JXZhbxDA2OljsZH0ykf2GWAVe1caZjo+C40/HAoGBALP/p2rtEVeKGATkP3dKz6Mi5pB5z2nGIVw8SJdNZiqEI4q57DQrLJmj6cuzrbWeoezJf74seCVEeO4yOHjcyEOHFXJR1ApLPI/gSXPcv5wkJungQ7/DQzBBCBxoJyc1RDLs2oCYYDj4YNvH0NpDy9owN44h3DwkYat4uoOehBxhAoGAAQbIKhQfzZtk89Z2fAfjV8wn88pwaKUb02kk4yIoAfDP+tNAaVdzZYTBGvQHORZl/ajgWRPJxQ4Ll6LQS0KEILyEP6om7HNEZlNiV2hCmTRmq7smEgXS9pOktp7oC1itaLWj+Mi0xtNKcuEQDvW01lW0FoDbU8tNRJPg+BgteGkCgYA16DuY/syAHdtLEfmAHhEk4bj9MtRzWHSr7sOpQnfMNMQXTeoZ6Nw6yoiyKBXip3xN2OGK80uKnfdMAO/bwZfBtpKBPxiZ5xCz7wZgQ/Db7R806ZqoK3K9OzqDK4FAkaakxt+0fG9rdwCF54NF2IyLUVbnIZ7nGwom1ZNuxvsVpw== -----END RSA PRIVATE KEY-----\r')
      time.sleep(2)
      clientid.sendline('write\r')
      clientid.sendline('exit\r')
      clientid.sendline('exit\r')
      clientid.sendline('exit\r')

    clientid.sendline('exit\r')
    clientid.sendline('exit\r')
    clientid.sendline('exit\r')
    clientid.sendline('exit\r')


  print "set line -> tunnel"
  
  print "cheking xpico240 connect type accept or connect"

  if (connect_type == 'connect'):
    print "connect type -> connect"
    if (protocol == 'tcp'):
      print "connect type -> connect tcp"
      tcp_listen()
    elif (protocol == 'tcp aes'):
      print "connect type -> connect tcp aes" 
      #eds()     
      tcpaes_listen()
    else:
      print "connect type -> connect tls"
      tls_listen()

  elif (connect_type == 'accept'):
    print "connect type -> accept"
    if (protocol == 'tcp'):
      print "connect type -> accept tcp"
      tcp_connect()
    elif (protocol == 'tcp aes'):
      print "connect type -> accept tcp aes"
      #eds1()      
      tcpaes_listen()
    else:
      print "connect type -> accept tls"
      tls_connect()
  

device_config()

sys.exit()