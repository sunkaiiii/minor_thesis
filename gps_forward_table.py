from data_reader import CarDrivingData
import math
from datetime import datetime
from functools import cmp_to_key

class DistanceRecord:
    def __init__(self, distance:float, data:CarDrivingData):
        self.distance = distance
        self.data = data
        
class GPSForwardTable:
    def __init__(self):
        self.max_size = 5000
        self.cloest_nodes = []
        self.nodes = []
    
    
    def calculate_distance(self,data1: CarDrivingData, data2: CarDrivingData) -> float:
        R = 6373.0
        lat1 = math.radians(data1.latitude)
        lon1 = math.radians(data1.longitude)
        lat2 = math.radians(data2.latitude)
        lon2 = math.radians(data2.longitude)
        dlon = lon2-lon1
        dlat = lat2-lat1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * \
            math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R*c
        if distance*1000 <1000:
            print("Distance: ", distance*1000)
        return distance*1000

    def refresh_table(self, self_node:CarDrivingData,nodes:[CarDrivingData]):
        print("Refresh forward table...")
        print("Current time is: " + str(self_node.gps_time))
        self.cloest_nodes = [DistanceRecord(self.calculate_distance(self_node,node),node) for node in nodes]
        self.cloest_nodes.sort(key=lambda x:x.distance)
        print("Refresh forward table successfully")


    def get_the_best_node(self,except_nodes = [])->DistanceRecord:

        if len(self.cloest_nodes) > 0:
            for node in self.cloest_nodes:
                if node.data in except_nodes:
                    continue
                return node
        else:
            return None
            
