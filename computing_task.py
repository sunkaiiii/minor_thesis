import cv2
import json
import numpy as np

# pip3 install opencv-python 
# sudo apt-get install libcblas-dev
# sudo apt-get install libhdf5-dev
# sudo apt-get install libhdf5-serial-dev
# sudo apt-get install libatlas-base-dev
# sudo apt-get install libjasper-dev 
# sudo apt-get install libqtgui4 
# sudo apt-get install libqt4-test

model = 'yolov3-tiny.weights'
cfg = 'yolov3-tiny.cfg'
class_file = "coco.names"
classes = None
confThreshold = 0.25  # Confidence threshold
with open(class_file, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')

def find_objects(file_path):
    result_map = {"objects": []}
    image = open(file_path,'rb').read()
    nparr = np.fromstring(image, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    blob = cv2.dnn.blobFromImage(img_np, 1 / 255, (416, 416), [0, 0, 0], 1, crop=False)
    cv_detection = cv2.dnn.readNetFromDarknet(cfg, model)
    cv_detection.setInput(blob)
    outs = cv_detection.forward(_get_output_layers(cv_detection))
    values = {}
    for out in outs:
        for detection in out:
            scores = detection[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold:
                values[classes[classId]] = confidence
    for key, value in values.items():
        detected_object = {"label": key, "accuracy": str(value)}
        result_map.get("objects").append(detected_object)
    return json.dumps(result_map)

def _get_output_layers(cv_detection):
    layerNames = cv_detection.getLayerNames()
    return [layerNames[i[0] - 1] for i in cv_detection.getUnconnectedOutLayers()]

if __name__ == '__main__':
    print(find_objects('/home/pi/Documents/minor_thesis/000000007454.jpg'))