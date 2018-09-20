import sys
import time
import os
import pexpect.fdpexpect
import pexpect
import socket
import shutil
import subprocess
import re
#import numpy
from time import gmtime, strftime

showtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())

#syntax

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>")
 return

if len(sys.argv) < 1:
    script_usage()
    sys.exit()

device_ip = sys.argv[1]
script_path = "/home/lantronix/MIDAS/xml"


def telnetDevice():
  clientid = pexpect.spawn('telnet '+device_ip)
  time.sleep(2)
  clientid.sendline('\r')
  clientid.sendline('\r')


def tlsVersion():
  print str(showtime) + "\t Test TLS version 1.2.Any client request with TLS version 1.0 and 1.1 will be rejected"
  tc = 1
  print str(showtime) + "\t import certificate and private key"
  tls = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form  configrecord=@"+script_path+"cert.xml")
  print str(showtime) + "\t Reboot" 
  pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d  "+'"'+  "group=Device&optionalGroupInstance&action=Reboot"+'"')
  time.sleep(60)
  clientid = pexpect.spawn('telnet '+device_ip)
  time.sleep(2)
  clientid.sendline('\r')
  clientid.sendline('\r') 
  clientid.sendline('config\r')
  clientid.expect('config')
  clientid.sendline('tls credential client\r')
  clientid.sendline('protocol tls1.2')
  clientid.sendline('write')
  tls_v = pexpect.run("curl --digest --tlsv1.0 -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
  print tls_v
  res = re.search('Error in protocol version',tls_v)
  if res:
     print str(showtime) + "\t protocol version mismatch error since tls version is 1.0 and device is 1.2. Test Passed"
     tls_v = pexpect.run("curl --digest --tlsv1.1 -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
     res = re.search('Error in protocol version',tls_v)
     if res:
       print str(showtime) + "\t protocol version mismatch error since tls version is 1.1 and device is 1.2. Test Passed"
     tls_v = pexpect.run("curl --digest --tlsv1.2 -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
     res = re.search('xPico',tls_v)
     if res:
        print str(showtime) + "\t web api command successful since tls version and device tls version is 1.2.Test Passed"
     else:
        print str(showtime) + "\t web api command Failed. Test Failed"
        tc = 0
  elif res == re.search('xPico',tls_v):
     print str(showtime) + "\t web api command successful even though tls version does not match.Test Failed"
     tc = 0


  print str(showtime) + "\t =========================================================="
  print str(showtime) + "\t Test TLS version 1.1.Any client request with TLS version 1.0 and 1.2 will be rejected"

  clientid.sendline('protocol tls1.1')
  clientid.sendline('write')
  tls_v = pexpect.run("curl --digest --tlsv1.0 -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
  print tls_v
  res = re.search('Error in protocol version',tls_v)
  if res:
     print str(showtime) + "\t protocol version mismatch error since tls version is 1.0 and device tls version is 1.1. Test Passed"
     tls_v = pexpect.run("curl --digest --tlsv1.2 -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
     print tls_v
     res = re.search('unsupported version',tls_v)
     if res:
       print str(showtime) + "\t protocol version mismatch error since tls version is 1.2 and device is 1.1. Test Passed"
       tls_v = pexpect.run("curl --digest --tlsv1.1 -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
       res = re.search('xPico',tls_v)
       if res:
        print str(showtime) + "\t web api command successful since tls version and device tls version is 1.1.Test Passed"
  elif res == re.search('xPico',tls_v):
     print str(showtime) + "\t web api command successful even though tls version does not match.Test Failed"
     tc = 0

 
  print str(showtime) + "\t ================================================================" 
  print str(showtime) + "\t Test TLS version 1.0.Any client request with TLS version 1.1 and 1.2 will be rejected"

  clientid.sendline('protocol tls1.0')
  clientid.sendline('write')
  tls_v = pexpect.run("curl --digest --tlsv1.1 -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
  print tls_v
  res = re.search('unsupported version',tls_v)
  if res:
     print str(showtime) + "\t protocol version mismatch error since tls version is 1.0 and device tls version is 1.1. Test Passed"
     tls_v = pexpect.run("curl --digest --tlsv1.2 -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
     print tls_v
     res = re.search('unsupported version',tls_v)
     if res:
       print str(showtime) + "\t protocol version mismatch error since tls version is 1.2 and device is 1.1. Test Passed"
       tls_v = pexpect.run("curl --digest --tlsv1.1 -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
       res = re.search('xPico',tls_v)
       if res:
        print str(showtime) + "\t web api command successful since tls version and device tls version is 1.1.Test Passed"
  elif res == re.search('xPico',tls_v):
     print str(showtime) + "\t web api command successful even though tls version does not match.Test Failed"
     tc = 0


  if tc == 0:
    print str(showtime) + "\t TLS version test case Failed"
  else:
    print str(showtime) + "\t TLS version test case Passed"
  
def main():
  pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=factory Defaults")
  time.sleep(2)
  print str(showtime) + "\t factory defaults the xpico240/250"
  time.sleep(2)
  print str(showtime) + "\t ..............................."
  time.sleep(2)
  print str(showtime) + "\t ..............................."
  time.sleep(5)
  print str(showtime) + "\t device is rebooting"
  tlsVersion()

main()

sys.exit()

import serial
import sys
import time
import os
import pexpect.fdpexpect
import pexpect
import socket
import shutil
import subprocess
import re
#import numpy
from time import gmtime, strftime

showtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())

#syntax

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>")
 return

if len(sys.argv) < 1:
    script_usage()
    sys.exit()

device_ip = sys.argv[1]


def telnetDevice():
  clientid = pexpect.spawn('telnet '+device_ip)
  time.sleep(2)
  clientid.sendline('\r')
  clientid.sendline('\r')


def tlsVersion():
  
  print str(showtime) + "\t Test TLS version 1.2.Any client request with TLS version 1.0 and 1.1 will be rejected"
  tc = 1
  clientid = pexpect.spawn('telnet '+device_ip)
  time.sleep(2)
  clientid.sendline('\r')
  clientid.sendline('\r') 
  clientid.sendline('config\r')
  clientid.expect('config')
  clientid.sendline('tls credential client\r')
  clientid.sendline('protocol tls1.2')
  clientid.sendline('write')
  tls_v = pexpect.run("curl --digest --tlsv1.0 -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
  print tls_v
  res = re.search('Error in protocol version',tls_v)
  if res:
     print str(showtime) + "\t protocol version mismatch error since tls version is 1.0 and device is 1.2. Test Passed"
     tls_v = pexpect.run("curl --digest --tlsv1.1 -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
     res = re.search('Error in protocol version',tls_v)
     if res:
       print str(showtime) + "\t protocol version mismatch error since tls version is 1.1 and device is 1.2. Test Passed"
     tls_v = pexpect.run("curl --digest --tlsv1.2 -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
     res = re.search('xPico',tls_v)
     if res:
        print str(showtime) + "\t web api command successful since tls version and device tls version is 1.2.Test Passed"
     else:
        print str(showtime) + "\t web api command Failed. Test Failed"
        tc = 0
  elif res == re.search('xPico',tls_v):
     print str(showtime) + "\t web api command successful even though tls version does not match.Test Failed"
     tc = 0


  print str(showtime) + "\t =========================================================="
  print str(showtime) + "\t Test TLS version 1.1.Any client request with TLS version 1.0 and 1.2 will be rejected"

  clientid.sendline('protocol tls1.1')
  clientid.sendline('write')
  tls_v = pexpect.run("curl --digest --tlsv1.0 -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
  print tls_v
  res = re.search('Error in protocol version',tls_v)
  if res:
     print str(showtime) + "\t protocol version mismatch error since tls version is 1.0 and device tls version is 1.1. Test Passed"
     tls_v = pexpect.run("curl --digest --tlsv1.2 -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
     print tls_v
     res = re.search('unsupported version',tls_v)
     if res:
       print str(showtime) + "\t protocol version mismatch error since tls version is 1.2 and device is 1.1. Test Passed"
       tls_v = pexpect.run("curl --digest --tlsv1.1 -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
       res = re.search('xPico',tls_v)
       if res:
        print str(showtime) + "\t web api command successful since tls version and device tls version is 1.1.Test Passed"
  elif res == re.search('xPico',tls_v):
     print str(showtime) + "\t web api command successful even though tls version does not match.Test Failed"
     tc = 0

 
  print str(showtime) + "\t ================================================================" 
  print str(showtime) + "\t Test TLS version 1.0.Any client request with TLS version 1.1 and 1.2 will be rejected"

  clientid.sendline('protocol tls1.0')
  clientid.sendline('write')
  tls_v = pexpect.run("curl --digest --tlsv1.1 -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
  print tls_v
  res = re.search('unsupported version',tls_v)
  if res:
     print str(showtime) + "\t protocol version mismatch error since tls version is 1.0 and device tls version is 1.1. Test Passed"
     tls_v = pexpect.run("curl --digest --tlsv1.2 -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
     print tls_v
     res = re.search('unsupported version',tls_v)
     if res:
       print str(showtime) + "\t protocol version mismatch error since tls version is 1.2 and device is 1.1. Test Passed"
       tls_v = pexpect.run("curl --digest --tlsv1.1 -k -u admin:PASSWORD https://"+device_ip+"/export/status -X POST -d"+ "optionalGroupList=Device")
       res = re.search('xPico',tls_v)
       if res:
        print str(showtime) + "\t web api command successful since tls version and device tls version is 1.1.Test Passed"
  elif res == re.search('xPico',tls_v):
     print str(showtime) + "\t web api command successful even though tls version does not match.Test Failed"
     tc = 0


  if tc == 0:
    print str(showtime) + "\t TLS version test case Failed"
  else:
    print str(showtime) + "\t TLS version test case Passed"
  
def main():
 tlsVersion()

main()

sys.exit()


import serial
import sys
import time
import os
import pexpect.fdpexpect
import pexpect
import socket
import shutil
import subprocess
#import numpy
from time import gmtime, strftime

showtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
#syntax

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>")
 return

if len(sys.argv) < 1:
    script_usage()
    sys.exit()

device_ip = sys.argv[1]

print str(showtime) + "\t Test Clock Source - manual and ntp"

def telnetDevice():
  clientid = pexpect.spawn('telnet '+device_ip)
  time.sleep(2)
  clientid.sendline('\r')
  clientid.sendline('\r')


def device_config():
  
  print str(showtime) + "\t Test clock source manual"
  clientid = pexpect.spawn('telnet '+device_ip)
  time.sleep(2)
  clientid.sendline('\r')
  clientid.sendline('\r') 
  clientid.sendline('config\r')
  clientid.expect('config')
  clientid.sendline('clock\r')
  clientid.sendline('source manual')
  clientid.sendline('exit')
  clientid.sendline('exit')
  clientid.sendline('status')
  clientid.sendline('clock')
  clientid.sendline('current Time 2016-09-09 18:12:34')
  time.sleep(4)
  clientid.sendline('show')
  current_time = clientid.expect('Current Time: 2016-09-09 18')
  if current_time == 0:
   print str(showtime) + "\t clock set correctly.clock source manual test passed"
  else:
   print str(showtime) + "\t failed to set time. clock source manual test failed"
  print str(showtime) + "\t Test clock source NTP"
  clientid.sendline('exit')
  clientid.sendline('exit')
  clientid.sendline('config')
  clientid.sendline('clock')
  time.sleep(5)
  clientid.sendline('source ntp')
  time.sleep(4)
  clientid.sendline('write')
  clientid.sendline('exit')
  clientid.sendline('exit')
  clientid.sendline('tlog')
  time.sleep(5)
  ntp = clientid.expect(['Starting NTP'])
  if ntp == 0:
    print str(showtime) + "\t ntp running"
    time.sleep(10)
    clientid.sendline('tlog')
    time.sleep(5)
    sync = clientid.expect(['Updating time'])
    if sync == 0:
     print str(showtime) + "\t device synchronised with ntp server.TEST PASSED"
     #print "test ntp sync time default 10 min"
     #print "reboot device"
     #reb = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")
     #print reb
     #time.sleep(60)
     #clientid = pexpect.spawn('telnet '+device_ip)
     #time.sleep(2)
     #clientid.sendline('\r')
     #clientid.sendline('\r')
     #clientid.sendline('config')
     #clientid.sendline('ntp')
    # clientid.sendline('sync time 10 min')
     #print "wait for sync time to expire.sleep 10 min"
     #time.sleep(605)
     #clientid.sendline('exit')
     #clientid.sendline('exit')
     #clientid.sendline('tlog')
     #sync = clientid.expect(['Updating time'])
     #if sync == 0:
      #print "device synchronised with ntp server after sync time.test passed"
     #else:
      #print "failed to synchronise with ntp server after sync time.test failed"
    else:
      print str(showtime) + "\t failed to synchronise with ntp server.test failed"
  else:
     print str(showtime) + "\t ntp server not running"
     sys.exit()


#main
device_config()

sys.exit()

