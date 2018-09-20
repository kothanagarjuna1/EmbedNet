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

print_f("Test Tunnel Connect Modes")
print_f("=========================")

#syntax

def script_usage():
 print_f("Usage: " + os.path.basename(sys.argv[0]) + " <serial_port>" + " <baudrate>" + " <databits>" + " <parity>" + " <stopbits>"  +  " <device_ip>"  + " <tunnel_port> " + " <remote ip> " + " <initial send>")
 return

if len(sys.argv) < 9:
    script_usage()
    sys.exit()

serial_port = sys.argv[1]
baudrate = sys.argv[2]
databits = sys.argv[3]
parity = sys.argv[4]
stopbits = sys.argv[5]
device_ip = sys.argv[6]
tunnel_port = sys.argv[7]
remote_ip = sys.argv[8] #must be a linux PC
initial_send = sys.argv[9]

def sock_open():
 sock = socket.socket(socket.AF_INET, # Internet
                          socket.SOCK_STREAM) # TCP
 sock1 = socket.socket(socket.AF_INET, # Internet
                       socket.SOCK_STREAM) # TCP
 #sock, sock1 = socket.socketpair()
 sock.settimeout(20)
 pexpect.run('rm udpdata')
 
 REMOTE_PORT1 = 5001
 REMOTE_PORT2 = 5002
 RPORT1 = int(REMOTE_PORT1)
 RPORT2 = int(REMOTE_PORT2)
 sock.bind((remote_ip, RPORT1))
 sock.listen(10)
 sock1.bind((remote_ip, RPORT2))
 sock1.listen(10)

def tunnel(remoteip, connection, insend):
 ser = serial.Serial(serial_port, '{0}'.format(baudrate), timeout=0, parity='{0}'.format(parity), stopbits = int('{0}'.format(stopbits)), bytesize = int('{0}'.format(databits)), rtscts = True)
 childid = pexpect.fdpexpect.fdspawn(ser)
 ser.close()
 ser.open()
 time.sleep(5)
 tun_port = int(tunnel_port)
   #pexpect.run('nc -v -u -n device_ip tun_port')
 sock = socket.socket(socket.AF_INET, # Internet
                          socket.SOCK_STREAM) # TCP
 sock1 = socket.socket(socket.AF_INET, # Internet
                       socket.SOCK_STREAM) # TCP
 #sock, sock1 = socket.socketpair()
 sock.settimeout(20)
 pexpect.run('rm udpdata')
 result = 0
 REMOTE_PORT1 = 5001
 REMOTE_PORT2 = 5002
 RPORT1 = int(REMOTE_PORT1)
 RPORT2 = int(REMOTE_PORT2)
 sock.bind((remoteip, RPORT1))
 sock.listen(10)
 sock1.bind((remoteip, RPORT2))
 sock1.listen(10)
 res = 0
 if ser.isOpen():
   print_f("serial opened")
   ser.flushInput()
   ser.flushOutput()
   time.sleep(10)
   ser.write('a')
 
   if (connection == 'sequential'):
    print_f("test tunnel sequential mode")
 #   sock_open()
    #ser.write('a')
    time.sleep(5)
    conn,addr = sock.accept()
    print_f("connected by", addr)
    print_f("sending from network")
    conn.send('abc')
    time.sleep(15)
    ser1 = ser.readlines()
    print_f("serial data ser1 is", ser1)
    print_f("receving from network")
    dat = conn.recv(10)
    print_f("data is", dat)
    time.sleep(60)
    #sock.shutdown(socket.SHUT_RDWR)
    conn.close()
    #sock.close()
    time.sleep(5)
   
    print_f("2nd TRY")
    ser.write('a')
    conn,addr= sock.accept()
    print_f("connected by", addr)
    print_f("sending from network")
    conn.send('abc')
    time.sleep(20)
    ser2 = ser.readlines()
    print_f("serial data ser2", ser2)
    print_f("receiving from network")
    dat1 = conn.recv(10)
    time.sleep(60)
    print_f("data1 is", dat1)
   
  ################################################
  
   if (connection == 'round-robin'):
    print_f("test tunnel round-robin mode")

    conn, addr = sock1.accept()
    print_f("connected by", addr)
    print_f("sending from network")
    conn.send('abc')
    time.sleep(10)
    ser2 = ser.readlines()
    print_f("serial data ser2", ser2)
    print_f("receiving from network")
    dat1 = conn.recv(10)
    print_f("data1 is", dat1)
    time.sleep(60)
    conn.close()
    time.sleep(5)
  
    print_f("2nd TRY")
    ser.write('a')
    time.sleep(10)
    conn, addr = sock.accept()
    print_f("connected by", addr)
    print_f("sending from network")
    conn.send('abc')
    time.sleep(10)
    ser1 = ser.readlines()
    print_f("serial data ser1", ser1)
    print_f("receiving from network")
    dat = conn.recv(10)
    print_f("data is", dat)
    time.sleep(60)
    conn.close() 

 #################################################################
   
   if (connection == 'simultaneous'):
    print_f("test tunnel simultaneous mode")
    conn,addr = sock.accept()
    print_f("connected by", addr)
    conn1, addr1 = sock1.accept()
    print_f("connected by", addr1)
    print_f("sending from network")
    conn.send('abc')
    time.sleep(10)
    conn1.send('abc')
    time.sleep(10)
    ser1 = ser.readlines()
    time.sleep(10)
    print_f("serial data ser1", ser1)
    dat = conn.recv(10)
    dat1 = conn1.recv(10)
    time.sleep(60)
    print_f("data is", dat)
    print_f("data1 is", dat1)
    conn.close()
    conn1.close()
 #####################################################################
 if (connection == 'round-robin') or (connection == 'sequential'): 
  if (dat == '{0}'.format(insend)+'a') and (dat1 == '{0}'.format(insend)+'a') and (ser1 == ['abc']) and (ser2 ==['abc']):
   print_f("data sent and received from network")
   res = 1
 if (connection == 'simultaneous'):
  if (dat == '{0}'.format(insend)+'a') and (dat1 == '{0}'.format(insend)+'a') and (ser1 == ['abcabc']):
   print_f("data sent and received from network")
   res = 1

 print_f("result is", res)
 return res
 sock.close()
 sock1.close()
 ser.close()

