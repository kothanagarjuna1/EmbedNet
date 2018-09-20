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
import subprocess
import time
from time import gmtime, strftime
import csv
import glob

#line = '1'
tunnel_port  = '10001'
FW_Version = '2.0.0.1R10_xport'


t = pexpect.run('mkdir ../test_report/'+FW_Version)
print t
os.chdir('../test_report/'+FW_Version)
"""
if line == '1':
 pexpect.run('mkdir line1')
 os.chdir('line1')
if line == '2':
 pexpect.run('mkdir line2')
 os.chdir('line2')
elif line == 'host_acm':
 pexpect.run('mkdir host_acm')
 os.chdir('host_acm')
"""
script_path = "/home/lantronix/MIDAS/test_report/"

cur = pexpect.run('pwd')
print cur


files_dict = {}

for files in glob.glob( "*" ):
    log = open( files, 'r' )
    file_contents =log.read()
    if "TEST CASE PASSED" in file_contents:
      print "Test Case "+ log.name + " Passed"
      files_dict[log.name] = "Passed"
    #f1 = open(files,'r')
    #file1_contents = f1.read()
    if "TEST CASE FAILED" in file_contents:
     print "Test Case "+ log.name + " Failed"
     files_dict[log.name] = "Failed"
    if "Traceback" in file_contents:
     print "Test Case "+ log.name + " Unfinished" 



#Final Report in CSV Format
with open(FW_Version+'_Test_Report_line.csv', 'w') as csvfile:
        DATE = pexpect.run('date')
        fieldnames = ['DATE', 'Date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        #writer.writeheader()
        writer.writerow(
            {'DATE':   'DATE',
             'Date': DATE}
        )


        fieldnames1 = ['Firmware Version', "Firmware_Version"]
        writer1 = csv.DictWriter(csvfile, fieldnames=fieldnames1)
        #writer1.writeheader()
        writer1.writerow(
           {'Firmware Version':  'Firmware Version',
            'Firmware_Version': FW_Version}
        )

        fieldnames2 = ['TEST_CASE', 'RESULT']
        writer2 = csv.DictWriter(csvfile, fieldnames=fieldnames2)
        writer2.writeheader()
        for TEST_CASE in files_dict:
                writer2.writerow(
                    {'TEST_CASE':        TEST_CASE,
                     'RESULT':           files_dict[TEST_CASE]}
                )

