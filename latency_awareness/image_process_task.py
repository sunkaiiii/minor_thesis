import cv2
import subprocess


def detect_face(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
    if (len(faces) == 0):
        return None, None
    (x, y, w, h) = faces[0]
    return gray[y:y + w, x:x + h], faces[0]


subprocess.Popen(['python3', "offloading_task.py"]).wait()
img = cv2.imread('offloading_result.jpg')
print(detect_face(img))
