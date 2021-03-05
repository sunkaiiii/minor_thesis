from datetime import datetime
import os
import pickle
import math
persistance_name = 'driving_sorted_data.dat'
filterd_file_name = 'filted_driving_data.dat'
# filterd_data_index = [169, 79, 113, 212, 109,
#                       301, 214, 306, 291, 152, 191, 207, 286]
# filterd_data_index.sort()

class CarDrivingData:
    def __init__(self, id: int, control_label: str, business_status: str, passenger_status: str, light_status: str, road_status: str, break_status: str, reserved_words: str, receive_date: datetime, gps_time: datetime, longitude: float, latitude: float, speed: float, direction: float, star_numbers: int):
        self.id = id
        self.control_label = control_label
        self.business_status = business_status
        self.passenger_status = passenger_status
        self.light_status = light_status
        self.road_status = road_status
        self.break_status = break_status
        self.reserved_words = reserved_words
        self.receive_date = receive_date
        self.gps_time = gps_time
        self.longitude = longitude
        self.latitude = latitude
        self.speed = speed
        self.direction = direction
        self.star_numbers = star_numbers

    def __str__(self):
        return ' id: ' + str(self.id) + ' receive_date: ' + str(self.receive_date) + ' longitude: ' + str(self.longitude) + ' latitude: ' + str(self.latitude) + ' speed: ' + str(self.speed) + ' direction: ' + str(self.direction)


def aggregate_data() -> [[CarDrivingData]]:
    dirname = '17'
    result = []
    for filename in walk_through_dictionary(dirname):
        file_path = os.path.join(dirname, filename)
        result.extend(__read_car_driving_data(file_path))
    result_map = divide_driving_data_in_map(result)
    return sorted(result_map.values(), key=lambda x: len(x), reverse=True)


def walk_through_dictionary(dir_name: str) -> [str]:
    return list(os.listdir(dir_name))


def __calculate_distance(data1: CarDrivingData, data2: CarDrivingData) -> float:
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
    print("Distance: ", distance*1000)
    return distance*1000


def __read_car_driving_data(file_name: str) -> [CarDrivingData]:
    f = open(file_name, 'r')
    result = []
    while True:
        s = f.readline()
        if len(s) <= 0:
            break
        infos = s.split('|')
        id = int(infos[0])
        control_label = infos[1]
        business_status = infos[2]
        passenger_status = infos[3]
        light_status = infos[4]
        road_status = infos[5]
        break_status = infos[6]
        reserved_words = infos[7]
        try:
            receive_date = datetime.strptime(infos[8], '%Y-%m-%d %H:%M:%S')
        except:
            try:
                receive_date = datetime.strptime(infos[8], '%Y-%m-%d')
            except:
                pass

        try:
            gps_time = datetime.strptime(infos[9], '%Y-%m-%d %H:%M:%S')
        except:
            try:
                gps_time = datetime.strptime(infos[9], '%Y-%m-%d')
            except:
                pass
        longitude = float(infos[10])
        latitude = float(infos[11])
        speed = float(infos[12])
        direction = float(infos[13])
        star_numbers = int(infos[14])
        car_info = CarDrivingData(id, control_label, business_status, passenger_status, light_status, road_status,
                                  break_status, reserved_words, receive_date, gps_time, longitude, latitude, speed, direction, star_numbers)
        result.append(car_info)
    return result


def divide_driving_data_in_map(driving_data: [CarDrivingData]) -> {int: [CarDrivingData]}:
    result = {}
    for data in driving_data:
        if result.get(data.id) is None:
            result[data.id] = []
        result[data.id].append(data)
    return result


def __persistance_sorted_driving_data():
    data = aggregate_data()
    with open(persistance_name, 'wb') as persistance:
        pickle.dump(data, persistance, pickle.HIGHEST_PROTOCOL)


def read_car_driving_data() -> [[CarDrivingData]]:
    if not os.path.exists(persistance_name):
        __persistance_sorted_driving_data()

    with open(persistance_name, 'rb') as persistance:
        return pickle.load(persistance)


def __save_filterd_selected_data():
    all_data = read_car_driving_data()[:100]
    # result = []
    # for index in filterd_data_index:
    #     result.append(all_data[index])
    with open(filterd_file_name, 'wb') as persistance:
        pickle.dump(all_data, persistance, pickle.HIGHEST_PROTOCOL)


def read_filterd_selected_data() -> [[CarDrivingData]]:
    if not os.path.exists(filterd_file_name):
        __save_filterd_selected_data()
    with open(filterd_file_name, 'rb') as persistance:
        return pickle.load(persistance)

if __name__ == '__main__':
    __save_filterd_selected_data()
# print(len(read_filterd_selected_data()))

# data = read_car_driving_data()

# file_name = "gps_tract.txt"
# with open(file_name,'w') as gps_file:
#     for d in data:
#         if len(d)<350:
#             continue
#         print(len(d))
#         gps_file.write('type,time,latitude,longitude,speed\n')
#         for d2 in d:
#             gps_file.write('T,{0},{1},{2},{3}\n'.format(d2.gps_time,d2.latitude,d2.longitude,d2.speed))
