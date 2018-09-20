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
from common import print_f
import ftplib

print "Test accept/connect modes always/Anycharacter/start Character with TCP/TCP AES/TLS"
print "=================================================================================="

#syntax

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>" + " <connect_type>" + "<serial_port>" + " <tunnel_port>" + " <vut_ip>" + " <protocol>" + " <vut_serial_port>" + " <mode>")

if len(sys.argv) < 8:
    script_usage()
    sys.exit()

     
device_ip = sys.argv[1]          #xpico240 ip address
connect_type = sys.argv[2]          #accept or connect
serial_port = sys.argv[3]        #xpico240 serial port
tunnel_port = sys.argv[4]        #tunnel port
vut_ip = sys.argv[5]             #must be eds4100
protocol = sys.argv[6]           # tls or tcp aes
vut_serial_port = sys.argv[7]    #eds4100 serial port
mode = sys.argv[8]               #always or any character or send character

xml_path = "/home/lantronix/MIDAS/xml/"
def fileCompare():
 file1 = open('../''9text.dat', 'r')
 time.sleep(5)
 file2 = open('data.txt', 'r')
 result = 0
 fread1 = file1.readlines()
#print line1
 time.sleep(5)
 fread2 = file2.readlines()
 time.sleep(5)
#print line2
 if (fread1 == fread2):
  print_f("file match tunnel TEST CASE PASSED")
  result = 1
 else:
  print_f("file different tunnel TEST FAILED")
 return result

 file1.close()
 file2.close()


def sendFile():
#open socket connection to port 10001
 pexpect.run('rm data.txt')
 ser = serial.Serial(serial_port,9600)
 ser1 = serial.Serial(vut_serial_port,9600)
 ser.close()
 ser.open()
 ser1.close()
 ser1.open()
 time.sleep(5)
 if ser.isOpen() and ser1.isOpen():
  print_f("serial opened")
  ser.flushInput()
  ser.flushOutput()
  ser1.flushInput()
  ser1.flushOutput()
  f = open('../''9text.dat','r')
  z = bytearray(f.read(6000))
  while z:
      print_f("send data through the tunnel")
      ser1.write(z)
      time.sleep(2)
      serdata = open('data.txt','a')
      seread = ser.read()
      time.sleep(2)
      serdata.write(seread)
      serdata.close()
      time.sleep(5)
      x = ser.inWaiting()
      #print str(showtime) + "\t"  (x)
      #print str(showtime) + "\t" + str(x)
      print_f(x)
      for i in range (0,5):
       if x != 0:
        serdata= open('data.txt','a')
        seread = ser.read(ser.inWaiting())
        time.sleep(5)
        serdata.write(seread)
       #ser.flushInput()
       #ser.flushOutput()
        serdata.close()
       else:
        time.sleep(2)
      print_f("data sent through the tunnel")
      z = bytearray(f.read(6000))
     #if ('{0}'.format(flag) == '1') or ('{0}'.format(flag) == '2'):
 else:
  print_f("cannot open serial port")
 f.close()
 ser.close()
 ser1.close()
 
def factorydefaults():
 
 clientid = pexpect.spawn('telnet '+vut_ip)
 clientid.sendline('\r')
 clientid.sendline('\r')
 time.sleep(3)
 clientid.sendline('enable\r')
 clientid.expect('enable')
 clientid.sendline('reload factory defaults\r')
 clientid.sendline('yes\r')
 clientid.sendline('no\r')
 print_f("EDS4100 reload factory defaults.......")
 time.sleep(2)
 print_f(".......................................")
 time.sleep(2)
 print_f(".......................................")
 time.sleep(2)
 print_f("device is rebooting")
 time.sleep(2)
 

 pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=factory Defaults")
 time.sleep(2)
 print_f("factory defaults the UUT")
 time.sleep(2)
 print_f("...............................")
 time.sleep(2)
 print_f("...............................")
 time.sleep(5)
 print_f("device is rebooting")
 time.sleep(30)

