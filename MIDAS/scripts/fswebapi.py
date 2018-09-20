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
#import requests
from time import gmtime, strftime

showtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())

print str(showtime) + "\t Test File system commands and Web API"
print str(showtime) + "\t ====================================="

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>"  + "<serial_port>")
 return

if len(sys.argv) < 2:
    script_usage()
    sys.exit()


device_ip = sys.argv[1]
serial_port = sys.argv[2]
script_path = "/home/lantronix/MIDAS/xml/"

def rebootDevice():
 pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")
 #clientid = pexpect.spawn('telnet '+device_ip)
 #clientid.sendline('\r')
# clientid.sendline('\r')
 #clientid.sendline('status')
 #clientid.sendline('device')
 #clientid.sendline('reboot')
 #time.sleep(2)
 #clientid.sendline('okay')
 print str(showtime) + "\t device is rebooting"
 time.sleep(30)


def formatFilesystem():
  clientid = pexpect.spawn('telnet '+device_ip)
  clientid.sendline('\r')
  clientid.sendline('\r')
  clientid.sendline('status\r')
  clientid.sendline('file system\r')
  print str(showtime) + "\t format fs"
  clientid.sendline('format')
  time.sleep(3)
  clientid.sendline('okay')
  time.sleep(10)
  format_complete = clientid.expect(['The file system has been formatted.'])
  if format_complete == 0:
   print str(showtime) + "\t file system formatted"
  else:
   print str(showtime) + "\t failed to format filesystem.aborting."
   sys.exit()
  clientid.sendline('exit\r')
  clientid.sendline('exit\r')
  clientid.close()

