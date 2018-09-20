#!/usr/local/bin/python3

import serial
import sys
import time
import os
#import fdpexpect
import pexpect.fdpexpect
import socket
import shutil
import subprocess
#import numpy
import re
#import requests

print "Test User Privilege"
print "==================="

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>" + "<secure flag>")
 return

if len(sys.argv) < 2:
    script_usage()
    sys.exit()

device_ip = sys.argv[1]
secure_flag = sys.argv[2] # values 1 or 0

print secure_flag

xml_path = '/home/lantronix/MIDAS/xml/'

if secure_flag == '0':
  http_var = "http://"+device_ip
elif secure_flag == '1':
  http_var = "-k https://"+device_ip

print http_var

def createUsers():

 if secure_flag == '1':
   print "import cert and keys for https"
   res = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/import/config -X POST --form configrecord=@"+xml_path+"cert.xml")
   print "import is",res
   reb = pexpect.run("curl --anyauth -u admin:PASSWORD http://"+device_ip+"/action/status -X POST -d" +'"'+ "group=device&optionalGroupInstance&action=reboot")     
   reb_res = re.search("Rebooting",reb)
   if reb_res:
     print "device is rebooting"
     time.sleep(60)
   else:
     print "failed to reboot" 
     sys.exit() 

 print http_var
 print "Format File System"
 res=pexpect.run("curl --anyauth -u admin:PASSWORD "+http_var+"/action/status -X POST -d  "+ '"'+ "group=File System&optionalGroupInstance&action=Format"+'"')
 print res
 
 print "Create Directories"
 dir = pexpect.run("curl --anyauth -u admin:PASSWORD "+http_var+"/fs/http -X MKCOL")
 pexpect.run("curl --anyauth -u admin:PASSWORD "+http_var+"/fs/http/hello -X MKCOL")
 pexpect.run("curl --anyauth -u admin:PASSWORD "+http_var+"/fs/http/login -X MKCOL")
 pexpect.run("curl --anyauth -u admin:PASSWORD "+http_var+"/fs/http/welcome -X MKCOL")
 pexpect.run("curl --anyauth -u admin:PASSWORD "+http_var+"/fs/http/hello1 -X MKCOL")

 print "Upload HTML Files"
 hello = pexpect.run("curl --anyauth -u admin:PASSWORD "+http_var+"/fs/http/hello/ -T "+xml_path+"hello.html")
 print hello
 pexpect.run("curl --anyauth -u admin:PASSWORD "+http_var+"/fs/http/login/ -T "+xml_path+"login.html")
 pexpect.run("curl --anyauth -u admin:PASSWORD "+http_var+"/fs/http/welcome/ -T "+xml_path+"welcome.html")
 pexpect.run("curl --anyauth -u admin:PASSWORD "+http_var+"/fs/http/hello1/ -T "+xml_path+"hello.html")

 print "Import xml"
 if secure_flag == '0': 
  res = pexpect.run("curl --anyauth -u admin:PASSWORD "+http_var+"/import/config -X POST --form configrecord=@"+xml_path+"userconfig.xml")
 else:
  res = pexpect.run("curl --anyauth -u admin:PASSWORD "+http_var+"/import/config -X POST --form configrecord=@"+xml_path+"userconfig.xml_tls")  
 print res
 time.sleep(20)
 userPrivilege()