#eds4100 accept mode settings both tcp_aes and tls
def ftp():
 print_f("xml file uploading starting in eds4100")

 tcp_connect = ""+xml_path+"tunnel_VUTconnect_tcp.xml"
 tcpaes_accept = ""+xml_path+"tunnel_VUTaccept_tcpaes.xml"
 tcpaes_connect = ""+xml_path+"tunnel_VUTtcpaes_connect.xml"
 tls_accept = ""+xml_path+"tunnel_VUTtls_accept.xml"
 tls_connect = ""+xml_path+"tunnel_VUTtls_connect.xml"
 ftp = ftplib.FTP("192.168.51.55")
 ftp.login("admin", "PASS") 
 print_f("FTP started.......")

 ftp.storbinary("STOR " + tcp_connect, open(tcp_connect, 'rb'))
 time.sleep(3)
 print_f("tcp aes accept xml uploaded")
 ftp.storbinary("STOR " + tcpaes_accept, open(tcpaes_accept, 'rb'))
 time.sleep(3)
 print_f("tcp aes accept xml uploaded")
 ftp.storbinary("STOR " + tcpaes_connect, open(tcpaes_connect, 'rb'))
 time.sleep(3)
 print_f("tcp aes connect xml uploaded")
 ftp.storbinary("STOR " + tls_accept, open(tls_accept, 'rb'))
 time.sleep(3)
 print_f("tls accept xml uploaded")
 ftp.storbinary("STOR " + tls_connect, open(tls_connect, 'rb'))
 time.sleep(3)
 print_f("tls accept xml uploaded")
 ftp.quit()
 ftp.close()
 print_f("ftp closed")


def vut_tls_accept():
   print_f("uploading eds4100 accept mode settings:")
  
   clientid = pexpect.spawn('telnet '+vut_ip)
   clientid.sendline('\r')
   clientid.sendline('\r')
   time.sleep(3)
   clientid.sendline('enable\r')
   clientid.expect('enable')
   clientid.sendline('xml\r')
   clientid.expect('xml')
   clientid.sendline('xcr import tunnel_VUTtls_accept.xml\r')
   clientid.expect('xml')
   clientid.sendline('write\r')
   clientid.expect('xml')
   clientid.sendline('exit\r')
   clientid.expect('enable')
   clientid.sendline('exit\r')
   print_f("eds4100: XML tunnel accept imported successfully from file system and telnet was closed")

def vut_tcpaes_accept():
   print "uploading eds4100 accept mode settings:"
   clientid = pexpect.spawn('telnet '+vut_ip)
   clientid.sendline('\r')
   clientid.sendline('\r')
   time.sleep(3)
   clientid.sendline('enable\r')
   clientid.expect('enable')
   clientid.sendline('xml\r')
   clientid.expect('xml')
   clientid.sendline('xcr import tunnel_VUTaccept_tcpaes.xml\r')
   clientid.expect('xml')
   clientid.sendline('write\r')
   clientid.expect('xml')
   clientid.sendline('exit\r')
   clientid.expect('enable')
   clientid.sendline('exit\r')
   print_f("eds4100: XML tunnel accept imported successfully from file system and telnet was closed")

#eds4100 connect mode settings tcp, tcp_aes and tls
def vut_tcpconnect():  
  print_f("uploading eds4100 connect mode settings:")
  
  clientid = pexpect.spawn('telnet '+vut_ip)
  clientid.expect('>')
  time.sleep(3)
  clientid.sendline('enable\r')
  clientid.expect('enable')
  clientid.sendline('xml\r')
  clientid.expect('xml')
  clientid.sendline('xcr import tunnel_VUTconnect_tcp.xml\r')
  clientid.expect('xml')
  clientid.sendline('write\r')
  clientid.expect('xml')
  clientid.sendline('exit\r')
  clientid.expect('enable')
  clientid.sendline('exit\r')
  print_f("eds4100: XML tunnel connect mode imported successfully from file system and telnet was closed")

