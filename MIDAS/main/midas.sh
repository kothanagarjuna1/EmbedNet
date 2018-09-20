#!/usr/local/bin/python3
import sys
import os
import socket
import shutil
import subprocess
import numpy
import re

subprocess.call("python midas.py xpico200",shell= True)
subprocess.call("python midas.py xportedge",shell= True)
