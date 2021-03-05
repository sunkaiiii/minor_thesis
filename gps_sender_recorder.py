from task_generator_gps import ComputingTask
from data_reader import CarDrivingData
from datetime import datetime
from task_generator_gps import TaskType
from threading import Thread


class GPSSenderRecorder:
    def __init__(self):
        self.save_file_name = str(datetime.now().strftime('%Y_%m_%d%H_%M_%S'))+".txt"

    def deliever_task(self, task: ComputingTask, self_data: CarDrivingData, car_driving_data: CarDrivingData):
        self.__send_offloading_task(task, self_data, car_driving_data)

    def __send_offloading_task(self, task: ComputingTask, self_data: CarDrivingData, car_driving_data: CarDrivingData):
        executor = GPSSenderWorker(
            self.save_file_name, task, self_data, car_driving_data)
        executor.start()


class GPSSenderWorker(Thread):
    def __init__(self, save_file_name, task: ComputingTask, self_data: CarDrivingData, car_driving_data: CarDrivingData):
        super().__init__()
        self.save_file_name = save_file_name
        self.task = task
        self.self_data = self_data
        self.data = car_driving_data

    def run(self):
        with open(self.save_file_name, 'a') as file:
            file.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n'.format(self.task.id, self.self_data.id, self.data.id, 'S', datetime.now(
            ), self.task.deadline, self.self_data.longitude, self.self_data.latitude, self.data.longitude, self.data.latitude))
            self.task.start()
            self.task.join()
            file.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n'.format(self.task.id, self.self_data.id, self.data.id, 'E', datetime.now(
            ), self.task.deadline, self.self_data.longitude, self.self_data.latitude, self.data.longitude, self.data.latitude))

if __name__ == '__main__':
    with open(str(datetime.now().strftime('%Y_%m_%d%H_%M_%S'))+".txt",'a') as file:
        file.write('13124')