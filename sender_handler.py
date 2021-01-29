from task_generator import ComputingTask
from task_generator import TaskType
from task_handler import TaskHandler
from uwb_handler import UWBInformation
import requests
class SenderHandler:
    def __init__(self):
        pass

    def deliever_task(self,task:ComputingTask,uwb_information:UWBInformation):
        if task.task_type == TaskType.EdgeOffloading:
            self.__send_offloading_task(task,uwb_information)

    def __send_offloading_task(self,task:ComputingTask,uwb_information:UWBInformation):
        url = task.offloading_url
        files = {'scirpt':open(task.offloading_scirpt,'rb')}
        request_url = 'http://' + uwb_information.address +':5000/deliever_offloading_task'
        data = {'offloadingUrl':url}
        print('sending offloading task to: '+request_url)
        r = requests.post(request_url,files=files,data=data)
        print(r.text)

if __name__ == '__main__':
    uwb_information = UWBInformation('',123,123,'','')
    uwb_information.address = '127.0.0.1'
    task = ComputingTask(4)
    handler = SenderHandler()
    handler.deliever_task(task,uwb_information)