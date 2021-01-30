from enum import Enum
from threading import Thread
import random
import time
import subprocess
import requests
import datetime

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
    def __init__(self, task_type,action = None):
        super().__init__()
        self.action = action
        self.deadline = None
        if task_type == 1:
            self.task_type = TaskType.LocalComputing
        elif task_type == 2:
            self.task_type = TaskType.LocalOffloading
        elif task_type == 3:
            self.task_type = TaskType.EdgeComputing
        elif task_type == 4:
            self.offloading_scirpt = 'offloading_task.py'
            self.offloading_url = generating_offloading_url()
            self.task_type = TaskType.EdgeOffloading
        else:
            raise TypeError
    def run(self):
        # print(str(self.task_type))
        # TODO sending the script file
        self.action()


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
            time.sleep(0.2)


    def generate_task(self)->ComputingTask:
        r = random.randint(1,4)
        if r == 1:
            task = ComputingTask(r,self.local_computing_action)
        elif r == 2:
            task = ComputingTask(r,self.local_offloading_action)
        elif r == 3:
            task = ComputingTask(r)
        elif r == 4:
            task = ComputingTask(r)
        #TODO the action would be vary depending on the type of the task
        task = ComputingTask(r,self.default_action)
        return task

    
    def local_computing_action(self):
        task = subprocess.Popen('python3 computing_task.py')
        task.wait()

    def local_offloading_action(self):
        task = subprocess.Popen('python3 offloading_task.py')
        task.wait()


    def default_action(self):
        time.sleep(random.randint(1,10))
        pass
