import subprocess
from threading import Thread
from flask import request
from flask import Flask
from task_handler import TaskHandler
import requests
import task_cacher
import os
app = Flask(__name__)
allow_request = False
task_handler = None

@app.route('/deliever_offloading_task',methods = ['POST'])
def deliever_offloading_task():
    if not allow_request or task_handler is None:
        # TODO send http code
        return 'asd'
    # return_url = request.form['returnUrl']
    offloading_url = request.form['offloadingUrl']
    scirpt_file = request.files['scirpt']
    filename = scirpt_file.filename
    scirpt_file.save(filename)
    exec_script = 'python3 '+filename + ' ' + offloading_url
    print("start offloading:"+exec_script)
    os.system(exec_script)
    cached_file_name = os.path.join('cache',task_cacher.create_id(offloading_url))
    print(cached_file_name)
    files = {'offloading_file':open(cached_file_name,'rb')}
    back_address = 'http://' + request.remote_addr + ':5000/receive_offloading_result'
    print("send offloading result to: " + back_address)
    r = requests.post(back_address,files = files)
    print(r.text)
    return 'ok'

@app.route('/receive_offloading_result',methods = ['POST'])
def receive_offloading_result():
    if not allow_request or task_handler is None:
        # TODO send http code
        return 'asd'
    offloading_file = request.files['offloading_file']
    if not os.path.isdir('offloading'):
        os.mkdir('offloading')
    save_path = os.path.join('offloading',offloading_file.filename)
    offloading_file.save(save_path)
    return 'ok'


class ReceiverTaskHandler():
    def __init__(self,handler:TaskHandler):
        app.run(host='0.0.0.0',debug=True,port=5000)
        task_handler = handler

    def start_service(self):
        allow_request = True

    def stop_service(self):
        allow_request = False

if __name__ == '__main__':
    handler = ReceiverTaskHandler(None)
    handler.start_service()
    import time
    time.sleep(10)
    handler.stop_service()

        