def tunnel_close(): #obselete. set tunnel disconnect to terminate connection
  clientid = pexpect.spawn('telnet ' +device_ip)
  clientid.sendline('status\r')
  clientid.expect('status')
  clientid.sendline('tunnel 1\r')
  clientid.expect('status Tunnel 1')
  clientid.sendline('current connection connect 2\r')
  clientid.expect('status Tunnel 1 Current Connection Connect 2')
  clientid.sendline('kill\r')
  clientid.expect('okay/cancel')
  clientid.sendline('okay\r')
  time.sleep(5)
  #clientid.expect('status Tunnel 1 Current Connection Connect 2')
  clientid.sendline('exit\r')
  clientid.expect('status Tunnel 1 Current Connection')
  clientid.sendline('current connection connect 1\r')
  clientid.expect('status Tunnel 1 Current Connection Connect 1')
  clientid.sendline('kill\r')
  clientid.expect('okay/cancel')
  clientid.sendline('okay\r')
  time.sleep(5)

  clientid.sendline('exit\r')
  clientid.expect('status Tunnel 1')
  clientid.sendline('exit\r')
  clientid.expect('status')
  clientid.sendline('exit\r')
  clientid.expect('>')
 
def device_config(remoteip,connection):
  clientid = pexpect.spawn('telnet ' +device_ip)
  clientid.sendline('status\r')
  clientid.expect('status')
  clientid.sendline('device\r')
  clientid.expect('status Device')
  clientid.sendline('reboot')
  clientid.expect('okay/cancel')
  clientid.sendline('okay\r')
  print_f("Rebooting")
  #clientid.expect('Rebooting')
  time.sleep(40)
  clientid = pexpect.spawn('telnet ' +device_ip)
  time.sleep(5)
  clientid.sendline('\r')
  clientid.sendline('\r')
  clientid.sendline('config\r')
  clientid.expect('config')
  clientid.sendline('line 1\r')
  clientid.expect('config Line 1')
  clientid.sendline('baud rate {0}'.format(baudrate))
  clientid.expect('config Line 1')
  clientid.sendline('data bits {0}'.format(databits))
  clientid.expect('config Line 1')
  clientid.sendline('parity {0}'.format(parity))
  clientid.expect('config Line')
  clientid.sendline('stop bits {0}'.format(stopbits))
  clientid.expect('config Line')
  clientid.sendline('flow control hardware\r')
  clientid.expect('config Line')
  clientid.sendline('protocol tunnel\r')
  clientid.sendline('exit\r')
  clientid.expect('config')
  clientid.sendline('tunnel 1\r')
  clientid.expect('config Tunnel 1')
  clientid.sendline('connect\r')
  clientid.expect('config Tunnel 1 Connect')
  clientid.sendline('host 1\r')
  clientid.expect('config Tunnel 1 Connect Host 1')
  clientid.sendline('address {0}'.format(remoteip))
  clientid.expect('config Tunnel 1 Connect Host 1')
  clientid.sendline('port 5001\r')
  clientid.expect('config Tunnel 1 Connect Host 1')
  clientid.sendline('protocol tcp\r')
  clientid.expect('config Tunnel 1 Connect Host 1')
  clientid.sendline('initial send {0}'.format(initial_send))
  clientid.expect('config Tunnel 1 Connect Host 1')
  clientid.sendline('exit\r')
