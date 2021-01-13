from flask import request
from flask import Flask
from multiprocessing import Process
app = Flask(__name__)
@app.route('/deliever_task',methods = ['POST'])
def deliever_task():
    return "123"
class ReceiverTaskHandler():
    def run(self):
        app.run(host='0.0.0.0',debug=False,port=5000)
    
    def start_service(self):
        self.server = Process(target=self.run)
        self.server.start()
    
    def stop_service(self):
        if self.server is not None:
            self.server.terminate()

        

