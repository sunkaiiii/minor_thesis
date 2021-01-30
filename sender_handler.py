from task_generator import ComputingTask
from task_generator import TaskType
from task_handler import TaskHandler
from uwb_handler import UWBInformation
from threading import Thread
import requests
class SenderHandler:
    def __init__(self,task_offloading_error_action = None):
        self.sended_tasks = {}
        self.task_offloading_error_action = task_offloading_error_action

    def deliever_task(self,task:ComputingTask,uwb_information:UWBInformation):
        if task.task_type == TaskType.EdgeOffloading:
            self.__send_offloading_task(task,uwb_information)

    def __send_offloading_task(self,task:ComputingTask,uwb_information:UWBInformation):
        executor = EdgeOffloadingTaskExecutor(task,uwb_information,error_action=self.task_offloading_error_action)
        executor.start()

class EdgeOffloadingTaskExecutor(Thread):
    def __init__(self,task:ComputingTask,uwb_information:UWBInformation,error_action = None):
        super().__init__()
        self.error_action = self.__default_action
        if error_action is not None:
            self.error_action = error_action
        self.task=task
        self.uwb_information = uwb_information

    def run(self):
        request_url = 'http://' + self.uwb_information.address +':5000/deliever_offloading_task'
        data = {'offloadingUrl':request_url}
        files = {'scirpt':open(task.offloading_scirpt,'rb')}
        timeout = 3.5
        if task.deadline is not None:
            pass
        print('sending offloading task to: '+request_url)
        try:
            r = requests.post(request_url,files = files, data=data,timeout=3.5)
            print(r.text)
        except:
            if self.error_action is not None:
                self.error_action(self.task,self.uwb_information)

    def __default_action(self,task:ComputingTask,uwb_information:UWBInformation):
        print("default error action")
        pass

if __name__ == '__main__':
    uwb_information = UWBInformation('',123,123,'','')
    uwb_information.address = '127.0.0.1'
    task = ComputingTask(4)
    handler = SenderHandler()
    handler.deliever_task(task,uwb_information)