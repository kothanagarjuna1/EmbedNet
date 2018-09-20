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


def eds32pr():  
  print "Setting TCP AES credential in EDS32PR"

  clientid = pexpect.spawn('telnet 192.168.51.214')
  clientid.expect('>')
  time.sleep(3)
  clientid.sendline('enable\r')
  clientid.sendline('tunnel 1\r')
  if (connect_type == 'connect'):
    clientid.sendline('accept\r')
    clientid.sendline('protocol tcp aes\r')
    clientid.sendline('aes encrypt key 11111111111111111111111111111111\r')
    clientid.sendline('aes decrypt key 11111111111111111111111111111111\r')
    clientid.sendline('exit\r')
    clientid.sendline('exit\r')
    clientid.sendline('exit\r')
    clientid.sendline('\r')
  elif (connect_type == 'accept'):
    clientid.sendline('connect\r')
    clientid.sendline('connect mode always\r')
    clientid.sendline('host 1\r')
    lientid.sendline('address {0}'.format(device_ip))
    clientid.sendline('port 10001')
    clientid.sendline('protocol tcp aes\r')    
    clientid.sendline('aes encrypt key 11111111111111111111111111111111\r')
    clientid.sendline('aes decrypt key 11111111111111111111111111111111\r')
    clientid.sendline('exit\r')
    clientid.sendline('exit\r')
    clientid.sendline('exit\r')
    clientid.sendline('\r')


eds32pr()

sys.exit()