def vut_tls_connect():  
   print_f("uploading eds4100 connect mode settings:")
   
   clientid = pexpect.spawn('telnet '+vut_ip)
   clientid.expect('>')
   time.sleep(3)
   clientid.sendline('enable\r')
   clientid.expect('enable')
   clientid.sendline('xml\r')
   clientid.expect('xml')
   clientid.sendline('xcr import tunnel_VUTtls_connect.xml\r')
   clientid.expect('xml')
   clientid.sendline('write\r')
   clientid.expect('xml')
   clientid.sendline('exit\r')
   clientid.expect('enable')
   clientid.sendline('exit\r')
   print_f("eds4100: XML tunnel connect mode imported successfully from file system and telnet was closed")

def vut_tcpaes_connect():  
   print_f("uploading eds4100 connect mode settings:")
   clientid = pexpect.spawn('telnet '+vut_ip)
   clientid.expect('>')
   time.sleep(3)
   clientid.sendline('enable\r')
   clientid.expect('enable')
   clientid.sendline('xml\r')
   clientid.expect('xml')
   clientid.sendline('xcr import tunnel_VUTtcpaes_connect.xml\r')
   clientid.expect('xml')
   clientid.sendline('write\r')
   clientid.expect('xml')
   clientid.sendline('exit\r')
   clientid.expect('enable')
   clientid.sendline('exit\r')
   print "eds4100: XML tunnel connect mode imported successfully from file system and telnet was closed"

def anyChar():
 ser = serial.Serial(serial_port,9600)
 ser.close()
 ser.open()
 time.sleep(5)
 if ser.isOpen():
   print_f("serial1 opened to send any character")
   ser.write('ab') 
   print_f("write 'ab'")
 ser.close()

def startChar():
 ser = serial.Serial(serial_port,9600)
 ser.close()
 ser.open()
 time.sleep(10)
 if ser.isOpen():
   print_f("serial1 opened to send start character 'b'")
   ser.write('bbb') 
   print_f("write 'b'")
 ser.close()


