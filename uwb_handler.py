import pygatt
import time
import struct
import json


class UWBInformation:
    def __init__(self, id: str, distance: int, quality: int):
        """
        Currently, the id and address will combine together
        """
        id_address_map = {'DW29A9': ('192.168.31.135', 'raspberry1'), 'DW2A58': ('192.168.31.105', 'raspberry2'), 'DW0CC1': (
            '192.168.31.171', 'raspberry3'), 'DW2C8B': ('192.168.31.114', 'raspberry4')}
        self.id = id
        self.quality = quality
        self.distance = distance
        self.address = ''
        self.device_name = ''
        device_info = id_address_map.get(self.id)
        if device_info is not None:
            self.address = device_info[0]
            self.device_name = device_info[1]

    def __str__(self):
        return "{"+"id:{0}, distance:{1}, quality:{2}, address:{3}, device_name:{4}".format(self.id, self.distance, self.quality,self.address,self.device_name) + "}"


class UWBHandler:
    def __init__(self):
        print("start to init UWBHandler")
        self.device_id = self.__get_self_id()
        self.device_address = None
        self.adapter = pygatt.GATTToolBackend()
        self.cdev = None
        self.__connect_device()

    def detect_nodes(self, callback):
        self.call_back_action = callback
        self.set_detect_status()

    def __get_self_id(self):
        # get the self name of the UWB device
        return 'DW2C8B'

    def __handle_detect_response_data(self, handle: int, value: bytes) -> [UWBInformation]:
        """
        handle -- integer, characteristic read handle the data was received on
        value -- bytearray, the data returned in the notification, 
        the length of the data should be 2+7*(number of devices), 
        with the 1 byte of data type, 
        1 byte of number of nodes, 
        n(number of sensed devices)*(2 bytes of node id, 4 bytes of the value of distance, 1 byte of quality)
        """
        length = len(value) - 2
        # check the correction of the response data
        if length % 7 != 0 or length == 0:
            return
        i = length / 7
        
        # splicing parsed strings
        unpack_str = '=bb'
        while i > 0:
            unpack_str += 'hib'
            i -= 1
        unpacked_data = struct.unpack(unpack_str, value)[2:]
        # print(unpacked_data)
        result = []
        i = int(length / 7) - 1
        # extract each data to the result lise
        while i >= 0:
            id, distance, quality = unpacked_data[i*3:i*3+3]
            hex_id = hex(id)[2:].upper()
            while len(hex_id) < 4:
                hex_id = '0'+hex_id # the char with the start of 0 will be removed from the hex converting action, try to add it back.
            result.append(UWBInformation(
                'DW'+hex_id, distance, quality))
            i -= 1
        for r in result:
            print(r)
        self.call_back_action(result)
        if self.call_back_action is None:
            return
        return result

    def __connect_device(self):
        """
        scan all the available devices and find the device that with the same name of ID, and then connect to the device.
        """
        print("start to connect device")
        self.adapter.reset()
        ble_devices = self.adapter.scan(run_as_root=True)
        for dev in ble_devices:
            print("%s %s" % (dev['name'], dev['address']))
            if dev['name'] == self.device_id:
                self.device_address = dev['address']
        self.adapter.reset()
        self.adapter.start()
        self.cdev = self.adapter.connect(self.device_address)

        #set mtu to 128 rather than default value 20 will fix an issue where the response data from Bluetooth will be truncated.
        self.cdev.exchange_mtu(128)
        print("connect device successfully")

    def __disconnect_device(self):
        if self.cdev is not None:
            self.adapter.disconnect(self.cdev)
        self.adapter.stop()
        self.cdev = None

    def set_detect_status(self):
        """
        write this uuid will set the tag mode to sense distancce
        0. Position only
        1. Distances
        2. Position and Distance
        """
        ldm = self.cdev.char_write(
            "a02b947e-df97-4516-996a-1882521e0ead", bytearray([1]))
        
        # the subscription will listen the response of the location data characteristic
        self.cdev.subscribe('003bbdf2-c634-4b3d-ab56-7ec889b89a37',
                            callback=self.__handle_detect_response_data)

    def stop_detect_nodes(self):
        self.cdev.unsubscribe('003bbdf2-c634-4b3d-ab56-7ec889b89a37')

    def set_to_anchor_mode(self):
        """
        the operation mode will contain 2 bytes, each bit represent a sepcific fuction
        the first byte is 
        7
        tag (0), anchor (1)
        6 - 5
        UWB - off (0), passive (1), active (2)
        4
        firmware 1 (0), firmware 2 (1)
        3
        accelerometer enable (0, 1)
        2
        LED indication enabled (0, 1)
        1
        firmware update enable (0, 1)
        0
        reserved
        the second byte is
        7
        initiator enable, anchor specific (0, 1)
        6
        low power mode enable, tag specific (0, 1)
        5
        location engine enable, tag specific (0, 1)
        4 - 0
        reserved

        in this method, it set the device to anchor with ative UWB and location engine enabled.
        """
        # print(self.cdev.char_read('3f0afd88-7770-46b0-b5e7-9fc099598964'))
        self.cdev.char_write(
            '3f0afd88-7770-46b0-b5e7-9fc099598964', bytearray([0xdd, 0xa0]))

    def set_to_tag_mode(self):
        """
        in this method, it set the device to tag with ative UWB and location engine enabled.
        """
        self.cdev.char_write(
            '3f0afd88-7770-46b0-b5e7-9fc099598964', bytearray([0x5d, 0xa0]))


def __test_callback(data: [UWBInformation]):
    pass


# if __name__ == '__main__':
#     handler = UWBHandler()
#     handler.set_to_anchor_mode()
#     # time.sleep(2000)
