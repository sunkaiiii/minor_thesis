import requests
import sys
def send_back(back_url:str,file_name:str):
    files = {'offloading_file':open(file_name,'rb')}
    r = requests.post(back_url,files = files)
    print(r.text)

if __name__ == '__main__':
    send_back(sys.argv[1],sys.argv[2])