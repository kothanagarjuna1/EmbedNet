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

print str(showtime) + "\t Test SMTP"
print str(showtime) + "\t ========="

def script_usage():
 print("Usage: " + os.path.basename(sys.argv[0]) + " <device_ip>" )
 return

if len(sys.argv) < 1:
    script_usage()
    sys.exit()

device_ip = sys.argv[1]

result = 0
def smtp(emailserver,user,password,emailid):
 print "Test",emailserver
 clientid = pexpect.spawn('telnet '+device_ip)
 #time.sleep(4)
 clientid.sendline('status')
 clientid.sendline('smtp')
 print "send email"
 clientid.sendline('send {0}'.format(emailserver))
 time.sleep(2)
 clientid.expect('Username:') 
 clientid.sendline('{0}'.format(emailid))
 time.sleep(2)
 clientid.expect('Password:')
 clientid.sendline('{0}'.format(password))
 time.sleep(3)
 clientid.expect('From:')
 clientid.sendline('{0}'.format(emailid))
 time.sleep(2)
 #clientid.expect('To:')
 clientid.sendline('{0}'.format(emailid))
 time.sleep(2)
 #clientid.expect('To:')
 clientid.sendline('pat@lantronix.com')
 time.sleep(2)
 #clientid.expect('To:')
 clientid.sendline('\r')
 clientid.expect('Subject:') 
 clientid.sendline('test smtp')
 time.sleep(2)
 #clientid.expect('Content:')
 clientid.sendline('line 1:123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890')
 time.sleep(2)
 #clientid.expect('Content:')
 clientid.sendline('line 2:')
 time.sleep(2)
 #clientid.expect('Content:')
 clientid.sendline('line 3:')
 time.sleep(2)
# clientid.expect('[Content]:')
 clientid.sendline('\r')
 time.sleep(2)
 mail = clientid.expect('Email successfully sent')
 if (mail == 0):
    print str(showtime) + "\t email successfully sent"
    result = 1
 else:
    print str(showtime) + "\t email failed to sent"
 clientid.close()
 return result
 

def smtpLive():
  result = smtp('smtp.live.com','naga.patindia@outlook.com','t35tingPAT','naga.patindia@outlook.com')
  return result  
def smtpGmail():
  result = smtp('smtp.gmail.com','naga.patindia@gmail.com','t35tingPAT','naga.patindia@gmail.com')
  return result
def smtpYahoo():
  result = smtp('smtp.mail.yahoo.com','naga.patindia2@yahoo.com','t35tingPAT2','naga.patindia2@yahoo.com')
  return result


def main():
 result_live = smtpLive()
 time.sleep(10)
 result_gmail = smtpGmail()
 time.sleep(10)
 result_yahoo = smtpYahoo()
 time.sleep(2)
 
 if ((result_live == 1) and (result_gmail == 1) and (result_yahoo == 1)):
    print "TEST CASE PASSED"
 else:
    print "TEST CASE FAILED"

main()

#end
sys.exit()

