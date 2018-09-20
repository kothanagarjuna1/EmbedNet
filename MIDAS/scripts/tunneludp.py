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
from common import print_f

#syntax

print_f("Test UDP Tunnel")
print_f("===============")

def script_usage():
 print_f("Usage: " + os.path.basename(sys.argv[0]) + " <serial_port>" + " <baudrate>" + " <databits>" + " <parity>" + " <stopbits>"  +  " <device_ip>"  + " <tunnel_port> " +  " <udp mode>"  +  " <socket bind> " + " <udp tunnel mode> "  + "<network>")
 return

if len(sys.argv) < 11:
    script_usage()
    sys.exit()

#NOTE: RUN THE SCRIPT AS LTRXENGR AND NOT ROOT

serial_port = sys.argv[1]
baudrate = sys.argv[2]
databits = sys.argv[3]
parity = sys.argv[4]
stopbits = sys.argv[5]
device_ip = sys.argv[6]
tunnel_port = sys.argv[7]
udp_mode = sys.argv[8] #values restricted or unrestricted
socketbind = sys.argv[9] # values: 1 or 0. if udptunnel is passive,socket bind is always 1 
udptunnel = sys.argv[10] #values: active or passive
network = sys.argv[11]
script_path = "/home/lantronix/MIDAS/xml"
print_f(network)

def udpTunnel (udpmode, sbind): # device initiates the connection
 ser = serial.Serial(serial_port, '{0}'.format(baudrate), timeout=0, parity='{0}'.format(parity), stopbits = int('{0}'.format(stopbits)), bytesize = int('{0}'.format(databits)), rtscts = True)
 childid = pexpect.fdpexpect.fdspawn(ser)
 ser.close()
 ser.open()
 time.sleep(5)
 tun_port = int(tunnel_port)
 #pexpect.run('nc -v -u -n device_ip 50001')
 sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
 sock.settimeout(20)
 sock1 = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
 sock1.settimeout(20)
 z = "HELLO WORLD"
 pexpect.run('rm udpdata')
 result = 0
 result1 = 0
 result2 = 0
 result3 = 0
 UDP_IP = '192.168.51.25'
 UDP_PORT = 50001
 UDP_PORT1 = 60001
 UDP_PORT = int(UDP_PORT)
 UDP_PORT1 = int(UDP_PORT1)
 if (sbind == '1'):
  sock.bind((UDP_IP,UDP_PORT))
  sock1.bind((UDP_IP,UDP_PORT1))
 if ser.isOpen():
   ser.flushInput()
   ser.flushOutput()
   print_f("serial opened")
   print_f("Testing UDP", udptunnel)
   ser.write('abc')
   time.sleep(5)
  
   if (udptunnel == 'active'): 
    if (sbind == '1'):
     data = sock.recv(10)
     print_f(data)

   if (udptunnel == 'passive'): 
    try:
     if (sbind == '1'):
      data = sock.recv(10)
      print_f(data)
    except Exception as e:
     result1 = 1
     print(str(e))
 
   sock.sendto(z, (device_ip, tun_port))
   time.sleep(60)
   if (udptunnel == 'passive'):
    data = sock.recv(10)
    print_f("data is", data)
    if (data == 'abc'):
     result2 = 1
     
   for x in range (0,len(z)):
    serdata = ser.read()
    print_f(serdata)
    fudp = open('udpdata','a')
    fudp.write(serdata)
    fudp.close()
   time.sleep(5)
   fudpsize = os.path.getsize("udpdata")

   if (udptunnel == 'passive'): 
    sock1.sendto(z, (device_ip, tun_port))
    time.sleep(60)
    for x in range (0,len(z)):
     serdata1 = ser.read()
     fudp = open('udpdata','a')
     fudp.write(serdata1)
     fudp.close()
     time.sleep(5)  
     print_f("serial data is", serdata1)
     fudpsize = os.path.getsize("udpdata")
     print_f(fudpsize)
     if (udpmode == 'unrestricted') and (fudpsize == len(z) * 2):
      result3 = 1
     elif (udpmode == 'restricted') and (serdata1 == ""):
       result3 = 1
      
   sock.close()
   ser.close()
   time.sleep(5)

#udp tunnel active result
   if (udptunnel == 'active'):

    if (udpmode == 'unrestricted') and (sbind == '1'):
     if (fudpsize == len(z)) and (data == 'abc'):
       print_f("udp tunnel active unrestricted mode: data sent through UDP tunnel.test passed")
       result = 1

    if (udpmode == 'unrestricted') and (sbind == '0'):
     if (fudpsize == len(z)):
      print_f("udp tunnel active unrestricted mode: data sent through UDP tunnel.test passed")
      result = 1
 
    if (udpmode == 'restricted') and (sbind == '0'):
     if (fudpsize == 0):
      print_f("udp tunnel active restricted mode: data discarded. test passed")
      result = 1

    if (udpmode == 'restricted') and (sbind == '1'):
     if (fudpsize == len(z)) and (data == 'abc'):
      print_f("restricted mode: udp data received. test passed")
      result = 1
    