"""  
def fileCompare_accept_tcp():
 file1 = open('100ktext.dat', 'r')
 file2 = open('data.txt', 'r')
 fread1 = file1.readlines()
#print line1
 fread2 = file2.readlines()
 if (fread1 == fread2):
  print_f("file match.TLS tunnel test passed"
  
 else:
  print_f("file different.TLS tunnel test failed."
  return 1

 file1.close()
 file2.close()
 return 0

def fileCompare_accept_tcpaes():
 file1 = open('100ktext.dat', 'r')
 file2 = open('data.txt', 'r')
 fread1 = file1.readlines()
#print line1
 fread2 = file2.readlines()
 if (fread1 == fread2):
  print_f("file match.TLS tunnel test passed"
  
 else:
  print_f("file different.TLS tunnel test failed."
  return 1

 file1.close()
 file2.close()
 return 0

def fileCompare_accept_tls():
 file1 = open('100ktext.dat', 'r')
 file2 = open('data.txt', 'r')
 fread1 = file1.readlines()
#print line1
 fread2 = file2.readlines()
 if (fread1 == fread2):
  print_f("file match.TLS tunnel test passed"
  
 else:
  print_f("file different.TLS tunnel test failed."
  return 1

 file1.close()
 file2.close()
 return 0

def fileCompare_conect_tcp():
 file1 = open('100ktext.dat', 'r')
 file2 = open('data.txt', 'r')
 fread1 = file1.readlines()
#print line1
 fread2 = file2.readlines()
 if (fread1 == fread2):
  print_f("file match.TLS tunnel test passed"
  
 else:
  print_f("file different.TLS tunnel test failed."
  return 1

 file1.close()
 file2.close()
 return 0


def fileCompare_conect_tcpaes():
 file1 = open('100ktext.dat', 'r')
 file2 = open('data.txt', 'r')
 fread1 = file1.readlines()
#print line1
 fread2 = file2.readlines()
 if (fread1 == fread2):
  print_f("file match.TLS tunnel test passed"
  
 else:
  print_f("file different.TLS tunnel test failed."
  return 1

 file1.close()
 file2.close()
 return 0

def fileCompare_conect_tls():
 file1 = open('100ktext.dat', 'r')
 file2 = open('data.txt', 'r')
 fread1 = file1.readlines()
#print line1
 fread2 = file2.readlines()
 if (fread1 == fread2):
  print_f("file match.TLS tunnel test passed"
  
 else:
  print_f("file different.TLS tunnel test failed."
  return 1

 file1.close()
 file2.close()
 return 0

def sendFile():
#open socket connection to port 10001
 pexpect.run('rm data.txt')
 ser = serial.Serial(serial_port,9600)
 ser1 = serial.Serial(vut_serial_port,9600)
 ser.close()
 ser.open()
 ser1.close()
 ser1.open()
 time.sleep(5)
 if ser.isOpen() and ser1.isOpen():
  print_f("serial opened"
  ser.flushInput()
  ser.flushOutput()
  ser1.flushInput()
  ser1.flushOutput()
  f = open('100ktext.dat','r')
  z = bytearray(f.read(6000))
  while z:
      ser1.write(z)
      serdata = open('data.txt','a')
      seread = ser.read()
      serdata.write(seread)
      serdata.close()
      x = ser.inWaiting()
      print str(showtime) + "\t"  (x)
      for i in range (0,5):
       if x != 0:
        serdata= open('data.txt','a')
        seread = ser.read(ser.inWaiting())
        time.sleep(5)
        serdata.write(seread)
       #ser.flushInput()
       #ser.flushOutput()
        serdata.close()
       else:
        time.sleep(2)
      print_f("data sent through tls tunnel"
      z = bytearray(f.read(6000))
     #if ('{0}'.format(flag) == '1') or ('{0}'.format(flag) == '2'):
 else:
      print_f("cannot open serial port"
 f.close()
 ser.close()
 ser1.close()
"""
####################xpico240 accept mode#######################################################################################

def uut_accept_tcp():
  print_f("Configuring xpico240 accept mode tcp")
 
  if (mode == 'always'):
    print_f("mode always")
    tcp_always = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"tunnel_accept_always_tcp.xml")
    time.sleep(10)
    print_f("tcp always xml imported successfully\n" + str(tcp_always))
    vut_tcpconnect()

  elif (mode == 'anyCharacter'):
    print_f("mode any character")
    tcp_anycharacter = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"tunnel_accept_anyCharacter_tcp.xml")
    time.sleep(10)
    print_f("tcp any character xml imported successfully" + str(tcp_anycharacter))
    vut_tcpconnect()
    anyChar()
  
  else: 
    print_f("mode start character")
    tcp_startcharacter = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"tunnel_accept_startCharacter_tcp.xml")
    time.sleep(10)
    print_f("tcp start character xml imported successfully" + str(tcp_startcharacter))
    vut_tcpconnect()
    startChar()

def uut_accept_tcpaes():
  print_f("Configuring xpico240 accept mode tcp")
 
  if (mode == 'always'):
    print_f("mode always")
    tcpaes_always = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"tunnel_accept_always_tcpaes.xml")
    time.sleep(10)
    print_f("tcp always xml imported successfully" + str(tcpaes_always))
    vut_tcpaes_connect()

  elif (mode == 'anyCharacter'):
    print_f("mode any character")
    tcpaes_anycharacter = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"tunnel_accept_anyCharacter_tcpaes.xml")
    time.sleep(10)
    print_f("tcp any character xml imported successfully" + str(tcpaes_anycharacter))
    vut_tcpaes_connect()
    anyChar()

  else: 
    print_f("mode start character")
    tcpaes_startcharacter = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"tunnel_accept_startCharacter_tcpaes.xml")
    time.sleep(10)
    print_f("tcp start character xml imported successfully" + str(tcpaes_startcharacter))
    vut_tcpaes_connect()
    startChar()

