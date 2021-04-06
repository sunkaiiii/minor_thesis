import multiprocessing
from queue import Queue
from threading import Thread
from task_generator import ComputingTask
import subprocess


class JobManager(Thread):
    def __init__(self):
        super().__init__()
        self.capacity = multiprocessing.cpu_count() * 2
        self.task_queue = Queue(self.capacity)

    def available_slots(self) -> int:
        return self.capacity - self.task_queue.qsize()

    def add_task(self, task: ComputingTask):
        self.task_queue.put(task)

    def start_executing(self):
        pass

    def run(self):
        while True:
            task = self.task_queue.get()
            file_name = task.script_name
            print('start_executing:'+file_name)
            subprocess.Popen(['python', file_name]).wait()


if __name__ == '__main__':
    from task_generator import ComputingTask

    i = 0
    job_manager = JobManager()
    job_manager.start()
    while i < 1000:
        task = ComputingTask(123, 'task.py')
        job_manager.add_task(task)
    job_manager.join()