#udp tunnel passive result
   if (udptunnel == 'passive'):
    print_f(result1)
    print_f(result2)
    print_f(result3)
    #if (sbind == '1') and (udpmode == 'unrestricted'):
    if (result1 == 1) and (result2 == 1) and (result3 == 1):
      #if (fudpsize == len(z) * 2):
       print_f("udp tunnel passive mode test case passed", udpmode)
       result = 1

    #if (sbind == '1') and (udpmode == 'restricted'):
     #if (result1 == 1) and  (result2 == 1) and (result3 == 1):
      #print "udp tunnel passive restricted mode test case passed"     
    #  result = 1
      
 print_f("result is:", result)
 return result

def device_config():
  print_f("configure device")
  telnet_config = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+script_path+"telnet.xml")
  print_f("enabled telnet ........")
  time.sleep(5)
  clientid = pexpect.spawn('telnet '+device_ip)
  clientid.sendline('status\r')
  clientid.expect('status')
  clientid.sendline('device\r')
  clientid.expect('status Device')
  clientid.sendline('reboot')
  clientid.expect('okay/cancel')
  clientid.sendline('okay\r')
  print_f("Rebooting")
  #clientid.expect('Rebooting')
  time.sleep(50)
  print_f("configuring device")
  clientid = pexpect.spawn('telnet '+device_ip)
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
  clientid.sendline('protocol tunnel\r')
  clientid.expect('config Line 1')
  clientid.sendline('exit\r')
  clientid.expect('config')
  clientid.sendline('tunnel 1\r')
  clientid.expect('config Tunnel 1')
  clientid.sendline('connect\r')
  clientid.expect('config Tunnel 1')
  clientid.sendline('host 1\r')
  clientid.sendline('protocol udp\r')
  clientid.sendline('address 192.168.51.25')
  #clientid.expect('config Tunnel Connect')
  if (udp_mode == 'restricted'):
    clientid.sendline('reception restricted\r')
  elif (udp_mode == 'unrestricted'):
    clientid.sendline('reception unrestricted\r')
  clientid.expect('config Tunnel 1')
  if (udptunnel == 'passive'):
   if network == 'eth0':
    clientid.sendline('address eth0\r')
    clientid.expect('config Tunnel 1')
   elif network == 'wlan0':
    clientid.sendline('address wlan0\r')
    clientid.expect('config Tunnel 1')
  clientid.sendline('port 50001\r')
  clientid.expect('config Tunnel 1')
  if (udptunnel == 'passive'):
   clientid.sendline('port <none>\r')
   clientid.expect('config Tunnel 1')
  clientid.sendline('exit\r')
  clientid.expect('config Tunnel 1')
  clientid.sendline('local port 10001\r')
  clientid.expect('config Tunnel 1')
  clientid.sendline('mode any char\r')
  clientid.expect('config Tunnel 1')
  clientid.sendline('exit\r')
  if (udptunnel == 'passive'):
   clientid.sendline('disconnect\r')
   clientid.sendline('timeout 90000')
  clientid.sendline('exit\r')
  clientid.expect('config Tunnel 1')
  clientid.sendline('exit\r')
  clientid.expect('config')
  clientid.sendline('write\r')
  clientid.expect('config')
  clientid.sendline('exit\r')
  clientid.expect('>')
  clientid.close()
  result = udpTunnel(udp_mode, socketbind)
  print_f(result)
  if (result == 1):
   print_f("TEST CASE PASSED")
  else:
   print_f("TEST FAILED")
  #udptunnel(filename)
  clientid = pexpect.spawn('telnet '+device_ip) 
  clientid.sendline('config\r')
  clientid.expect('config')
  clientid.sendline('tunnel 1')
  clientid.expect('config Tunnel 1')
  clientid.sendline('connect')
  clientid.expect('config Tunnel 1')
  clientid.sendline('mode disable\r')
  time.sleep(2)
  #clientid.expect('okay/cancel')
  clientid.sendline('okay\r')
  time.sleep(3)
  clientid.expect('config Tunnel 1')
  clientid.sendline('exit\r')
  clientid.sendline('disconnect\r')
  clientid.sendline('timeout <disabled>\r')
  clientid.sendline('exit\r')
  clientid.sendline('exit\r')
  clientid.expect('config')
  clientid.sendline('write\r')
  clientid.expect('config')
  clientid.sendline('exit\r')
  clientid.expect('>')

# main program
device_config()

sys.exit()
