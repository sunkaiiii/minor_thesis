from data_reader import CarDrivingData
from datetime import datetime
from datetime import timedelta
import threading
class GPSInformationHandler:
    def __init__(self,data:[CarDrivingData]):
        self.driving_data = data
        self.time = datetime.strptime('2018-04-01 17:00:00','%Y-%m-%d %H:%M:%S')
        self.current_gps_data = self.driving_data[0]
        self.current_index = 0
        self.__find_data_by_time()

    def __find_data_by_time(self)->CarDrivingData:
        while self.current_index < len(self.driving_data):
            data = self.driving_data[self.current_index]
            if self.time > data.receive_date:
                self.current_index+=1
            else:
                self.current_gps_data = data
                break
        self.time = self.time+timedelta(seconds=1)
        timer = threading.Timer(0.05,self.__find_data_by_time)
        timer.start()
        # print('Current data is:'+ str(self.current_gps_data))


if __name__ == '__main__':
    import data_reader
    datas = data_reader.read_filterd_selected_data()
    handler = GPSInformationHandler(datas[0])
    import time
    time.sleep(10)
    print(handler.current_gps_data)