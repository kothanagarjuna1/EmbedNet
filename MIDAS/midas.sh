#!/usr/local/bin/python3
import sys
import os
import socket
import shutil
import subprocess
#import numpy
import re

subprocess.call("python tunnel.py /dev/ttyS6 192.168.51.161 192.168.51.25 accept 9600 8 N 1 always tcp",shell= True)
subprocess.call("python tunnel.py /dev/ttyS6 192.168.51.161 192.168.51.25 accept 9600 8 N 1 'any character' tcp",shell= True)
subprocess.call("python tunnel.py /dev/ttyS6 192.168.51.161 192.168.51.25 accept 9600 8 N 1 'start character' tcp",shell= True)
subprocess.call("python tunnel.py /dev/ttyS6 192.168.51.161 192.168.51.25 connect 9600 8 N 1 always tcp",shell= True)
subprocess.call("python tunnel.py /dev/ttyS6 192.168.51.161 192.168.51.25 connect 9600 8 N 1 'any character' tcp",shell= True)
subprocess.call("python tunnel.py /dev/ttyS6 192.168.51.161 192.168.51.25 connect 9600 8 N 1 'start character' tcp",shell= True)


subprocess.call("python tunnel.py /dev/ttyS6 192.168.51.161 192.168.51.25 accept 9600 8 N 1 always 'tcp aes'",shell= True)
subprocess.call("python tunnel.py /dev/ttyS6 192.168.51.161 192.168.51.25 accept 9600 8 N 1 'any character' 'tcp aes'",shell= True)
subprocess.call("python tunnel.py /dev/ttyS6 192.168.51.161 192.168.51.25 accept 9600 8 N 1 'start character' 'tcp aes'",shell= True)
subprocess.call("python tunnel.py /dev/ttyS6 192.168.51.161 192.168.51.25 connect 9600 8 N 1 always 'tcp aes'",shell= True)
subprocess.call("python tunnel.py /dev/ttyS6 192.168.51.161 192.168.51.25 connect 9600 8 N 1 'any character' 'tcp aes'",shell= True)
subprocess.call("python tunnel.py /dev/ttyS6 192.168.51.161 192.168.51.25 connect 9600 8 N 1 'start character' 'tcp aes'",shell= True)

subprocess.call("python tunnel.py /dev/ttyS6 192.168.51.161 192.168.51.25 accept 9600 8 N 1 always tls",shell= True)
subprocess.call("python tunnel.py /dev/ttyS6 192.168.51.161 192.168.51.25 accept 9600 8 N 1 'any character' tls",shell= True)
subprocess.call("python tunnel.py /dev/ttyS6 192.168.51.161 192.168.51.25 accept 9600 8 N 1 'start character' tls",shell= True)
subprocess.call("python tunnel.py /dev/ttyS6 192.168.51.161 192.168.51.25 connect 9600 8 N 1 always tls",shell= True)
subprocess.call("python tunnel.py /dev/ttyS6 192.168.51.161 192.168.51.25 connect 9600 8 N 1 'any character' tls",shell= True)
subprocess.call("python tunnel.py /dev/ttyS6 192.168.51.161 192.168.51.25 connect 9600 8 N 1 'start character' tls",shell= True)





