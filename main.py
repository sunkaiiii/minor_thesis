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

class UWBInformation:
    def __init__(self, id, distance, quality):
        self.id = id
        self.quality = distance
        self.distance = quality

# Handle data callback used to process location data notified by DWM1001
def handle_data(handle,value):
    """
	handle -- integer, characteristic read handle the data was received on
	value -- bytearray, the data returned in the notification, 
	the length of the data should be 2+7*(number of devices), with the 1 byte of data type, 1 byte of number of nodes, 2 bytes of node, 4 bytes of the value of distance, 1 byte of quality
	"""
    length = len(value) - 2
    if length % 7 != 0 or length == 0:
        return
    i = length / 7
    unpack_str = '=bb'
    while i>0:
        unpack_str += 'hib'
        i -= 1
    unpacked_data = struct.unpack(unpack_str,value)[2:]
    print(unpacked_data)
    result = []
    i = int(length / 7)
    while(i>0):
        id,distance,quality = unpacked_data[(i-1)*3:(i-1)*3+3]
        result.append(UWBInformation(id,distance,quality))
        i-=1
    return result


# Activating logging
if 0:
	logging.basicConfig()
	logging.getLogger('pygatt').setLevel(logging.DEBUG)

# Name of target device :
tdev = 'DW2C8B'

# This program must be run as super user in order to access the BLE peripheral with Pygatt
# if not os.geteuid() == 0:
#     sys.exit("\nRoot necessary to run this script\n")
 
# Enable RBP3B BLE peripheral :
# subprocess.call('sudo hciconfig hci0 up',shell=True)
   
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
if not any (d['name'] == tdev for d in all_dev):
	print("The target device is not in range with the Raspberry Pi 3B")
	sys.exit("\nPlease connect dwm1001 target device and restart script\n")

for dev in all_dev:
	if dev['name'] == tdev:
		tadd = dev['address']

# Connect to target device
print("Connecting to device %s\n" %tdev )
adapter.start()
cdev = adapter.connect(tadd)
time.sleep(1)

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
ldm =  cdev.char_write("a02b947e-df97-4516-996a-1882521e0ead",bytearray([1]))
ldm =  cdev.char_read("a02b947e-df97-4516-996a-1882521e0ead")
print(ldm)
#print("Location data mode : %s \n" % hexlify(ldm))

# Read and subscribe to location characteristic:
# Data Location characteristic is : uuid 003bbdf2-c634-4b3d-ab56-7ec889b89a37 handle 0x0010
cdev.subscribe('003bbdf2-c634-4b3d-ab56-7ec889b89a37',callback = handle_data)
time.sleep(100)
		
adapter.stop()
    