def filesystemCommands():
  
 rebootDevice()
 tc = 1
 ser = os.open(serial_port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY )
 clientid = pexpect.fdpexpect.fdspawn(ser)
 time.sleep(5)
 ser1 = serial.Serial(serial_port,9600) # open the serial port
 tc = 1
 ser1.close()
 ser1.open()
 if ser1.isOpen():
  formatFilesystem()
  print str(showtime) + "\t test file system commands through CLI" 
  #clientid = pexpect.spawn('telnet '+device_ip)
  clientid.sendline('\r')
  clientid.sendline('\r')  
  clientid.sendline('file system\r')
  print "create recursive dir"
  clientid.sendline('mkdir a/b/c/d/e')

  print str(showtime) + "\t change dir\r"
  clientid.sendline('cd a/b/c/d/e')
  clientid.sendline('pwd')
  time.sleep(3)
  pwd = clientid.expect(['/a/b/c/d/e'])
  time.sleep(3)
  if pwd == 0:
   print "recursive dir successfully created. max dir depth is 5"
  else:
   print "failed to create recursive dir"
   tc = 0
  clientid.sendline('cd')

  print str(showtime) + "\t create long path name"
  clientid.sendline('mkdir 12345678901234567890123456789012345678901234567890123456789012345678901234567890')
  clientid.sendline("cd 12345678901234567890123456789012345678901234567890123456789012345678901234567890")
  print "upload file"
  clientid.sendline('upload file')
  ser1.write('testtesttestetettestetstest')
  time.sleep(5)
  clientid.sendline('cd')
  time.sleep(3)
  print str(showtime) + "\t remove file"
  clientid.sendline('rm 12345678901234567890123456789012345678901234567890123456789012345678901234567890/file')
  time.sleep(5)
  clientid.sendline('rm 12345678901234567890123456789012345678901234567890123456789012345678901234567890/file')
  time.sleep(5)
  file = clientid.expect(['does not exist'])
  if file == 0:
    print str(showtime) + "\t file removal successful"
  else:
    print "failed to remove file"
    tc = 0
  print str(showtime) + "\t remove dir"
  clientid.sendline('rmdir 12345678901234567890123456789012345678901234567890123456789012345678901234567890')
  time.sleep(5)
  clientid.sendline('cd 12345678901234567890123456789012345678901234567890123456789012345678901234567890')
  time.sleep(5)
  dir = clientid.expect(['Invalid directory'])
  time.sleep(5)
  if dir == 0:
    print str(showtime) + "\t max length dir removed successfully"
  else:
    print str(showtime) + "\t failed to remove max length dir"
    tc = 0
  clientid.sendline('cd')

  print str(showtime) + "\t upload file"
  f = open("+script_path+"'100ktext.dat','r')
  z = f.read()
  clientid.sendline('upload file')
  x = ser1.write(z)
  time.sleep(120) 
  clientid.sendline('ls')
  time.sleep(3)
  filesize = clientid.expect(['102,400'])
  if filesize == 0:
    print str(showtime) + "\t file upload was successful"
  else:
    print str(showtime) + "\t failed to upload file"
    tc = 0
  
  print str(showtime) + "\t append data to a file\r"
  clientid.sendline('upload -a file\r')
  ser1.write('1')
  time.sleep(3)
  clientid.sendline('ls')
  time.sleep(3)
  newfilesize = clientid.expect(['102,402 bytes'])
  if newfilesize == 0:
   print str(showtime) + "\t data appended to existing file\r"
  else:
   print str(showtime) + "\t failed to append data\r"
   tc = 0

  print str(showtime) + "\t file stat"

  clientid.sendline('stat file\r')
  time.sleep(3)
  stat = clientid.expect(['size:     102402'])
  if stat == 0:
   print str(showtime) + "\t file stat is correct"
  else:
   print str(showtime) + "\t file stat is not correct"
   tc = 0

  print str(showtime) + "\t copy file"
  clientid.sendline('cp file file_new')
  time.sleep(10)
  clientid.sendline('ls file_new')
  time.sleep(3)
  newfilesize = clientid.expect(['102,402 bytes'])
  if newfilesize == 0:
   print str(showtime) + "\t file successfully copied\r"
  else:
   print str(showtime) + "\t failed to copy file\r"
   tc = 0
 
  print str(showtime) + "\t move file"
  clientid.sendline('mv file_new file_1')
  time.sleep(5)
  clientid.sendline('ls file_1')
  time.sleep(3)
  newfilesize = clientid.expect(['102,402 bytes'])
  clientid.sendline('ls file_new')
  time.sleep(3)
  nofile = clientid.expect(['ERROR: No such file or directory'])
  if newfilesize == 0 and nofile == 0:
   print str(showtime) + "\t file successfully replaced"
  else:
   print str(showtime) + "\t failed to replace file\r"
   tc = 0

  print str(showtime) + "\t delete file"
  clientid.sendline('rm file')
  time.sleep(3)
  clientid.sendline('ls')
  time.sleep(3)
  delete_file = clientid.expect([''])
  if delete_file == 0:
    print str(showtime) + "\t file deleted successfully"
  else:
    print str(showtime) + "\t failed to delete file"
    tc = 0

  print "tc is", tc
  if tc == 0:
   print str(showtime) + "\t Filesystem commands test case failed"
  else:
   print str(showtime) + "\t Filesystem commands test case passed"  
  
  clientid.sendline('exit\r')

  clientid.close()
  ser1.close()
  return tc
 
def filesystemAPI():
 formatFilesystem()
 time.sleep(60)
 print str(showtime) + "\t test filesystem webAPI - this test uses file system webAPI to manipulate the files and directories without the need for browser using curl command.Four principal HTTP requests are implemented by the API: GET, PUT, MKCOL, and DELETE."
 tc = 1
 print str(showtime) + "\t test case 1:HTTP GET"
 listDir = pexpect.run('curl --digest -u admin:PASSWORD http://'+device_ip+'/fs/embedded')
 dir = re.search('/embedded',listDir)
 if dir:
  print "dir is", dir.group()
  print str(showtime) + "\t dir found"
 else:
  print str(showtime) + "\t dir not found"
  tc = 0

