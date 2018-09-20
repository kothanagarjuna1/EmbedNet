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
from shutil import copyfile
import glob


def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>"  + "<serial_port>" + "<firmware version>" + "<hardware>")
 return

if len(sys.argv) < 3:
    script_usage()
    sys.exit()


device_ip = sys.argv[1]
serial_port = sys.argv[2]
version = sys.argv[3] 
hardware = sys.argv[4] # xpico200 or xpicowifi

xml_path = "/home/ltrxengr/xpico200/xml/"
#cd /home/ltrxengr/"+hardware+"/firmware
#rm *.rom
#cd /home/ltrxengr/xpico200/scripts

if hardware == 'xpico200':
  dest_dir = "/home/ltrxengr/xpico200/firmware/"
elif hardware == 'xpicowifi':
  dest_dir = "/home/ltrxengr/xpw/firmware/"


def upload_cert():
 print "upload certificate and reboot device"
 x = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form configrecord=@../xml/cert.xml_notrustedauthority")
 print x
 pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")
 print "device is rebooting"
 time.sleep(100)

def reboot():
 print "reboot device"
 pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")
 time.sleep(40)

def fwVersion():
 ser = os.open(serial_port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY )
 ser = serial.Serial(serial_port,9600) # open the serial port
 serid = pexpect.fdpexpect.fdspawn(ser)
 time.sleep(5)

 print version
 serid.sendline('status')
 serid.sendline('device')
 serid.sendline('show')
 time.sleep(3)
 sdk_version = version+'.1'
 print sdk_version
 fw_version = serid.expect(sdk_version)
 if fw_version == 0:
   print "SDK built firmware upgrade successful"
   fw = 1
 else:
   print "SDK built firmware upgrade failed"
   fw = 0
 serid.sendline('exit')
 serid.sendline('exit')
 return fw


def moveFile():
 print "move firmware from local dir"
 for file in glob.glob(r'/home/ltrxengr/*.rom'):
    print(file)
    shutil.move(file, dest_dir)
    time.sleep(2)
 time.sleep(3)


moveFile()