def uut_accept_tls():
  print_f("Configuring xpico240 accept mode tcp")
 
  if (mode == 'always'):
    print_f("mode always")
    tls_always = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"tunnel_accept_always_tls.xml")
    time.sleep(10)
    print_f("tcp always xml imported successfully" + str(tls_always))
    vut_tls_connect()

  elif (mode == 'anyCharacter'):
    print_f("mode any character")
    tls_anycharacter = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"tunnel_accept_anyCharacter_tls.xml")
    time.sleep(10)
    print_f("tcp any character xml imported successfully" + str(tls_anycharacter))
    vut_tls_connect()
    anyChar()

  else: 
    print_f("mode start character")
    tls_startcharacter = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"tunnel_accept_startCharacter_tls.xml")
    time.sleep(10)
    print_f("tcp start character xml imported successfully" + str(tls_startcharacter))
    vut_tls_connect()
    startChar()


####################xpico240 connect mode#######################################################################################


def uut_connect_tcp():
  print_f("Configuring xpico240 accept mode tcp")
 
  if (mode == 'always'):
    print_f("mode always")
    tcp_always = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"tunnel_connect_always_tcp.xml")
    time.sleep(10)
    print_f("tcp always xml imported successfully" + str(tcp_always))


  elif (mode == 'anyCharacter'):
    print_f("mode any character")
    tcp_anycharacter = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"tunnel_connect_anyCharacter_tcp.xml")
    time.sleep(10)
    print_f("tcp any character xml imported successfully" + str(tcp_anycharacter))
    anyChar()

  else: 
    print_f("mode start character")
    tcp_startcharacter = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"tunnel_connect_startCharacter_tcp.xml")
    time.sleep(10)
    print_f("tcp start character xml imported successfully" + str(tcp_startcharacter))
    startChar()

def uut_connect_tcpaes():
  print_f("Configuring xpico240 accept mode tcp")
 
  if (mode == 'always'):
    print_f("mode always")
    tcpaes_always = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"tunnel_connect_always_tcpaes.xml")
    time.sleep(10)
    print_f("tcp always xml imported successfully" + str(tcpaes_always))
    vut_tcpaes_accept

  elif (mode == 'anyCharacter'):
    print_f("mode any character")
    tcpaes_anycharacter = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"tunnel_connect_anyCharacter_tcpaes.xml")
    time.sleep(10)
    print_f("tcp any character xml imported successfully" + str(tcpaes_anycharacter))
    vut_tcpaes_accept
    anyChar()

  else: 
    print_f("mode start character")
    tcpaes_startcharacter = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"tunnel_connect_startCharacter_tcpaes.xml")
    time.sleep(10)
    print_f("tcp start character xml imported successfully" + str(tcpaes_startcharacter))
    vut_tcpaes_accept
    startChar()


def uut_connect_tls():
  print_f("Configuring xpico240 accept mode tcp")
 
  if (mode == 'always'):
    print_f("mode always")
    tls_always = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"tunnel_connect_always_tls.xml")
    time.sleep(10)
    print_f("tcp always xml imported successfully" + str(tls_always))
    vut_tls_accept()

  elif (mode == 'anyCharacter'):
    print_f("mode any character")
    tls_anycharacter = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"/tunnel_connect_anyCharacter_tls.xml")
    time.sleep(10)
    print_f("tcp any character xml imported successfully" + str(tls_anycharacter))
    vut_tls_accept()  
    anyChar()

  else: 
    print_f("mode start character")
    tls_startcharacter = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"tunnel_connect_startCharacter_tls.xml")
    time.sleep(10)
    print_f("tcp start character xml imported successfully" + str(tls_startcharacter))
    vut_tls_accept()
    startChar()

