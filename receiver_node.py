from flask import request
from flask import Flask
import requests
import task_cacher
from multiprocessing import Process
import os
app = Flask(__name__)
@app.route('/deliever_offloading_task',methods = ['POST'])
def deliever_offloading_task():
    # return_url = request.form['returnUrl']
    offloading_url = request.form['offloadingUrl']
    scirpt_file = request.files['scirpt']
    filename = scirpt_file.filename
    scirpt_file.save(filename)
    exec_script = filename + offloading_url
    print("start offloading:"+exec_script)
    os.system(exec_script)
    cached_file_name = task_cacher.create_id(offloading_url)
    files = {'file',open(os.path.join('cache',cached_file_name),'rb')}
    back_address = request.remote_addr
    requests.post(back_address+'/receive_offloading_result',files = files)
    

@app.route('/receive_offloading_result',methods = ['POST'])
def receive_offloading_result():
    offloading_file = request.files['file']
    if os.path.isdir('offloading'):
        os.mkdir('offloading')
    save_path = os.path.join('offloading',offloading_file.filename)
    offloading_file.save(save_path)

class ReceiverTaskHandler():
    def run(self):
        app.run(host='0.0.0.0',debug=False,port=5000)
    
    def start_service(self):
        self.server = Process(target=self.run)
        self.server.start()
    
    def stop_service(self):
        if self.server is not None:
            self.server.terminate()

if __name__ == '__main__':
    handler = ReceiverTaskHandler()
    handler.run()
        

