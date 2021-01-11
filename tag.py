#!/usr/bin/python3.5
# Decawave
# @YvesBernard
#
# This program is a quick example setting up a BLE connection
# between a Raspberry Pi 3B and a DWM1001 module using PANS software

# It requires the following libraries:
#   - Pygatt "sudo pip install git+https://github.com/peplin/pygatt"
#   - Pexpect "sudo pip install pexpect"

# In order to run the script : sudo python main.py
#
# The DW1001 device to be connected to must be set in variable tdev line 58

import os
import sys
import pygatt
import time
import logging
import binascii
from binascii import hexlify
import struct
import subprocess

# Handle data callback used to process location data notified by DWM1001
def handle_data(handle, value):
	"""
	handle -- integer, characteristic read handle the data was received on
	value -- bytearray, the data returned in the notification
	"""
	hex_data = hexlify(value)
	print(str(value))

# Activating logging
if 0:
	logging.basicConfig()
	logging.getLogger('pygatt').setLevel(logging.DEBUG)

# Name of target device :
tdev = 'DW2C8B'
arch = 'DW2A58'

# This program must be run as super user in order to access the BLE peripheral with Pygatt
if not os.geteuid() == 0:
    sys.exit("\nRoot necessary to run this script\n")
 
# Enable RBP3B BLE peripheral :
subprocess.call('sudo hciconfig hci0 up',shell=True)
   
# Initialization of pygatt 
adapter = pygatt.GATTToolBackend()

# Scanning surrounding BLE devices
all_dev = adapter.scan(run_as_root=True)

# Outputting devices
i = 0
print("BLE devices in range:")
for dev in all_dev: 
	print(" #%d %s %s" % (i ,dev['name'] , dev['address']))
	i+=1

print('\n')

# Connecting to the target device
if not any (d['name'] == tdev or arch for d in all_dev):
	print("The target device is not in range with the Raspberry Pi 3B")
	sys.exit("\nPlease connect dwm1001 target device and restart script\n")

for dev in all_dev:
	if dev['name'] == tdev:
		tadd = dev['address']
	elif dev['name'] == arch:
		aadd = dev['address']

# Connect to target device
print("Connecting to device %s\n" %tdev )
adapter.start()
adev = adapter.connect(aadd)
ldm = adev.char_write("3f0afd88-7770-46b0-b5e7-9fc099598964",bytearray([222,128]))
ldm = adev.char_write("80f9d8bc-3bff-45bb-a181-2d6a37991208",bytearray([32]))
adapter.disconnect(adev)
cdev = adapter.connect(tadd)

# Discover GATT model characteristics
# For DWM1001-dev/PANS detailed GATT model please refer to DWM1001-api-guide version 2.2 section 7

#
# For BLE documentation please see :
# https://devzone.nordicsemi.com/tutorials/b/bluetooth-low-energy/posts/ble-characteristics-a-beginners-tutorial
# https://github.com/peplin/pygatt


# print("List of BLE Characteristics:")

# for uuid in cdev.discover_characteristics().keys():
# 	try:
# 		print("UUID %s (handle %d): %s" %(uuid, cdev.get_handle(uuid), binascii.hexlify(cdev.char_read(uuid))))
# 	except:
# 		print("UUID %s (handle %d): %s" %(uuid, cdev.get_handle(uuid), "!deny!"))

# print('\n')

# Read location data mode 
print("Location Mode Characteristic set to : 0\n")
ldm = adev.char_write("3f0afd88-7770-46b0-b5e7-9fc099598964",bytearray([92,16]))
ldm = cdev.char_write("80f9d8bc-3bff-45bb-a181-2d6a37991208",bytearray([32]))
ldm =  cdev.char_write("a02b947e-df97-4516-996a-1882521e0ead",bytearray([1]))
#print("Location data mode : %s \n" % hexlify(ldm))

# Read and subscribe to location characteristic:
# Data Location characteristic is : uuid 003bbdf2-c634-4b3d-ab56-7ec889b89a37 handle 0x0010
cdev.subscribe('003bbdf2-c634-4b3d-ab56-7ec889b89a37',callback = handle_data)
time.sleep(100)
		
adapter.stop()
    
