from flask import request
from flask import Flask
import requests
import task_cacher
import subprocess
import os
app = Flask(__name__)
@app.route('/deliever_offloading_task',methods = ['POST'])
def deliever_offloading_task():
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
    offloading_file = request.files['offloading_file']
    if not os.path.isdir('offloading'):
        os.mkdir('offloading')
    save_path = os.path.join('offloading',offloading_file.filename)
    offloading_file.save(save_path)
    return 'ok'

class ReceiverTaskHandler():
    def __init__(self):
        self.server = None
    def start_service(self):
        self.server = subprocess.Popen('python3 receiver_node.py')
    
    def stop_service(self):
        if self.server is not None:
            self.server.terminate()

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=5000)
        