def sdk(demo):
 

 ser = os.open(serial_port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY )
 ser = serial.Serial(serial_port,9600) # open the serial port
 serid = pexpect.fdpexpect.fdspawn(ser)
 time.sleep(5)

 if demo == 'hello world':
  print "Test Case 1: Hello World Demo"
  print "Upgrade built SDK Hello World rom"
  if hardware == 'xpico200': 
   fw = pexpect.run('curl --anyauth -k -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F imageFile=@'+dest_dir+'/helloDemo_'+version+'.1.0.rom',timeout=180)
   time.sleep(180)
  elif hardware == 'xpicowifi':
   up = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=Device&action=Firmware Upload")
   print up
   time.sleep(10)
   fw = pexpect.run('curl --anyauth -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F datafile=@'+dest_dir+'/helloDemo_'+version+'_1.0.rom',timeout=180)
   print fw
   time.sleep(25)
   reb = pexpect.run('curl --anyauth http://'+device_ip+'/reboot -X POST')
   print reb
   time.sleep(20)
   
  fwVersion()
  print "Verify serial port prints Hello World"
  serid.sendline('config')
  serid.sendline('line 1')
  serid.sendline('protocol hello world')
  time.sleep(3)
  serid.sendline('exit')
  serid.sendline('exit')
  serid.sendline('exit')
  time.sleep(5)
  res = serid.expect('Hello world')
  if res == 0:
   print "Test Case 1: Hello world demo Test Case Passed"
   res = 1
  else:
   print "Test Case 1: Hello world demo Test Case Failed" 
   res = 1
  reboot()

 if demo == 'echo':
   print "Test Case 2: Echo Demo"
   print "Upgrade built SDK echo rom"
   if hardware == 'xpico200':
    fw = pexpect.run('curl --anyauth -k -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F imageFile=@'+dest_dir+'/echoDemo_'+version+'.1.0.rom',timeout=180)
    time.sleep(180)
   elif hardware == 'xpicowifi':
    up = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=Device&action=Firmware Upload")
    print up
    time.sleep(10)
    fw = pexpect.run('curl --anyauth -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F datafile=@'+dest_dir+'/echoDemo_'+version+'_1.0.rom',timeout=180)
    print fw
    time.sleep(25)
    reb = pexpect.run('curl --anyauth http://'+device_ip+'/reboot -X POST')
    print reb
    time.sleep(20)

   fwVersion()
   print "Verify echo demo echoes back to the Line whatever it receives on the Line"
   serid.sendline('config')
   serid.sendline('line 1')
   serid.sendline('protocol echo')
   time.sleep(3)
   serid.sendline('exit')
   serid.sendline('exit')
   serid.sendline('exit')
   serid.sendline('exit')
   time.sleep(3)
   protocol = serid.expect('Echo')
   serid.sendline('123\r')
   data = serid.expect('123')
   if protocol == 0 and data == 0:
     print "data echoes back correctly"
     print "Test Case 2: Echo Demo Test Case Passed"
     res = 1
   else:
     print "data does not echo back"
     print "Test Case 2: Echo Demo Test Case Failed"
     res = 0
   reboot()

 if demo == 'tcp tunnel':
   print "Test Case 3: TCP Tunnel"
   print "Upgrade built SDK echo rom"
   if hardware == 'xpico200':
    fw = pexpect.run('curl --anyauth -k -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F imageFile=@'+dest_dir+'/tcpTunnelDemo_'+version+'.1.0.rom',timeout=180)
    time.sleep(180)
   elif hardware == 'xpicowifi':
    up = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=Device&action=Firmware Upload")
    print up
    time.sleep(10)
    fw = pexpect.run('curl --anyauth -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F datafile=@'+dest_dir+'/tcpTunnelDemo_'+version+'_1.0.rom',timeout=180)
    print fw
    time.sleep(25)
    reb = pexpect.run('curl --anyauth http://'+device_ip+'/reboot -X POST')
    print reb
    time.sleep(20)

   fwVersion()
   print "Verify data is sent through tcp tunnel"
   serid.sendline('config')
   serid.sendline('line 1')
   serid.sendline('protocol tcp tunnel')
   time.sleep(3)
   serid.sendline('exit')
   serid.sendline('exit')
   serid.sendline('exit')
   time.sleep(3)
   protocol = serid.expect('TCP Tunnel')
   tun_port = '10001'
   tun_port = int(tun_port)
   sock = socket.create_connection((device_ip,tun_port))
   time.sleep(3)
   sock.send('123\r')
   data = serid.expect('123')
   if protocol == 0 and data == 0:
     print "Data sent through tcp tunnel"
     print "Test Case 3: TCP Tunnel Test Case Passed"
     res = 1
   else:
     print "Data is not sent through tcp tunnel"
     print "Test Case 3: TCP Tunnel Test Case Failed"
     res = 0
   sock.close()
   reboot()


 if demo == 'programmatic scan':
   print "Test Case 4: programmaticScanDemo"
   print "Upgrade built SDK echo rom"
   if hardware == 'xpico200':
    fw = pexpect.run('curl --anyauth -k -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F imageFile=@'+dest_dir+'/programmaticScanDemo_'+version+'.1.0.rom',timeout=180)
    time.sleep(180)
   elif hardware == 'xpicowifi':
    up = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=Device&action=Firmware Upload")
    print up
    time.sleep(10)
    fw = pexpect.run('curl --anyauth -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F datafile=@'+dest_dir+'/programmaticScanDemo_'+version+'_1.0.rom',timeout=180)
    print fw
    time.sleep(25)
    reb = pexpect.run('curl --anyauth http://'+device_ip+'/reboot -X POST')
    print reb
    time.sleep(20)

   fwVersion()
   print "Verify tlog shows scan results of AP's within range"
   time.sleep(3)
   serid.sendline('tlog')
   time.sleep(4)
   rssi = serid.expect('RSSI')
   scan = serid.expect('Scan completed')
   if scan == 0 and rssi == 0:
     print "tlog shows scan results of AP's within range"
     print "Test Case 4: programmaticScanDemo Test Case Passed"
     res = 1
   else:
     print "tlog does not show scan results"
     print "Test Case 4: programmaticScanDemo Test Case Failed"
     res = 0
   reboot()
                                  
 if demo == 'xml access':
   print "Test Case 5: xmlAccessDemo"
   print "Upgrade built SDK rom"
   if hardware == 'xpico200':
    fw = pexpect.run('curl --anyauth -k -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F imageFile=@'+dest_dir+'xmlAccessDemo_'+version+'.1.0.rom',timeout=180)
    time.sleep(180)
   elif hardware == 'xpicowifi':
    up = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=Device&action=Firmware Upload")
    print up
    time.sleep(10)
    fw = pexpect.run('curl --anyauth -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F datafile=@'+dest_dir+'/xmlAccessDemo_'+version+'_1.0.rom',timeout=180)
    print fw
    time.sleep(25)
    reb = pexpect.run('curl --anyauth http://'+device_ip+'/reboot -X POST')
    print reb
    time.sleep(20)

   fwVersion()
   print "Verify read device status and configuration values via XML"
   time.sleep(3)
   serid.sendline('tlog')
   time.sleep(4)
   scan = serid.expect(version)
   if scan == 0:
     print "tlog shows correct firmware version"
     print "Test Case 5: xmlAccesDemo Test Case Passed"
     res = 1
   else:
     print "tlog does not show scan results"
     print "xmlAccessDemo Test Case Failed"
     res = 0
   reboot()
 
 if demo == "custom data":
   print "Test Case 6: customDataDemo"
   print "Upgrade built SDK rom"
   if hardware == 'xpico200':
    fw = pexpect.run('curl --anyauth -k -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F imageFile=@'+dest_dir+'/customDataDemo_'+version+'.1.0.rom',timeout=180)
    time.sleep(180)
   elif hardware == 'xpicowifi':
    up = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=Device&action=Firmware Upload")
    print up
    time.sleep(10)
    fw = pexpect.run('curl --anyauth -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F datafile=@'+dest_dir+'/customDataDemo_'+version+'_1.0.rom',timeout=180)
    print fw
    time.sleep(25)
    reb = pexpect.run('curl --anyauth http://'+device_ip+'/reboot -X POST')
    print reb
    time.sleep(20)

   fwVersion()
   pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"sdk_customdata.xml")   
   serid.sendline('tlog')
   name = serid.expect('test')
   serial_number = serid.expect('1234455')
   if name == 0 and serial_number == 0:
     print "customDataDemo Test Case Passed"
     res = 1
   else:
     print "customDataDemo Test Case Failed"
     res = 0

 if demo == 'power down':
   print "Test Case 7: powerDownDemo"
   print "Upgrade built SDK rom"
   if hardware == 'xpico200':
    fw = pexpect.run('curl --anyauth -k -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F imageFile=@'+dest_dir+'powerDownDemo_'+version+'.1.0.rom',timeout=180)
    time.sleep(180)
   elif hardware == 'xpicowifi':
    up = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=Device&action=Firmware Upload")
    print up
    time.sleep(10)
    fw = pexpect.run('curl --anyauth -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F datafile=@'+dest_dir+'/powerDownDemo_'+version+'_1.0.rom',timeout=180)
    print fw
    time.sleep(25)
    reb = pexpect.run('curl --anyauth http://'+device_ip+'/reboot -X POST')
    print reb
    time.sleep(20)

   fwVersion()
   print "import xml to configure power settings"
   x = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"sdk_power.xml")
   print x
   time.sleep(40)
   print "disable power. check tlog to confirm device woke up from standby"
   x = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+xml_path+"powerdisable.xml")
   print x
   serid.sendline('tlog')
   standby =  serid.expect('Waking from Standby')
   if standby == 0:
    print "Test Case 7: powerDownDemo Test Case Passed"
    res = 1
   else:
    print "Device does not power down as expected"
    print "Test Case 7: powerDownDemo Test Case Failed"
    res = 0

 if demo == 'mach10 serial api':
   print "Test Case 8: mach10SerialAPIDemo"
   print "Upgrade built SDK rom"
   fw = pexpect.run('curl --anyauth -k -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F imageFile=@'+dest_dir+'mach10SerialAPIDemo_'+version+'.1.0.rom',timeout=180)
   time.sleep(180)
   fwVersion()
   serid.sendline('config')
   serid.sendline('line 1')
   serid.sendline('protocol mach10 serial api')
   time.sleep(3)
   serid.sendline('exit')
   serid.sendline('exit')
   serid.sendline('exit')
   time.sleep(3)
   ser.write('mach10_getsettings~\r')
   time.sleep(10)
   bytesToRead = ser.inWaiting()
   serdata = ser.read(bytesToRead)
   print "serdata",serdata
   res = re.search('project_tag',serdata)
   if res:
    print "Mach10 serial API response successful.Test Case Passed"
    res = 1
   else:
    print "Mach10 serial API response failed.Test Case Failed"   
    res = 0

 if demo == 'udp tunnel':
   print "Test Case 9: udpTunnelDemo"
   print "Upgrade built SDK rom"
   if hardware == 'xpico200':
    fw = pexpect.run('curl --anyauth -k -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F imageFile=@'+dest_dir+'udpTunnelDemo_'+version+'.1.0.rom',timeout=180)
    time.sleep(180)
   elif hardware == 'xpicowifi':
    up = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=Device&action=Firmware Upload")
    print up
    time.sleep(10)
    fw = pexpect.run('curl --anyauth -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F datafile=@'+dest_dir+'/udpTunnelDemo_'+version+'_1.0.rom',timeout=180)
    print fw
    time.sleep(25)
    reb = pexpect.run('curl --anyauth http://'+device_ip+'/reboot -X POST')
    print reb
    time.sleep(20)

   fw = fwVersion()
   serid.sendline('config')
   serid.sendline('line 1')
   serid.sendline('protocol udp tunnel')
   time.sleep(3)
   serid.sendline('exit')
   serid.sendline('exit')
   serid.sendline('exit')
   time.sleep(3)
   res = serid.expect('UDP Tunnel')
   print res
   #sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
   udp_conn = pexpect.run('nc -v -u -n '+device_ip+' 10001',timeout = 30)
   time.sleep(10)
   print udp_conn
   conn_stat = re.search('succeeded',udp_conn)
   print conn_stat.group()
   conn_stat1 = serid.expect('Connected')
   print conn_stat1
   if fw == 1 and conn_stat1 == 0 and conn_stat:
     res =1 
     print "udTunnelDemo Test Case Passed. Only Firmware Upgrade is Verified due to an open bug with udp tunnel"
   else:
     print "udpTunnelDemo Test Case Failed"
     res = 0

 if demo == 'spi log':
   print "Test Case 10: spiLogDemo"
   print "Upgrade built SDK rom"
   if hardware == 'xpico200':
    fw = pexpect.run('curl --anyauth -k -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F imageFile=@'+dest_dir+'spiLogDemo_'+version+'.1.0.rom',timeout=180)
    time.sleep(180)
   elif hardware == 'xpicowifi':
    up = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=Device&action=Firmware Upload")
    print up
    time.sleep(10)
    fw = pexpect.run('curl --anyauth -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F datafile=@'+dest_dir+'/spiLogDemo_'+version+'_1.0.rom',timeout=180)
    print fw
    time.sleep(25)
    reb = pexpect.run('curl --anyauth http://'+device_ip+'/reboot -X POST')
    print reb
    time.sleep(20)

   res = fwVersion()
   serid.sendline('config')
   serid.sendline('spi')
   serid.sendline('protocol log')
   time.sleep(3)
   spi_log = serid.expect('config SPI')
   serid.sendline('exit')
   serid.sendline('exit')
   serid.sendline('exit')
   if res == 1 and spi_log == 0:
    print "spiLogDemo Test Case Passed. Only Firmware Upgrade is Verified for this demo.This demo requires customers to connect the spi-slave device"
    res = 1
   else:
    print "spiLogDemo Test Case Failed" 
    res = 0

 if demo == 'bt provisioning':
   print "Test Case 10: btOemProvisioningDemo"
   print "Upgrade built SDK rom"
   fw = pexpect.run('curl --anyauth -k -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F imageFile=@'+dest_dir+'btOemProvisioningDemo_'+version+'.1.0.rom',timeout=180)
   time.sleep(180)
   res = fwVersion()
   serid.sendline('config')
   serid.sendline('line 1')
   #serid.sendline('protocol log')
   #time.sleep(3)
   if res == 1:
    print "btProvisioningDemo Test Case Passed. Only Firmware Upgrade is Verified for this demo.This demo requires bluetooth app to connect to device"
    res = 1
   else:
    print "btProvisioningDemo Test Case Failed"
    res = 0

 if demo == 'configurable pin':
   print "Test Case 11 configurablePinDemo"
   print "Upgrade built SDK rom"
   if hardware == 'xpico200':
    fw = pexpect.run('curl --anyauth -k -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F imageFile=@'+dest_dir+'configurablePinDemo_'+version+'.1.0.rom',timeout=180)
    time.sleep(180)
   elif hardware == 'xpicowifi':
    up = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=Device&action=Firmware Upload")
    print up
    time.sleep(10)
    fw = pexpect.run('curl --anyauth -u admin:PASSWORD http://'+device_ip+'/upgrade -X POST -F datafile=@'+dest_dir+'/configurablePinDemo_'+version+'_1.0.rom',timeout=180)
    print fw
    time.sleep(25)
    reb = pexpect.run('curl --anyauth http://'+device_ip+'/reboot -X POST')
    print reb
    time.sleep(20)

   fwVersion()
   serid.sendline('config')
   serid.sendline('cpm')
   serid.sendline('role blinker')
   serid.sendline('CP 2')
   serid.sendline('state enabled')
   serid.sendline('show')
   time.sleep(3)
   cp = serid.expect('2')
   state = serid.expect('Enabled')
   if cp == 0 and state == 0:
    print "CP 2 assigned successfully.configurablePinDemo Example Test Case Passed"
    res = 1
   else:
    print "CP 2 assignment failed .configurablePinDemp Example Test Case Failed"
    res = 0
   
   reboot()

 if res == 1:
   print "SDK Demo Examples TEST CASE PASSED"
 else:
   print "SDK Demo Examples TEST CASE FAILED"


def main():
 if hardware == 'xpico200':
  #sdk('hello world')
 # sdk('echo')
  #sdk('tcp tunnel')
  #sdk('programmatic scan')
  #sdk('xml access')
  #sdk('custom data')
 # sdk('power down')    
 # sdk('mach10 serial api')
  #sdk('udp tunnel')
  sdk('spi log')
  sdk('bt provisioning')
  sdk('configurable pin')

 elif hardware == 'xpicowifi':
  reboot()
  sdk('hello world')
  sdk('echo')
  sdk('tcp tunnel')
  sdk('programmatic scan')
  sdk('xml access')
  sdk('custom data')
  sdk('power down')   
  sdk('udp tunnel')
  sdk('spi log')
  sdk('configurable pin')

main()
