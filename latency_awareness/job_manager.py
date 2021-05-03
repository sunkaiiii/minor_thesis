import multiprocessing
import os
from queue import Queue
from threading import Thread
from task_generator import ComputingTask
import subprocess


class JobManager(Thread):
    def __init__(self, log_callback = None):
        super().__init__()
        self.capacity = multiprocessing.cpu_count() * 3
        self.task_queue = Queue(self.capacity)
        self.log_callback = log_callback
        self.remote_task_execution_finished_callback = None
        self.finished = False

    def available_slots(self) -> int:
        return self.capacity - self.task_queue.qsize()

    def add_task(self, task: ComputingTask):
        self.task_queue.put(task)

    def start_executing(self):
        pass

    def run(self):
        while not self.finished or self.available_slots()!=self.capacity:
            try:
                task = self.task_queue.get(timeout=1)
                file_name = task.script_name
                print('start_executing:'+file_name)
                subprocess.Popen(['python3', file_name]).wait()
                if self.log_callback is not None and not task.remote_task:
                    self.log_callback(task)
                if self.remote_task_execution_finished_callback is not None and task.remote_task:
                    print('call remote task execution finished callback')
                    os.remove(file_name)
                    self.remote_task_execution_finished_callback(task)
            except:
                continue
        print('job finished')

def dummy(task):
    pass

if __name__ == '__main__':
    from task_generator import ComputingTask

    i = 0
    job_manager = JobManager()
    job_manager.remote_task_execution_finished_callback = dummy
    job_manager.start()
    while i < 1000:
        task = ComputingTask(123, 'task.py',remote_task=True)
        job_manager.add_task(task)
    job_manager.join()
