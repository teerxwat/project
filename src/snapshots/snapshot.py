import cv2
import numpy as np
import time
import os

cap = cv2.VideoCapture("http://192.168.1.115:81/stream")
if not cap.isOpened():
    print("Unable to connect to ESP32-CAM")
    exit()

folder = "../../static/default_picture"
if not os.path.exists(folder):
    os.makedirs(folder)

for i in range(10):
    ret, frame = cap.read()
    if not ret:
        print("Unable to capture frame from ESP32-CAM")
        exit()
    cv2.imwrite(os.path.join(folder, "image_" + str(i) + ".jpg"), frame)
    print("Image " + str(i) + " saved successfully")
    time.sleep(0.01)  # delay for 1 millisecond
cap.release()
