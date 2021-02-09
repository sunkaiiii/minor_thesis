from threading import Thread
from flask import request
from flask import Flask
from flask import abort
from task_handler import TaskHandler
import task_generator
import requests
import task_cacher
import os
app = Flask(__name__)
allow_request = False
task_handler:TaskHandler = None

@app.route('/deliever_offloading_task',methods = ['POST'])
def deliever_offloading_task():
    if not allow_request or task_handler is None:
        abort(400)
    # return_url = request.form['returnUrl']
    offloading_url = request.form['offloadingUrl']
    scirpt_file = request.files['scirpt']
    
    print(offloading_url)
    # check the file and offloading url are correctly sent.
    if offloading_url is None or scirpt_file is None:
        abort(400)
    filename = scirpt_file.filename
    scirpt_file.save(filename)

    # generate task for this request
    handler = __OffloadingTaskHandler(filename,offloading_url,request.remote_addr)
    task = task_generator.create_local_task(handler.offloading_task_aciton)
    task_handler.add_new_task(task)
    return 'ok'

class __OffloadingTaskHandler:
    def __init__(self,filename:str,offloading_url:str,back_address:str):
        self.filename = filename
        self.offloading_url = offloading_url
        self.back_address = back_address

    def offloading_task_aciton(self):
        exec_script = 'python3 '+self.filename + ' ' + self.offloading_url
        print("start offloading:"+exec_script)
        os.system(exec_script)
        cached_file_name = os.path.join('cache',task_cacher.create_id(self.offloading_url))
        print(cached_file_name)
        files = {'offloading_file':open(cached_file_name,'rb')}
        back_address = 'http://' + self.back_address + ':5000/receive_offloading_result'
        print("send offloading result to: " + back_address)
        r = requests.post(back_address,files = files)
        print(r.text)

@app.route('/receive_offloading_result',methods = ['POST'])
def receive_offloading_result():
    if task_handler is None:
        abort(400)
    offloading_file = request.files['offloading_file']
    if not os.path.isdir('offloading'):
        os.mkdir('offloading')
    save_path = os.path.join('offloading',offloading_file.filename)
    offloading_file.save(save_path)
    return 'ok'


class ReceiverTaskHandler(Thread):
    def __init__(self,handler:TaskHandler):
        super().__init__()
        global task_handler
        task_handler = handler
    def run(self):
        app.run(host='0.0.0.0',debug=False,port=5000)

    def start_service(self):
        allow_request = True

    def stop_service(self):
        allow_request = False

if __name__ == '__main__':
    executor = TaskHandler(None)
    handler = ReceiverTaskHandler(executor)
    handler.start_service()
    allow_request = True
    handler.setDaemon(0)
    handler.start()
    executor.start()
    handler.join()

        