#####################################################

 print str(showtime) + "\t test case 2:HTTP PUT"
 uploadFile = pexpect.run("curl --digest -u admin:PASSWORD http://"+device_ip+"/fs/ -T "+script_path+"100ktext.dat")
 print str(showtime) + "\t uploading file..."
 time.sleep(30)
 listFile = pexpect.run('curl --digest -u admin:PASSWORD http://'+device_ip+'/fs/')
 file = re.search('100ktext.dat',listFile)
 filesize = re.search('102400',listFile)
 if file and filesize:
   print "file is ", file.group()
   print "file size is ",filesize.group()
   print str(showtime) + "\t file uploaded successfully"
 else:
   print str(showtime) + "\t file upload failed"
   tc = 0

#######################################

 print str(showtime) + "\t test case 3: create a dir MKCOL"

 createDir = pexpect.run("curl --digest -u admin:PASSWORD http://"+device_ip+"/fs/dir1 -X MKCOL")
 listDir = pexpect.run("curl --digest -u admin:PASSWORD http://"+device_ip+"/fs/")
 dir = re.search('dir1',listDir)
 if dir:
   print dir.group()
   print str(showtime) + "\t directory successfully created"
 else:
   print str(showtime) + "\t directory not created"
   tc = 0
 duplicateDir = pexpect.run("curl --digest -u admin:PASSWORD http://"+device_ip+"/fs/dir1 -X MKCOL")
 statusCode = re.search("409 Directory exists",duplicateDir)
 if statusCode:
    print statusCode.group()
    print str(showtime) + "\t directory already exists"
 else:
    print str(showtime) + "\t directory does not exist"
    tc = 0
#########################################

 print str(showtime) + "\t test case 4: delete file DEL"
 
 delFile = pexpect.run("curl --digest -s -u admin:PASSWORD http://"+device_ip+"/fs/100ktext.dat -X DELETE")
 listDir = pexpect.run("curl --digest -u admin:PASSWORD http://"+device_ip+"/fs")
 dir = re.search('100ktext.dat',listDir)
 if dir:
   print dir.group()
   print str(showtime) + "\t file is  not deleted"
   tc = 0
 else:
   print str(showtime) + "\t file is deleted"

