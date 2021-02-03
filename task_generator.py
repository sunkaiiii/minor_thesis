from enum import Enum
from threading import Thread
import random
import time
import subprocess
import requests
from datetime import datetime,timedelta

class TaskType(Enum):
    LocalComputing = 1
    LocalOffloading = 2
    EdgeComputing = 3
    EdgeOffloading = 4


def generating_offloading_url()->str:
    urls = ['https://photo-collection-monash.s3.amazonaws.com/20161128_032955000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161128_033042000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161205_004901000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161205_004921000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161205_005003000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161205_005023000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161205_005057000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161205_005118000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161205_005128000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161205_005132000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161205_005154000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161205_005204000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161205_005211000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161205_005232000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161226_010508000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161226_010539000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161226_010553000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161226_010621000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161226_010650000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161226_010753000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161226_010831000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161226_010857000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161226_010910000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161226_010932000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161226_011257000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161226_011310000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161226_011323000_iOS.jpg'
    ,'https://photo-collection-monash.s3.amazonaws.com/20161226_011329000_iOS.jpg']
    index = random.randint(0,len(urls)-1)
    return urls[index]

class ComputingTask(Thread):
    """
    The computing task contains an executable scirpt.
    """
    def __init__(self, task_type,action,deadline = None,except_nodes_id = [],offloading_scirpt = None, offloading_url = None):
        super().__init__()
        self.action = action
        self.deadline = deadline
        self.except_nodes_id = except_nodes_id
        self.offloading_url = offloading_url
        self.offloading_scirpt = offloading_scirpt
        if task_type == 1:
            self.task_type = TaskType.LocalComputing
        elif task_type == 2:
            self.task_type = TaskType.LocalOffloading
        elif task_type == 3:
            self.task_type = TaskType.EdgeComputing
        elif task_type == 4:
            self.task_type = TaskType.EdgeOffloading
        else:
            raise TypeError
    def run(self):
        self.action()

    def convert_edge_offloading_to_local_offloading(self):
        if self.task_type != TaskType.EdgeOffloading:
            raise Exception("The task type is not Edge Offloading")
        return ComputingTask(2,self.__local_offloading_action,self.deadline,self.except_nodes_id,offloading_scirpt=self.offloading_scirpt,offloading_url=self.offloading_url)
    
    def convert_edge_computing_to_local_computing(self):
        if self.task_type != TaskType.EdgeComputing:
            raise Exception("The task type if not Edge Computing")
        return ComputingTask(1,self.__local_computing_action)

    def __local_offloading_action(self):
        print('converted task,offloading url:'+self.offloading_url+" offloading scirpt:"+self.offloading_scirpt)
        task = subprocess.Popen(['python3',self.offloading_scirpt,self.offloading_url])
        task.wait()

    def __local_computing_action(self):
        task = subprocess.Popen(['python3','computing_task.py'])
        task.wait() 

def create_local_task(action):
    return ComputingTask(TaskType.LocalOffloading,action)

class TaskGenerator(Thread):
    """
    Randomly generate a task with a specific type.
    The types of a task will be four types
    """
    def __init__(self,callback):
        super().__init__()
        self.callback = callback
    
    def run(self):
        while True:
            task = self.generate_task()
            self.callback(task)
            # time.sleep(random.randint(1,10))

            # the interval for generating a task may vary depending on different testing method.
            time.sleep(random.randint(1,1))


    def generate_task(self)->ComputingTask:
        r = random.randint(1,4)
        deadline = datetime.now()+timedelta(seconds=random.randint(10,100))
        if r == 1:
            task = ComputingTask(r,self.local_computing_action,deadline=deadline)
        elif r == 2:
            task = ComputingTask(r,self.local_offloading_action,deadline=deadline)
        elif r == 3:
            task = ComputingTask(r,self.default_action,deadline=deadline)
        elif r == 4:
            task = ComputingTask(r,self.default_action,deadline=deadline,offloading_scirpt='offloading_task.py',offloading_url=generating_offloading_url())
        return task

    
    def local_computing_action(self):
        task = subprocess.Popen(['python3','computing_task.py'])
        task.wait()

    def local_offloading_action(self):
        task = subprocess.Popen(['python3','offloading_task.py',generating_offloading_url()])
        task.wait()


    def default_action(self):
        pass

if __name__ == '__main__':
    task = ComputingTask(4,None)
    task = task.convert_edge_offloading_to_local_offloading()
    task.start()
    task.join()