#  if  (connection == 'simultaneous'):
  #clientid.expect('config Tunnel 1 Connect\r')
  clientid.sendline('host 2\r')
  #clientid.expect('config Tunnel 1 Connect Host 2\r')
  clientid.sendline('address {0}'.format(remoteip))
  #clientid.expect('config Tunnel Connect Host 2\r')
  clientid.sendline('port 5002\r')
  clientid.sendline('initial send {0}'.format(initial_send))
  clientid.expect('config Tunnel 1 Connect Host 2')
  #clientid.expect('config Tunnel 1 Connect Host 2\r')
  clientid.sendline('exit\r')
  clientid.expect('config Tunnel 1 Connect')
  clientid.sendline('local port <random>\r')
  clientid.expect('config Tunnel 1 Connect')
  clientid.sendline('mode any character\r')
  clientid.expect('config Tunnel 1 Connect')
  clientid.sendline('connections {0}'.format(connection))
  clientid.expect('config Tunnel 1 Connect')
  clientid.sendline('exit\r')
  clientid.expect('config Tunnel 1')
  clientid.sendline('disconnect\r')
  clientid.expect('config Tunnel 1 Disconnect')
  clientid.sendline('timeout 60000\r')
  clientid.sendline('exit\r')
  clientid.expect('config Tunnel 1')
  clientid.sendline('exit\r')
  clientid.expect('config')
  clientid.sendline('write\r')
  clientid.expect('config')
  clientid.sendline('exit\r')
  clientid.expect('>')
  clientid.close()


# main program
def main():
 device_config(remote_ip,'sequential')
 seq_result = tunnel(remote_ip, 'sequential', initial_send)
 if (seq_result == 1):
    print_f("Tunnel Connect Sequential Passed")
 else:
    print_f("Tunnel Connect Sequential Failed")

 device_config(remote_ip,'simultaneous')
 sim_result = tunnel(remote_ip, 'simultaneous', initial_send)
 if (sim_result == 1):
    print_f("Tunnel Connect Simultaneous Passed")
 else:
    print_f("Tunnel Connect Simultaneous Failed")

 device_config(remote_ip,'round-robin')
 rr_result = tunnel(remote_ip, 'round-robin', initial_send)
 if (rr_result == 1):
    print_f("Tunnel Connect Round-Robin Passed")
 else:
    print_f("Tunnel Connect Round-Robin Failed")

 if ((seq_result == 1) and (sim_result == 1) and (rr_result == 1)):
    print_f("Tunnel Connect TEST CASE PASSED")
 else:
    print_f("Tunnel Connect TEST CASE FAILED")


main()
sys.exit()
