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
import csv
#sys.path.append('/home/lantronix/xport_edge/scripts/')
from common import print_f,telnet,xpico_factorydefaults,xpico_reboot,wlan_up,xport_CPM


def script_usage():
	print_f("Usage: " + os.path.basename(sys.argv[0]) + "<Device Name xpico/Edge>")
	return

if len(sys.argv) < 1:
	script_usage()
	sys.exit()

def subprocess_Popen(cmd, log_file):
	cmd_list = cmd.split(" ")
	proc=subprocess.Popen(
	    cmd_list, stdout=subprocess.PIPE, 
	    stderr=subprocess.STDOUT
	)
	output_log(log_file, proc)

#helper function call subprocess Popon class
#And write log to file

device_ip = "192.168.51.72"
serial_port = '/dev/ttyS5'
serial_port1 = '/dev/ttyS4'
wlan0_ip = '192.168.51.84'
vut_ip = '192.168.51.25' #should support sha-2
vut_serial_port = '/dev/ttyS7'
FW_Version = '1.9.0.2R1'
hardware = 'xpico200' #xpico200 or xport edge
line = '1'

t = pexpect.run('mkdir ../test_report/'+hardware+'/'+FW_Version)
print t
os.chdir('../test_report/'+FW_Version)
script_path = "/home/lantronix/MIDAS/scripts/"

def test_cases(cmd_str, saved_log):
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	subprocess_Popen(cmd_str, saved_log)
	time.sleep(5)


files_dict = {}
def output_log(file_name, process):
 logfile = open(file_name, 'w')
 files_dict[logfile.name] = "FAIL"
 for line in process.stdout:
   logfile.write(line)
   if re.search(r"\bTEST CASE PASSED\b", line):
     files_dict[logfile.name] = "PASS"
     process.wait()

if (hardware == 'xpico200'):
        if line == '1':
		pexpect.run('mkdir line1')
 		os.chdir('line1')
	if line == '2':
 		pexpect.run('mkdir line2')
 		os.chdir('line2')
	elif line == 'cdc_acm':
 		pexpect.run('mkdir cdc_acm')
 		os.chdir('host_acm')  

	
