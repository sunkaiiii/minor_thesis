from task_generator import ComputingTask
from task_generator import TaskType
from task_handler import TaskHandler
from forward_table import DistanceRecord
from threading import Thread
import requests
class SenderHandler:
    def __init__(self,task_offloading_error_action = None):
        self.task_offloading_error_action = task_offloading_error_action

    def deliever_task(self,task:ComputingTask,uwb_information:DistanceRecord):
        if task.task_type == TaskType.EdgeOffloading:
            self.__send_offloading_task(task,uwb_information)

    def __send_offloading_task(self,task:ComputingTask,uwb_information:DistanceRecord):
        executor = EdgeOffloadingTaskExecutor(task,uwb_information,error_action=self.task_offloading_error_action)
        executor.start()

class EdgeOffloadingTaskExecutor(Thread):
    def __init__(self,task:ComputingTask,distance_record:DistanceRecord,error_action = None):
        super().__init__()
        self.error_action = self.__default_action
        if error_action is not None:
            self.error_action = error_action
        self.task=task
        self.distance_record = distance_record

    def run(self):
        request_url = 'http://' + self.distance_record.uwb_information.address +':5000/deliever_offloading_task'
        data = {'offloadingUrl':self.task.offloading_url}
        files = {'scirpt':open(self.task.offloading_scirpt,'rb')}
        timeout = 3.5
        if self.task.deadline is not None:
            pass
        print('sending offloading task to: '+request_url)
        try:
            r = requests.post(request_url,files = files, data=data,timeout=3.5)
            print(r.text)
        except:
            if self.error_action is not None:
                self.error_action(self.task,self.distance_record)

    def __default_action(self,task:ComputingTask,uwb_information:DistanceRecord):
        print("default error action")
        pass

if __name__ == '__main__':
    uwb_information = UWBInformation('',123,123)
    uwb_information.address = '127.0.0.1'
    task = ComputingTask(4)
    handler = SenderHandler()
    handler.deliever_task(task,uwb_information)