"""
####################hapa+ accept mode#######################################################################################

def vut_accept_tcpaes():

  print "Configuring hspa+ connect mode tcpaes"
  connect_tcpaes = pexpect.run("curl --anyauth -u admin:PASS http://"+vut_ip+"/import/config -X POST --form configrecord=@tunnel_VUTaccept_tcpaes.xml")
  time.sleep(10)
  print "tls xml imported successfully" + str(connect_tcpaes)

def vut_accept_tls():

  print "Configuring hspa+ connect mode tls"
  connect_tls = pexpect.run("curl --anyauth -u admin:PASS http://"+vut_ip+"/import/config -X POST --form configrecord=@tunnel_VUTaccept_tls.xml")
  time.sleep(10)
  print "tls xml imported successfully" + str(connect_tls)

####################hapa+ connect mode#######################################################################################

def vut_connect_tcp():

  print "Configuring hspa+ connect mode tcp"
  connect_tcp = pexpect.run("curl --anyauth -u admin:PASS http://"+vut_ip+"/import/config -X POST --form configrecord=@tunnel_VUTconnect_tcp.xml")
  time.sleep(10)
  print "tls xml imported successfully" + str(connect_tcp)

def vut_connect_tcpaes():

  print "Configuring hspa+ connect mode tcp aes"
  connect_tcpaes = pexpect.run("curl --anyauth -u admin:PASS http://"+vut_ip+"/import/config -X POST --form configrecord=@tunnel_VUTconnect_tcpaes.xml")
  time.sleep(10)
  print "tls xml imported successfully" + str(connect_tcpaes)

def vut_connect_tls():

  print "Configuring hspa+ connect mode tls"
  connect_tls = pexpect.run("curl --anyauth -u admin:PASS http://"+vut_ip+"/import/config -X POST --form configrecord=@tunnel_VUTconnect_tls.xml")
  time.sleep(10)
  print "tls xml imported successfully" + str(connect_tls)
"""



def device_config(port):
  #factorydefaults()
  ftp()
  print_f("configure device")
  telnet_config = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"telnet.xml")
  print_f("enabled telnet ........")
  time.sleep(5)
  clientid = pexpect.spawn('telnet '+device_ip)
  clientid.expect('>')
  clientid.sendline('config\r')
  clientid.expect('config')
  clientid.sendline('line 1\r')
  clientid.expect('config Line 1')
  clientid.sendline('protocol tunnel\r')
  clientid.sendline('exit\r')
  clientid.sendline('exit\r')
  clientid.sendline('exit\r')
  
  print_f("set line -> tunnel")
  
  print_f("cheking xpico240 connect type accept or connect")
  if (connect_type == 'accept'):
    print_f("connect type accept")
       
    if (protocol == 'tcp'):
     print_f("Protocol tcp")
     print_f("checking mode always/any character/start character")
     uut_accept_tcp()
     #vut_connect_tcp()
     sendFile()
     fileCompare()
   
    elif (protocol == 'tcpaes'):
     print_f("protocol tcp aes")
     uut_accept_tcpaes()
     #vut_connect_tcpaes()
     sendFile()
     fileCompare()

    else:
     print_f("protocol tls")
     uut_accept_tls()
     #vut_connect_tls()
     sendFile()
     fileCompare()
        
  elif (connect_type == 'connect'):
    print_f("connect type connect")
    

    if (protocol == 'tcp'):
     print_f("Protocol tcp")
     uut_connect_tcp()
     sendFile()
     fileCompare()
   
    elif (protocol == 'tcpaes'):
     print_f("protocol tcp aes")
     uut_connect_tcpaes()
     #vut_accept_tcpaes()
     sendFile()
     fileCompare()

    else:
     print_f("protocol tls")
     uut_connect_tls()
     #vut_accept_tls()
     sendFile()
     fileCompare()
       
  else:
    print_f("connect type not selected")   

#main program

device_config(tunnel_port)

sys.exit()