if hardware == 'xpico200' or hardware == 'xport edge':

	###############################################################################################################################################################################
	#1. OEM test cases 
	###############################################################################################################################################################################
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".........................TEST CASE : OEM SECURE FLAG ON.................................")
	xpico_factorydefaults(device_ip)
	wlan_up(device_ip)
	test_cases_proc('python '+script_path+'oem.py '+wlan0_ip+' 1 '+serial_port+'', "oem_FlagOn") 
	print_f(".........................TEST CASE : OEM SECURE FLAG OFF.................................")
	wlan_up(device_ip)
	test_cases_proc('python '+script_path+'oem.py '+wlan0_ip+' 0 '+serial_port+'', "oem_FlagOff")
	
	###############################################################################################################################################################################
	#2. User test cases 
	###############################################################################################################################################################################
	#Initial factory defaults the device
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	xpico_factorydefaults(device_ip)
	telnet(device_ip)
	print_f(".........................TEST CASE : USERS SECURE FLAG ON.................................")
	#test_cases_proc('python '+script_path+'users.py '+device_ip+' 1 ', "users_FlagON") 
	print_f(".........................TEST CASE : USERS SECURE FLAG OFF.................................")
	test_cases_proc('python '+script_path+'users.py '+device_ip+' 0 ', "users_FlagOff")

 	
 	###############################################################################################################################################################################
	#4. MUX test cases (TCP, TCP AES, TLS and UDP)
	###############################################################################################################################################################################
	#Initial factory defaults the device
	xpico_factorydefaults(device_ip)
	telnet(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f("...................TEST CASE : MUX TCP TCPAES TLS AND UDP...........................................")
	print_f("..................TEST CASE : MUX CONNECT TCP...........................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 connect tcp 1 eth0', "MUX_CONNECT_TCP")
	print_f("...................TEST CASE : MUX ACCEPT TCP .......................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 accept tcp 1 eth0', "MUX_ACCEPT_TCP")
	print_f("...................TEST CASE : MUX BOTH TCP............................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 both tcp 1 eth0', "MUX_BOTH_TCP")
	print_f("..................TEST CASE : MUX CONNECT TCPAES...........................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 connect tcpaes 1 eth0', "MUX_CONNECT_TCPAES")
	print_f("...................TEST CASE : MUX ACCEPT TCPAES .......................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 accept tcpaes 1 eth0', "MUX_ACCEPT_TCPAES")
	print_f("...................TEST CASE : MUX BOTH TCPAES............................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 both tcpaes 1 eth0', "MUX_BOTH_TCPAES")
	print_f("...................TEST CASE : MUX ACCEPT TCPAES .......................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 udp tcpaes 1 eth0', "MUX_ACCEPT_UDP")
	print_f("..................TEST CASE : MUX CONNECT TLS...........................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 connect tls 1 eth0', "MUX_CONNECT_TLS")
	print_f("...................TEST CASE : MUX ACCEPT TLS .......................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 accept tls 1 eth0', "MUX_ACCEPT_TLS")
	print_f("...................TEST CASE : MUX BOTH TCPAES............................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 both tls 1 eth0', "MUX_BOTH_TLS")
	
	
	###############################################################################################################################################################################
	#5. Tunnelling test cases (TCP, TCP AES, TLS and UDP)
	###############################################################################################################################################################################
	#Initial factory defaults the device
	VUT_factorydefaults(vut_ip)
	xpico_factorydefaults(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f("1: Test tunnel tcp accept mode always")
	test_cases_proc('python '+script_path+'tunnelling.py '+device_ip+' accept '+serial_port+' 10001 '+vut_ip+' tcp '+vut_serial_port+' always ', "Tunnel_TCP_accept_always") 
	print_f("2. Test tunnel tcp accept mode Any Character")
	test_cases_proc('python '+script_path+'tunnelling.py '+device_ip+' accept '+serial_port+' 10001 '+vut_ip+' tcp '+vut_serial_port+' anyCharacter ', "Tunnel_TCP_accept_AnyCharcter")
	print_f("3. Test tunnel tcp accept mode Start Character")
	test_cases_proc('python '+script_path+'tunnelling.py '+device_ip+' accept '+serial_port+' 10001 '+vut_ip+' tcp '+vut_serial_port+' startCharacter ', "Tunnel_TCP_accept_StartCharacter")

	#Initial factory defaults the device
	VUT_factorydefaults(vut_ip)
	xpico_factorydefaults(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f("1. Test tunnel tcp connect mode always")
	test_cases_proc('python '+script_path+'tunnelling.py '+device_ip+' connect '+serial_port+' 10001 '+vut_ip+' tcp '+vut_serial_port+' always ', "Tunnel_TCP_connect_always")
	print_f("2. Test tunnel tcp connect mode any character")
	test_cases_proc('python '+script_path+'tunnelling.py '+device_ip+' connect '+serial_port+' 10001 '+vut_ip+' tcp '+vut_serial_port+' anyCharacter ', "Tunnel_TCP_connect_AnyCharcter")
	print_f("3. Test tunnel tcp connect mode start character")
	test_cases_proc('python '+script_path+'tunnelling.py '+device_ip+' connect '+serial_port+' 10001 '+vut_ip+' tcp '+vut_serial_port+' startCharacter ', "Tunnel_TCP_connect_StartCharacter")

	#Initial factory defaults the device
	VUT_factorydefaults(vut_ip)
	xpico_factorydefaults(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f("1. Test tunnel TCP AES accept mode always")
	test_cases_proc('python '+script_path+'tunnelling.py '+device_ip+' accept '+serial_port+' 10001 '+vut_ip+' tcpaes '+vut_serial_port+' always ', "Tunnel_TCPAES_accept_always")
	print_f("2. Test tunnel TCP AES accept mode any character")
	test_cases_proc('python '+script_path+'tunnelling.py '+device_ip+' accept '+serial_port+' 10001 '+vut_ip+' tcpaes '+vut_serial_port+' anyCharacter ', "Tunnel_TCPAES_accept_AnyCharcter")
	print_f("3. Test tunnel TCP AES accept mode start character")
	test_cases_proc('python '+script_path+'tunnelling.py '+device_ip+' accept '+serial_port+' 10001 '+vut_ip+' tcpaes '+vut_serial_port+' startCharacter ', "Tunnel_TCPAES_accept_StartCharacter.txt")

	#Initial factory defaults the device
	VUT_factorydefaults(vut_ip)
	xpico_factorydefaults(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f("1. Test tunnel tcpaes connect mode always")
	test_cases_proc('python '+script_path+'tunnelling.py '+device_ip+' connect '+serial_port+' 10001 '+vut_ip+' tcpaes '+vut_serial_port+' always ', "Tunnel_TCPAES_connect_always")
	print_f("2. Test tunnel tcp aes connect mode any character")
	test_cases_proc('python '+script_path+'tunnelling.py '+device_ip+' connect '+serial_port+' 10001 '+vut_ip+' tcpaes '+vut_serial_port+' anyCharacter ', "Tunnel_TCPAES_connect_AnyCharcter")
	print_f("3. Test tunnel tcp aes connect mode start character")
	test_cases_proc('python '+script_path+'tunnelling.py '+device_ip+' connect '+serial_port+' 10001 '+vut_ip+' tcpaes '+vut_serial_port+' startCharacter ', "Tunnel_TCPAES_connect_StartCharacter.txt")


	#Initial factory defaults the device
	VUT_factorydefaults(vut_ip)
	xpico_factorydefaults(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f("1. Test tunnel tls accept mode always")
	test_cases_proc('python '+script_path+'tunnelling.py '+device_ip+' accept '+serial_port+' 10001 '+vut_ip+' tls '+vut_serial_port+' always ', "Tunnel_TLS_accept_always")
	print_f("2. Test tunnel tls accept mode any character")
	test_cases_proc('python '+script_path+'tunnelling.py '+device_ip+' accept '+serial_port+' 10001 '+vut_ip+' tls '+vut_serial_port+' anyCharacter ', "Tunnel_TLS_accept_AnyCharcter")
	print_f("3. Test tunnel tls accept mode start character")
	test_cases_proc('python '+script_path+'tunnelling.py '+device_ip+' accept '+serial_port+' 10001 '+vut_ip+' tls '+vut_serial_port+' startCharacter ', "Tunnel_TLS_accept_StartCharacter")

	#Initial factory defaults the device
	VUT_factorydefaults(vut_ip)
	xpico_factorydefaults(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f("1. Test tunnel tls connect mode always")
	test_cases_proc('python '+script_path+'tunnelling.py '+device_ip+' connect '+serial_port+' 10001 '+vut_ip+' tls '+vut_serial_port+' always ', "Tunnel_TLS_connect_always")
	print_f("2. Test tunnel tls connect mode any character")
	test_cases_proc('python '+script_path+'tunnelling.py '+device_ip+' connect '+serial_port+' 10001 '+vut_ip+' tls '+vut_serial_port+' anyCharacter ', "Tunnel_TLS_connect_AnyCharcter")
	print_f("3. Test tunnel tls connect mode start character")
	test_cases_proc('python '+script_path+'tunnelling.py '+device_ip+' connect '+serial_port+' 10001 '+vut_ip+' tls '+vut_serial_port+' startCharacter ', "Tunnel_TLS_connect_StartCharacter")
	
	###############################################################################################################################################################################
	#6. TUNNEL UDP test cases
	###############################################################################################################################################################################
	#Initial factory defaults the device
	xpico_factorydefaults(device_ip)
	telnet(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f("..............................TEST CASE : TUNNEL UDP RESTRICTED ACTIVE.........................")
	test_cases_proc('python '+script_path+'tunneludp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 restricted 1 active eth0', "TUNNEL_UDP_RESTRICTED_ACTIVE" )
	print_f("..............................TEST CASE : TUNNEL UDP RESTRICTED PASSIVE........................")
	test_cases_proc('python '+script_path+'tunneludp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 restricted 1 passive eth0', "TUNNEL_UDP_RESTRICTED_PASSIVE")
	print_f("..............................TEST CASE : TUNNEL UDP UNRESTRICTED ACTIVE.......................")
	test_cases_proc('python '+script_path+'unneludp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 unrestricted 1 active eth0', "TUNNEL_UDP_UNRESTRICTED_ACTIVE")
	print_f("..............................TEST CASE : TUNNEL UDP UNRESTRICTED PASSIVE......................")
	test_cases_proc('python '+script_path+'tunneludp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 unrestricted 1 passive eth0', "TUNNEL_UDP_UNRESTRICTED_PASSIVE")
	print_f("..............................TEST CASE : TUNNEL UNRESTRICTED ACTIVE............................")
	test_cases_proc('python '+script_path+'tunneludp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 unrestricted 0 active eth0', "TUNNEL_UNRESTRICTED_ACTIVE")
	print_f("..............................TEST CASE : TUNNEL RESTRICTED ACTIVE............................")
	test_cases_proc('python '+script_path+'tunneludp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 restricted 0 active eth0', "TUNNEL_RESTRICTED_ACTIVE")

	#Initial factory defaults the device
	xpico_factorydefaults(device_ip)
	test_cases_proc ('python '+script_path+'tunnelconnect.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 192.168.51.177 hel', "TUNNEL_CONNECT_MODE")

	###############################################################################################################################################################################
	#7. File system and webapi test cases
	###############################################################################################################################################################################
	#Initial factory defaults the device
	xpico_factorydefaults(device_ip)
	wlan_up(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".........................TEST CASES : FILE SYSTEM AND WEB API.................................")
	test_cases_proc('python '+script_path+'fswebapi.py '+device_ip+' '+serial_port+'', "FILE_SYSTEM_AND_WEB_API") 

	###############################################################################################################################################################################
	#9. CLOCK test case
	###############################################################################################################################################################################
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".........................TEST CASE : CLOCK.................................")
	telnet(device_ip)
	test_cases_proc('python '+script_path+'clock.py '+device_ip+'', "CLOCK") 
	###############################################################################################################################################################################
	#10. HTTPS SERVER test case
	###############################################################################################################################################################################
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".........................TEST CASE : HTTP SERVER.................................")
	test_cases_proc('python '+script_path+'http_server.py '+device_ip+'', " HTTP_SERVER") 

	###############################################################################################################################################################################
	#11. TLS_VERSION test case
	###############################################################################################################################################################################
	xpico_factorydefaults(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".........................TEST CASE : TLS VERSION.................................")
	test_cases_proc('python '+script_path+'tls_version.py '+device_ip+'', "TLS_VERSION") 

	##############################################################################################################################################################################
	#12. Reboot test case
	###############################################################################################################################################################################
	#Initial factory defaults the device
	xpico_factorydefaults(device_ip)
	wlan_up(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".........................TEST CASE : REBOOT.................................")
	test_cases_proc('python '+script_path+'reboot.py '+device_ip+' '+wlan0_ip+' '+serial_port+'', "REBOOT") 

	###############################################################################################################################################################################
	#13. Mach10 test cases
	###############################################################################################################################################################################
	#Initial factory defaults the device
	telnet(device_ip)
	print_f(".........................TEST CASE : MACH10 FIRMWARE UPDATE.................................")
	test_cases_proc('python '+script_path+'mach10.py '+device_ip+' FW', "MACH10 FIRMWARE UPDATE") 
	print_f(".........................TEST CASE : MACH10 CONFIG UPDATE.................................")
	test_cases_proc('python '+script_path+'mach10.py '+device_ip+' config', "MACH10 CONFIG UPDATE") 

	###############################################################################################################################################################################
	#14. TLS Tunnel server and client test cases
	###############################################################################################################################################################################
	#Initial factory defaults the device
	xpico_factorydefaults(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".........................TEST CASE : TLS SERVER.................................")
	test_cases_proc('python '+script_path+'tls.py_server '+device_ip+' '+serial_port+' 1 1', "TLS_SERVER") 
	print_f(".........................TEST CASE : TLS CLIENT.................................")
	test_cases_proc('python '+script_path+'tls.py_server '+device_ip+' '+serial_port+' 1 0', "TLS_CLIENT") 

	###############################################################################################################################################################################
	#15. Modem Emulation test cases
	###############################################################################################################################################################################
	xpico_factorydefaults(device_ip)
	telnet(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".........................TEST CASE : Modem Emulation............................")
	test_cases_proc ('python '+script_path+'modememul.py '+serial_port+' 9600 8 N 1 '+device_ip+' 6001 ../5ktext.dat', "Modem_Emulation")

	###############################################################################################################################################################################
	#16. Virtual line test cases
	###############################################################################################################################################################################
	xpico_factorydefaults(device_ip)
	telnet(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".........................TEST CASE : Virtual lines............................")
	test_cases_proc ('python '+script_path+'virtual_linel.py '+device_ip+' '+serial_port+'', "Virtual_Line")
	
	###############################################################################################################################################################################
	#17. Host_ACM test cases
	###############################################################################################################################################################################
	#Initial factory defaults the device
	xpico_factorydefaults(device_ip)
	telnet(device_ip)
	USB_HOST_up(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f("..............................TEST CASE : TUNNEL UDP RESTRICTED ACTIVE HOST.........................")
	test_cases_proc('python '+script_path+'tunneludp.py_acm '+serial_port1+' 115200 8 N 1 '+device_ip+' 10002 restricted 1 active eth0', "TUNNEL_UDP_RESTRICTED_ACTIVE_HOST_ACM" )
	print_f("..............................TEST CASE : TUNNEL UDP RESTRICTED PASSIVE HOST........................")
	test_cases_proc('python '+script_path+'tunneludp.py_acm '+serial_port1+' 115200 8 N 1 '+device_ip+' 10002 restricted 1 passive eth0', "TUNNEL_UDP_RESTRICTED_PASSIVE_HOST_ACM")
	print_f("..............................TEST CASE : TUNNEL UDP UNRESTRICTED ACTIVE HOST.......................")
	test_cases_proc('python '+script_path+'tunneludp.py_acm '+serial_port1+' 115200 8 N 1 '+device_ip+' 10002 unrestricted 1 active eth0', "TUNNEL_UDP_UNRESTRICTED_ACTIVE_HOST_ACM")
	print_f("..............................TEST CASE : TUNNEL UDP UNRESTRICTED PASSIVE HOST......................")
	test_cases_proc('python '+script_path+'tunneludp.py_acm '+serial_port1+' 115200 8 N 1 '+device_ip+' 10002 unrestricted 1 passive eth0', "TUNNEL_UDP_UNRESTRICTED_PASSIVE_HOST_ACM")
	print_f("..............................TEST CASE : TUNNEL UNRESTRICTED ACTIVE HOST............................")
	test_cases_proc('python '+script_path+'tunneludp.py_acm '+serial_port1+' 115200 8 N 1 '+device_ip+' 10002 unrestricted 0 active eth0', "TUNNEL_UNRESTRICTED_ACTIVE_HOST_ACM")
	print_f("..............................TEST CASE : TUNNEL RESTRICTED ACTIVE HOST............................")
	test_cases_proc('python '+script_path+'tunneludp.py_acm '+serial_port1+' 115200 8 N 1 '+device_ip+' 10002 restricted 0 active eth0', "TUNNEL_RESTRICTED_ACTIVE_HOST_ACM")

	#Initial factory defaults the device
	xpico_factorydefaults(device_ip)
	telnet(device_ip)
	USB_HOST_up(device_ip)
	wlan_up(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f("..............................TEST CASE : TUNNEL UDP UNRESTRICTED PASSIVE HOST WLAN0......................")
	test_cases_proc('python '+script_path+'tunneludp.py_acm '+serial_port1+' 115200 8 N 1 '+wlan0_ip+' 10002 unrestricted 1 passive wlan0', "TUNNEL_UDP_UNRESTRICTED_PASSIVE_wlan0_HOST_ACM")
	print_f("..............................TEST CASE : TUNNEL UDP RESTRICTED PASSIVE HOST WLAN0........................")
	test_cases_proc('python '+script_path+'tunneludp.py_acm '+serial_port1+' 115200 8 N 1 '+wlan0_ip+' 10002 restricted 1 passive wlan0', "TUNNEL_UDP_RESTRICTED_PASSIVE_wlan0_HOST_ACM")

	
	###############################################################################################################################################################################
	#18. MUX test cases (TCP AES and TLS)
	###############################################################################################################################################################################
	#Initial factory defaults the device
	VUT_factorydefaults(device_ip)
	xpico_factorydefaults(device_ip)
	telnet(device_ip)
	USB_HOST_up(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".....................TEST CASE : MUX TLS ACCEPT MODE HOST..................................")
	test_cases_proc('python '+script_path+'mux_tls_aes.py '+device_ip+' '+serial_port1+' 10001 '+vut_ip+' '+vut_serial_port+' connect tls', "MUX_TLS_CONNECT_MODE_HOST_ACM") 
	print_f(".....................TEST CASE : MUX TLS CONNECT MODE HOST..................................")
	test_cases_proc('python '+script_path+'mux_tls_aes.py '+device_ip+' '+serial_port1+' 10001 '+vut_ip+' '+vut_serial_port+' accept tls', "MUX_TLS_ACCEPT_MODE_HOST_ACM")

	VUT_factorydefaults(device_ip)
	xpico_factorydefaults(device_ip)
	telnet(device_ip)
	USB_HOST_up(device_ip) 
	print_f("....................TEST CASE : MUX TCP AES ACCEPT MODE HOST................................")
	test_cases_proc('python '+script_path+'mux_tls_aes.py '+device_ip+' '+serial_port1+' 10001 '+vut_ip+' '+vut_serial_port+' connect tcpaes', "MUX_TCPAES_CONNECT_MODE_HOST_ACM") 
	print_f("....................TEST CASE : MUX TLS ACCEPT MODE HOST.....................................")
	test_cases_proc('python '+script_path+'mux_tls_aes.py '+device_ip+' '+serial_port1+' 10001 '+vut_ip+' '+vut_serial_port+' accept tcpaes', "MUX_TCPAES_ACCEPT_MODE_HOST_ACM") 
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	
	#Initial factory defaults the device
	xpico_factorydefaults(device_ip)
	telnet(device_ip)
	USB_HOST_up(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f("..................TEST CASE : MUX CONNECT TCP HOST...........................................")
	test_cases_proc ('python '+script_path+'mux_host.py '+serial_port1+' 115200 8 N 1 '+device_ip+' 10002 1 192.168.51.177 connect tcp 1 eth0', "MUX_CONNECT_TCP_HOST_ACM")
	print_f("...................TEST CASE : MUX ACCEPT TCP HOST .......................................")
	test_cases_proc ('python '+script_path+'mux_host.py '+serial_port1+' 115200 8 N 1 '+device_ip+' 10002 1 192.168.51.177 accept tcp 1 eth0', "MUX_ACCEPT_TCP_HOST_ACM")
	print_f("...................TEST CASE : MUX ACCEPT UDP HOST............................................")
	test_cases_proc ('python '+script_path+'mux_host.py '+serial_port1+' 1152000 8 N 1 '+device_ip+' 10002 1 192.168.51.177 accept udp 1 eth0', "MUX_ACCEPT_UDP_HOST_ACM")
	
	#Initial factory defaults the device
	xpico_factorydefaults(device_ip)
	telnet(device_ip)
	USB_HOST_up(device_ip)
	wlan_up(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f("..................TEST CASE : MUX CONNECT TCP HOST WLAN0...........................................")
	test_cases_proc ('python '+script_path+'mux_host.py '+serial_port1+' 115200 8 N 1 '+wlan0_ip+' 10002 1 192.168.51.177 connect tcp 1 wlan0', "MUX_CONNECT_TCP_wlan0_HOST_ACM")
	print_f("...................TEST CASE : MUX ACCEPT TCP HOST WLAN0............................................")
	test_cases_proc ('python '+script_path+'mux_host.py '+serial_port1+' 115200 8 N 1 '+wlan0_ip+' 10002 1 192.168.51.177 accept tcp 1 wlan0', "MUX_ACCEPT_TCP_wlan0_HOST_ACM")
	print_f("...................TEST CASE : MUX ACCEPT UDP HOST WLAN0............................................")
	test_cases_proc ('python '+script_path+'mux_host.py '+serial_port1+' 115200 8 N 1 '+wlan0_ip+' 10002 1 192.168.51.177 accept udp 1 wlan0', "MUX_ACCEPT_UDP_wlan0_HOST_ACM")
	
	###############################################################################################################################################################################
	#19. File system and webapi test cases
	###############################################################################################################################################################################
	#Initial factory defaults the device
	xpico_factorydefaults(device_ip)
	telnet(device_ip)
	USB_HOST_up(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".........................TEST CASES : FILE SYSTEM AND WEB API HOST.................................")
	test_cases_proc('python '+script_path+'fswebapi.py_host '+device_ip+' '+serial_port1+' host_cdc_acm', "FILE_SYSTEM_AND_WEB_API_HOST_ACM") 

	###############################################################################################################################################################################
	#20. modem_emulation_host
	###############################################################################################################################################################################
	#Initial factory defaults the device
	xpico_factorydefaults(device_ip)
	USB_HOST_up(device_ip)
	telnet(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".........................TEST CASES : Modem Emulation HOST.................................")
	test_cases_proc('python '+script_path+'modememul.py_hostacm '+serial_port1+' 115200 8 N 1 '+device_ip+' 6001 ../5ktext.dat host_cdc_acm', "MODEM_EMULATION_HOST_ACM") 
	
	###############################################################################################################################################################################
	#21. Tunnel connect simultanious and round_robin test cases
	###############################################################################################################################################################################
	xpico_factorydefaults(device_ip)
	telnet(device_ip)
	USB_HOST_up(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".........................TEST CASES : Tunnel connect simultanious and round_robin test cases HOST.................................")
	test_cases_proc('python '+script_path+'tunnelconnect1.py '+serial_port1+' 115200 8 N 1 '+device_ip+' 10002 192.168.51.177 hel', "TUNNEL_CONNECT_HOST_ACM") 

	###############################################################################################################################################################################
	#22. Virtual line test cases
	###############################################################################################################################################################################
	#xpico_factorydefaults(device_ip)
	telnet(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".........................TEST CASE : Virtual lines............................")
	test_cases_proc ('python '+script_path+'virtual_line.py '+device_ip+' '+serial_port+'', "Virtual_Line")
	

if hardware == 'xpico200'


	print_f("xpico200 device selected to run automation")
	###############################################################################################################################################################################
	#1. User test cases 
	###############################################################################################################################################################################
	#Initial factory defaults the device
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	xpico_factorydefaults(device_ip)
	telnet(device_ip)
	xport_CPM(device_ip)
	print_f(".........................TEST CASE : USERS SECURE FLAG ON.................................")
	#test_cases_proc('python '+script_path+'users.py '+device_ip+' 1 ', "users_FlagON") 
	print_f(".........................TEST CASE : USERS SECURE FLAG OFF.................................")
	test_cases_proc('python '+script_path+'users.py '+device_ip+' 0 ', "users_FlagOff")

	###############################################################################################################################################################################
	#2. TUNNEL UDP test cases
	###############################################################################################################################################################################
	#Initial factory defaults the device
	xpico_factorydefaults(device_ip)
	telnet(device_ip)
	xport_CPM(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f("..............................TEST CASE : TUNNEL UDP RESTRICTED ACTIVE.........................")
	test_cases_proc('python '+script_path+'tunneludp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 restricted 1 active eth0', "TUNNEL_UDP_RESTRICTED_ACTIVE" )
	print_f("..............................TEST CASE : TUNNEL UDP RESTRICTED PASSIVE........................")
	test_cases_proc('python '+script_path+'tunneludp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 restricted 1 passive eth0', "TUNNEL_UDP_RESTRICTED_PASSIVE")
	print_f("..............................TEST CASE : TUNNEL UDP UNRESTRICTED ACTIVE.......................")
	test_cases_proc('python '+script_path+'unneludp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 unrestricted 1 active eth0', "TUNNEL_UDP_UNRESTRICTED_ACTIVE")
	print_f("..............................TEST CASE : TUNNEL UDP UNRESTRICTED PASSIVE......................")
	test_cases_proc('python '+script_path+'tunneludp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 unrestricted 1 passive eth0', "TUNNEL_UDP_UNRESTRICTED_PASSIVE")
	print_f("..............................TEST CASE : TUNNEL UNRESTRICTED ACTIVE............................")
	test_cases_proc('python '+script_path+'tunneludp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 unrestricted 0 active eth0', "TUNNEL_UNRESTRICTED_ACTIVE")
	print_f("..............................TEST CASE : TUNNEL RESTRICTED ACTIVE............................")
	test_cases_proc('python '+script_path+'tunneludp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 restricted 0 active eth0', "TUNNEL_RESTRICTED_ACTIVE")


	xpico_factorydefaults(device_ip)
	telnet(device_ip)
	print_f("...................TEST CASE : TUNNEL CONNECT MODE........................................")
	test_cases_proc ('python '+script_path+'tunnelconnect.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 192.168.51.177 hel', "TUNNEL_CONNECT_MODE")

	###############################################################################################################################################################################
	#3. MUX test cases (TCP, TCP AES, TLS and UDP)
	###############################################################################################################################################################################
	#Initial factory defaults the device
	xpico_factorydefaults(device_ip)
	telnet(device_ip)
	xport_CPM(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f("...................TEST CASE : MUX TCP TCPAES TLS AND UDP...........................................")
	print_f("..................TEST CASE : MUX CONNECT TCP...........................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 connect tcp 1 eth0', "MUX_CONNECT_TCP")
	print_f("...................TEST CASE : MUX ACCEPT TCP .......................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 accept tcp 1 eth0', "MUX_ACCEPT_TCP")
	print_f("...................TEST CASE : MUX BOTH TCP............................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 both tcp 1 eth0', "MUX_BOTH_TCP")
	print_f("..................TEST CASE : MUX CONNECT TCPAES...........................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 connect tcpaes 1 eth0', "MUX_CONNECT_TCPAES")
	print_f("...................TEST CASE : MUX ACCEPT TCPAES .......................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 accept tcpaes 1 eth0', "MUX_ACCEPT_TCPAES")
	print_f("...................TEST CASE : MUX BOTH TCPAES............................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 both tcpaes 1 eth0', "MUX_BOTH_TCPAES")
	print_f("...................TEST CASE : MUX ACCEPT TCPAES .......................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 udp tcpaes 1 eth0', "MUX_ACCEPT_UDP")
	print_f("..................TEST CASE : MUX CONNECT TLS...........................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 connect tls 1 eth0', "MUX_CONNECT_TLS")
	print_f("...................TEST CASE : MUX ACCEPT TLS .......................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 accept tls 1 eth0', "MUX_ACCEPT_TLS")
	print_f("...................TEST CASE : MUX BOTH TCPAES............................................")
	test_cases_proc ('python '+script_path+'mux8tcp.py '+serial_port+' 9600 8 N 1 '+device_ip+' 10001 1 192.168.51.177 both tls 1 eth0', "MUX_BOTH_TLS")
	
	###############################################################################################################################################################################
	#4. File system and webapi test cases
	###############################################################################################################################################################################
	#Initial factory defaults the device
	xpico_factorydefaults(device_ip)
	wlan_up(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".........................TEST CASES : FILE SYSTEM AND WEB API.................................")
	test_cases_proc('python '+script_path+'fswebapi.py '+device_ip+' '+serial_port+'', "FILE_SYSTEM_AND_WEB_API") 
	
	###############################################################################################################################################################################
	#6. HTTPS SERVER test case
	###############################################################################################################################################################################
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".........................TEST CASE : HTTP SERVER.................................")
	test_cases_proc('python '+script_path+'http_server.py '+device_ip+'', " HTTP_SERVER") 

	###############################################################################################################################################################################
	#7. TLS_VERSION test case
	###############################################################################################################################################################################
	xpico_factorydefaults(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".........................TEST CASE : TLS VERSION.................................")
	test_cases_proc('python '+script_path+'tls_version.py '+device_ip+'', "TLS_VERSION") 

	"""
	###############################################################################################################################################################################
	#8. Mach10 test cases
	###############################################################################################################################################################################
	#Initial factory defaults the device
	telnet(device_ip)
	print_f(".........................TEST CASE : MACH10 FIRMWARE UPDATE.................................")
	test_cases_proc('python '+script_path+'mach10.py '+device_ip+' FW', "MACH10 FIRMWARE UPDATE") 
	print_f(".........................TEST CASE : MACH10 CONFIG UPDATE.................................")
	test_cases_proc('python '+script_path+'mach10.py '+device_ip+' config', "MACH10 CONFIG UPDATE") 
	"""
	
	###############################################################################################################################################################################
	#9. Modem Emulation test cases
	###############################################################################################################################################################################
	xpico_factorydefaults(device_ip)
	telnet(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".........................TEST CASE : Modem Emulation............................")
	test_cases_proc ('python '+script_path+'modememul.py '+serial_port+' 9600 8 N 1 '+device_ip+' 6001 ../5ktext.dat', "Modem_Emulation")
	###############################################################################################################################################################################
	#10. Virtual line test cases
	###############################################################################################################################################################################
	xpico_factorydefaults(device_ip)
	telnet(device_ip)
	xport_CPM(device_ip)
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".........................TEST CASE : Virtual lines............................")
	test_cases_proc ('python '+script_path+'virtual_line.py '+device_ip+' '+serial_port+'', "Virtual_Line")

	###############################################################################################################################################################################
	#11. CLOCK test case
	###############################################################################################################################################################################
	print_f("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print_f(".........................TEST CASE : CLOCK.................................")
	telnet(device_ip)
	test_cases_proc('python '+script_path+'clock.py '+device_ip+'', "CLOCK") 



#Final Report in CSV Format
print "Auto Regression Completed."
print "Generate Test Report"
with open(FW_Version+'_Test_Report_xportedge.csv', 'w') as csvfile:
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
		 
                fieldnames2 = ['Hardware', "Hardware"]
        	writer2 = csv.DictWriter(csvfile, fieldnames=fieldnames2)
        	#writer1.writeheader()
        	writer2.writerow(
           		{'Hardware':  'Hardware',
            	 'Hardware': hardware}
        	)



        	fieldnames3 = ['TEST_CASE', 'RESULT']
        	writer3 = csv.DictWriter(csvfile, fieldnames=fieldnames3)
        	writer3.writeheader()
        	for TEST_CASE in files_dict:
                	writer3.writerow(
                    	{'TEST_CASE':        TEST_CASE,
                     	 'RESULT':           files_dict[TEST_CASE]}
                	)