def userPrivilege():
 tc = 1 
 print "Test Case 1: Privilege User"
 res = pexpect.run("curl --anyauth -u admin:PASSWORD "+http_var+"/welcome/welcome.html")
 admin = re.search('Welcome to my Website',res)
 res = pexpect.run("curl --anyauth -u user1:user1 "+http_var+"/welcome/welcome.html")
 user = re.search('Welcome to my Website',res)
 res = pexpect.run("curl --anyauth -u techuser:techuser "+http_var+"/welcome/welcome.html")
 techuser = re.search('Welcome to my Website',res)
 res = pexpect.run("curl --anyauth -u tech1:tech1 "+http_var+"/welcome/welcome.html")
 tech1 = re.search('Welcome to my Website',res)
 
 if admin and user and techuser and tech1:
   print "can login as admin,user and tech.test case passed"
 else:
   print "failed to login as one of the user. test case failed"
   tc = 0

 print "Test Case 2: Privilege Admin"

 res = pexpect.run("curl --anyauth -u admin:PASSWORD "+http_var+"/hello/hello.html")
 print "admin",res
 admin = re.search('A Small Hello',res)
 res = pexpect.run("curl --anyauth -u user1:user1 "+http_var+"/hello/hello.html")
 print "user",res
 user = re.search('Unauthorized username',res)
 res = pexpect.run("curl --anyauth -u techuser:techuser "+http_var+"/hello/hello.html")
 print "tech",res
 techuser = re.search('Unauthorized username',res)
 res = pexpect.run("curl --anyauth -u tech1:tech1 "+http_var+"/hello/hello.html")
 print "tech1",res
 tech1 = re.search('Unauthorized username',res)

 if admin and user and techuser and tech1:
   print "can login only as admin. cannot login as user or tech. test case passed"
 else:
   print "can login as user other than admin. test case failed"
   tc = 0

 print "tc is",tc

 print "Test Case 3: Privilege Tech"
 
 res = pexpect.run("curl --anyauth -u admin:PASSWORD "+http_var+"/hello1/hello.html")
 admin = re.search('A Small Hello',res)
 res = pexpect.run("curl --anyauth -u user1:user1 "+http_var+"/hello1/hello.html")
 user = re.search('Unauthorized username',res)
 res = pexpect.run("curl --anyauth -u techuser:techuser "+http_var+"/hello1/hello.html")
 techuser = re.search('A Small Hello',res)
 res = pexpect.run("curl --anyauth -u tech1:tech1 "+http_var+"/hello1/hello.html")
 tech1 = re.search('Unauthorized username',res)

 if admin and user and techuser and tech1:
  print "can login as admin and techuser. cannot login as user or tech1. test case passed"
 else:
  print "can login as user other than admin and techuser. test case failed"
  tc = 0
 
 print "Test Case 4: Privilege None"

 res = pexpect.run("curl --anyauth -u admin:PASSWORD "+http_var+"/login/login.html")
 admin = re.search('Unauthorized username',res)
 res = pexpect.run("curl --anyauth -u user1:user1 "+http_var+"/login/login.html")
 user = re.search('Unauthorized username',res)
 res = pexpect.run("curl --anyauth -u techuser:techuser "+http_var+"/login/login.html")
 techuser = re.search('Unauthorized username',res)
 res = pexpect.run("curl --anyauth -u tech1:tech1 "+http_var+"/login/login.html")
 tech1 = re.search('Unauthorized username',res)

 if admin and user and techuser and tech1:
  print "cannot login as admin,user,tech1 and techuser. test case passed"
 else:
  print  "can login as one of the user. test case failed"
  tc = 0

 print "Test Case 5: URI /"
 
 res = pexpect.run("curl --anyauth -u admin:PASSWORD "+http_var+"'")
 admin = re.search('Unauthorized username',res)
 res = pexpect.run("curl --anyauth -u user1:user1 "+http_var+"'")
 user = re.search('Unauthorized username',res)
 res = pexpect.run("curl --anyauth -u techuser:techuser "+http_var+"'")
 techuser = re.search('Unauthorized username',res)
 res = pexpect.run("curl --anyauth -u tech1:tech1 "+http_var+"'")
 tech1 = re.search('Unauthorized username',res)

 if not admin and user and techuser and tech1:
  print "can login only as admin. test case passed"
 else:
  print "can login as user other than admin. test case failed"
  tc = 0

 if tc == 1:
   print "User Roles TEST CASE PASSED"
 else:
   print "User Roles TEST CASE FAILED"
   
def main():
 createUsers()

main()

#end
sys.exit()