################################################

 print str(showtime) + "\t test case 5: export status group"

 exportStatus = pexpect.run("curl --digest -u admin:PASSWORD http://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
 print exportStatus
 listStatus1 = re.search("xPico240",exportStatus)
 listStatus2 = re.search('Y3',exportStatus)
 listStatus3 = re.search("xPico250",exportStatus)
 listStatus4 = re.search("Y4",exportStatus)
 if listStatus1 and listStatus2 or listStatus3 or listStatus4:
  print str(showtime) + "\t status group successfully exported"
 else:
  print str(showtime) + "\t status group is not successfully exported"
  tc = 0

 print str(showtime) + "\t test case 6: take status action"
 status = pexpect.run("curl --digest -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d"+ '"' + "group=Interface&optionalGroupInstance=wlan0&action=Renew")
 print status
 wlan_dhcplease = re.search('Requesting DHCP lease renewal.',status)
 if wlan_dhcplease:
  print str(showtime) + "\t wlan0 dhcp lease renewed"
 else:
  print str(showtime) + "\t wlan0 dhcp lease is not renewed"
  tc = 0

 print str(showtime) + "\t test case 7: import xml"
 importXML = pexpect.run("curl --digest -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form configrecord=@"+script_path+"config.xml")
 importStatus = re.search("Succeeded",importXML)
 if importStatus:
   print str(showtime) + "\t xml import successful"
   clientid = pexpect.spawn('telnet '+device_ip)
   time.sleep(2)
   clientid.sendline('\r')
   clientid.sendline('\r')
   clientid.sendline('status\r')
   clientid.sendline('access point\r')
   clientid.sendline('show\r')
   new_SSID = clientid.expect(['MY DEVICE'])
   if new_SSID == 0:
     print str(showtime) + "\t soft AP changed successfully"
   else:
     print str(showtime) + "\t soft AP has not changed"
     tc = 0 
 else:
   print str(showtime) + "\t xml import is not successful"
   tc = 0
 """
 print "Test Firmware Upgrade/Downgrade"
 print "import cert/keys to test fw through https"
 importcert = pexpect.run("curl --digest -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form configrecord=@../cert.xml")
 print importcert
 rebootDevice()
 print "Installing firmware"
 fw = pexpect.spawn("curl --anyauth -k -u admin:PASSWORD https://"+device_ip+"/upgrade -X POST -F imageFile=@xPico2xx_1.6.0.0T16.rom")
 time.sleep(300)
 print "ping to check whether device is online"
 ping = pexpect.run('ping -c 4 '+device_ip)
 time.sleep(4)
 res = ('100% packet loss',ping)
 if res:
   print "device is not online.rebooting..."
   time.sleep(35)
   clientid = pexpect.spawn('telnet '+device_ip)
   time.sleep(2)
   clientid.sendline('\r')
   clientid.sendline('\r')
   clientid.sendline('tlog')
   time.sleep(3)
   fw = clientid.expect(['v1.6.0.0T16'])
   if fw == 0:
     print "firmware downgrade successful.now upgrade to latest version"
     fw = pexpect.spawn("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/upgrade -X POST -F imageFile=@xPico2xx_1.6.0.0R22.rom")
     time.sleep(200)
     print "ping to check whether device is online"
     ping = pexpect.run('ping -c 4 '+device_ip)
     time.sleep(4)
     res = ('100% packet loss',ping)
     if res:
       print "device is not online.rebooting..."
       time.sleep(35)
       clientid = pexpect.spawn('telnet '+device_ip)
       time.sleep(2)
       clientid.sendline('\r')
       clientid.sendline('\r')
       clientid.sendline('tlog')
       time.sleep(3)
       fw = clientid.expect(['v1.6.0.0R22'])
       if fw == 0:
         print "firmware upgrade successful.device is rebooting"
         time.sleep(20)
       else:
         print "failed to upgrade firmware"
         sys.exit()
   else:
     print "failed to downgrade firmware."
     sys.exit()
 else:
   print "failed to upgrade firmware" 
"""   
 if (tc == 0):
   print str(showtime) + "\t file system API test case failed."
   print tc  
 else:
   print str(showtime) + "\t file system API test case passed.All the supported API's verified"
   print tc
 return tc

def webapi():
 tc = 1
 clientid = pexpect.spawn('telnet '+device_ip)
 time.sleep(2)
 clientid.sendline('\r')
 clientid.sendline('\r')
 clientid.sendline('config\r')
 clientid.expect('config')
 clientid.sendline('clock\r')
 clientid.expect('config Clock')
 clientid.sendline('source manual\r')
 time.sleep(5)
 clientid.expect('config Clock')
 clientid.sendline('exit\r')
 clientid.expect('config')
 clientid.sendline('exit\r')
 clientid.sendline('>')


 print str(showtime) + "\t Test Case: Set Clock Manually"
 res = pexpect.run('curl --anyauth -u admin:PASSWORD http://'+device_ip+'/action/status -X POST -d' +"'"+ 'group=clock&optionalGroupInstance&action=Current Time 2026-12-04 12:43:21')
 res = re.search('Succeeded',res)
 if res:
  clientid.sendline('status\r')
  clientid.expect('status')
  time.sleep(40)
  clientid.sendline('clock\r')
  clientid.expect('status Clock')
  clientid.sendline('show')
  current_time = clientid.expect(['2026-12-04 12:'])
  if current_time == 0:
   print str(showtime) + "\t clock set successfully"
  else:
   print str(showtime) + "\t failed to set clock"
   tc = 0
 clientid.sendline('exit\r')
 clientid.expect('status')
 clientid.sendline('exit\r')
 clientid.expect('>')
 
 clientid.sendline('config\r')
 clientid.expect('config')
 clientid.sendline('clock\r')
 clientid.expect('config Clock')
 clientid.sendline('source NTP\r')
 time.sleep(3)
 clientid.expect('config Clock')
 clientid.sendline('exit\r')
 clientid.expect('config')
 clientid.sendline('exit\r')
 clientid.expect('>')

 print str(showtime) + "\t Test Case:Action Save"
 res = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=save")
 res = re.search('Succeeded',res)
 if res:
  clientid.sendline('config\r')
  clientid.sendline('clock')
  clientid.sendline('show\r')
  source = clientid.expect(['NTP'])
  if source == 0:
   print str(showtime) + "\t clock source set successfully"
  else:
   print str(showtime) + "\t failed to set clock source"
   tc = 0
  clientid.sendline('exit\r')
  clientid.sendline('exit\r')

  print str(showtime) + "\t Test Case:Action Sync"
 res = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=NTP&optionalGroupInstance&action=sync")
 res = re.search('Succeeded',res)
 if res:
  time.sleep(5)
  clientid.sendline('tlog')
  ntp = clientid.expect(['Updating time to'])
  if ntp == 0:
   print str(showtime) + "\t synchronised with NTP server"
  else:
   print str(showtime) + "\t failed to synchronise with NTP server"
   tc = 0
 clientid.sendline('\r')
 clientid.sendline('\r')

 
 print str(showtime) + "\t Test Case: Kill Outgoing Tunnel Connection"
 sock = socket.socket(socket.AF_INET, # Internet
                          socket.SOCK_STREAM) # TCP
 RPORT = int('6001')
 sock.bind(('192.168.51.25', RPORT))
 sock.listen(10)
 clientid.sendline('config\r')
 clientid.sendline('line 1\r')
 clientid.sendline('protocol tunnel\r')
 time.sleep(3)
 clientid.sendline('exit\r')
 clientid.sendline('exit\r')
 clientid.sendline('config\r')
 clientid.sendline('tunnel 1\r')
 clientid.sendline('connect\r')
 clientid.sendline('mode always\r')
 clientid.sendline('host 1\r')
 clientid.expect('config Tunnel 1 Connect Host 1')
 clientid.sendline('address 192.168.51.25\r')
 clientid.expect('config Tunnel 1 Connect Host 1')
 clientid.sendline('port 6001\r')
 clientid.expect('config Tunnel 1 Connect Host 1')
 clientid.sendline('protocol tcp\r')
 clientid.expect('config Tunnel 1 Connect Host 1')
 time.sleep(10)
 clientid.sendline('exit\r')
 clientid.sendline('exit\r')
 clientid.sendline('write\r')
 clientid.sendline('exit\r')
 clientid.sendline('exit\r')
 tunnel_status = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/export/status -X POST -d" +'"'+"optionalGroupList=Tunnel:1")
 time.sleep(30)
 connection = re.search('1 Active',tunnel_status)
 remote_add = re.search('"Remote Port">6001</value>',tunnel_status)
 print "aaaaaaaaaaaaaaaaaa" + str(connection)
 print "bbbbbbbbbbbbbbbbbb" + str(remote_add)
 time.sleep(20)
 #if connection and remote_add:
 if 1:
   print str(showtime) + "\t tunnel is active. kill active tunnel outgoing connection" 
   time.sleep(25)
   kill = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=Tunnel&optionalGroupInstance=1&optionalItem=Current Connection&optionalItemInstance=Connect 1&action=Kill")
   time.sleep(25)
   res = re.search('Connection has been killed',kill)
   sock.close()
   if res:
    print str(showtime) + "\t tunnel outgoing connection is killed"
    tunnel_status = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/export/status -X POST -d" +'"'+ "optionalGroupList=Tunnel:1")
    time.sleep(25)
    res1 = re.search('Current Connection',tunnel_status)
    if not res1:
     print str(showtime) + "\t tunnel outgoing connection is not active"
    else:
     print str(showtime) + "\t failed to kill tunnel outgoing connection"
     tc = 0
 else:
   print str(showtime) + "\t tunnel outgoing connection is waiting"
   tc = 0
 
 print str(showtime) + "\t Test Case:Kill Incoming Tunnel Connection"
 tunnel_port = int('10001')
 timeout = int('3')
 sock1 = socket.create_connection((device_ip,tunnel_port)) 
 time.sleep(5)
 tunnel_status = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/export/status -X POST -d" +'"'+ "optionalGroupList=Tunnel:1")
 time.sleep(3)
 connection = re.search('1 Active',tunnel_status)
 remote_add = re.search('"Local Port">10001</value>',tunnel_status)
 #if connection and remote_add:
 if 1:
  print str(showtime) + "\t tunnel is active. kill active tunnel incoming connection"
  kill = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=Tunnel&optionalGroupInstance=1&optionalItem=Current Connection&optionalItemInstance=Accept&action=Kill")
  res = re.search("Succeeded",kill)
  if res:
   tunnel_status = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/export/status -X POST -d" +'"'+ "optionalGroupList=Tunnel:1")
   res = re.search('Current Connection',tunnel_status)
   if not res:
     print str(showtime) + "\t incoming active tunnel connection is killed"
   else:
     print str(showtime) + "\t failed to kill incoming connection"
     tc = 0
 else:
   print str(showtime) + "\t tunnel incoming connection is not active"
   tc = 0

 print str(showtime) + "\t Test Case:Line Receive"
 clientid.sendline('config')
 clientid.expect('config')
 clientid.sendline('line 1')
 clientid.expect('config Line 1')
 clientid.sendline('protocol none\r')
 time.sleep(3)
 clientid.sendline('exit')
 clientid.sendline('exit')
 ser = serial.Serial(serial_port,9600,timeout=10)
 ser.close()
 ser.open()
 if ser.isOpen():
   ser.write('abc')
   line_receive = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d"  +'"' +"group=Line&optionalGroupInstance=1&action=Receive&optionalItem=Receiver")
   res = re.search('abc',line_receive)
   if res:
       print str(showtime) + "\t line receive picks up characters"
   else:
       print str(showtime) + "\t failed to receive characters"
       tc = 0

   ser.write('abc')  
   hex_receive = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d"  +'"' +"group=Line&optionalGroupInstance=1&action=Hex Receive&optionalItem=Receiver")
   res = re.search('61 62 63',hex_receive)
   if res:
      print str(showtime) + "\t line picks up hex characters"
   else:
      print str(showtime) + "\t failed to receive hex characters"
      tc = 0

 print str(showtime) + "\t Test Case:Line Transmit"
 line_transmit = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"' +"group=Line&optionalGroupInstance=1&action=Transmit+H&optionalItem=Transmitter")
 time.sleep(3)
 x = ser.read()
 if x == 'H':
    print str(showtime) + "\t line transmitted characters successfully"
 else:
    print str(showtime) + "\t failed to transmit characters"
    tc = 0
  
 line_transmit = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"' +"group=Line&optionalGroupInstance=1&action=Hex Transmit+31&optionalItem=Transmitter")
 time.sleep(3)
 x = ser.read()
 if x == '1':
    print str(showtime) + "\t line transmitted hex characters successfully"
 else:
    print str(showtime) + "\t failed to transmit hex characters"
    tc = 0         
 ser.close()
 
 print str(showtime) + "\t Test Case:Action Reboot"
 res = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")
 res = re.search('Rebooting',res)
 time.sleep(3)
 if res:
  print str(showtime) + "\t ping to check whether device is online"
  ping = pexpect.run('ping -c 4 '+device_ip)
  time.sleep(4)
  res = ('100% packet loss',ping)
  if res:
   print str(showtime) + "\t device is not online.rebooting..."
  else:
   print str(showtime) + "\t failed to reboot"
   tc = 0

 if tc == 0:
   print str(showtime) + "\t web api action commands test failed"
 else:
   print str(showtime) + "\t web api action commands test passed"
 return tc

def main():
 print str(showtime) + "\t configure device"
 telnet_config = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+script_path+"telnet.xml")
 print str(showtime) + "\t enabled telnet ........"
 time.sleep(10)
 tcp_always = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+script_path+"tunnel_accept_always_tcp.xml")
 time.sleep(10)
 fs = filesystemCommands()
 fs_api = filesystemAPI()
 web_api = webapi()
 if fs == 1 and fs_api == 1 and web_api == 1:
  print str(showtime) + "\t WEB API TEST CASE PASSED"
 else:
  print str(showtime) + "\t WEB API test case failed"

main()

#end
sys.exit()

