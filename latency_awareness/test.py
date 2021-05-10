import base64
with open("offloading_result.jpg",'rb') as f:
    file_data = f.read()
    data =  str(base64.b64encode(file_data))
    print(str(data))