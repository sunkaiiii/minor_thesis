import pygatt
import time
import struct
import json

class UWBHandler:
    def __init__(self):
        self.device_id = self.__get_self_id()
        self.device_address = None

    def detect_nodes(self,callback):
        self.call_back_action = callback
        self.set_detect_status()
    
    def __get_self_id(self):
        return 'DW2C8B'

    def __handle_detect_response_data(self,handle,value):
        """
        handle -- integer, characteristic read handle the data was received on
        value -- bytearray, the data returned in the notification, 
        the length of the data should be 2+7*(number of devices), with the 1 byte of data type, 1 byte of number of nodes, 2 bytes of node, 4 bytes of the value of distance, 1 byte of quality
        """
        if self.adapter is not None:
            self.adapter.stop()
        if self.call_back_action is None:
            return
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
        i = int(length / 7) - 1
        while i >= 0:
            id,distance,quality = unpacked_data[i*3:i*3+3]
            result.append(UWBInformation('DW'+hex(id)[2:].upper(),distance,quality))
            i-=1
        print(result)
        self.call_back_action(result)
        return result

    def set_detect_status(self):
        self.adapter = pygatt.GATTToolBackend()
        if self.device_address is None:
            self.adapter.reset()
            ble_devices = self.adapter.scan(run_as_root=True)
            for dev in ble_devices: 
                print("%s %s" % (dev['name'] , dev['address']))
                if dev['name'] == self.device_id:
                    self.device_address = dev['address']
        self.adapter.start()
        cdev = self.adapter.connect(self.device_address)
        ldm =  cdev.char_write("a02b947e-df97-4516-996a-1882521e0ead",bytearray([1]))
        ldm =  cdev.char_read("a02b947e-df97-4516-996a-1882521e0ead")
        cdev.subscribe('003bbdf2-c634-4b3d-ab56-7ec889b89a37',callback = self.__handle_detect_response_data)
        

class UWBInformation:
    def __init__(self, id, distance, quality):
        self.id = id
        self.quality = distance
        self.distance = quality
    def __str__(self):
        return "{"+"id:{0}, distance:{1}, quality:{2}".format(self.id,self.distance,self.quality) + "}"


