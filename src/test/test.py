import paho.mqtt.client as mqtt
import cv2
import numpy as np
import time
import os
import glob

# MQTT broker details
mqtt_broker = "server-mqtt.thddns.net"
mqtt_port = 3333
mqtt_username = "mqtt"
mqtt_password = "admin1234"
mqtt_topic = "sensor/value"

# Flag to keep track of file operation
file_operation_active = False


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    client.subscribe(mqtt_topic)


def on_message(client, userdata, msg):
    global file_operation_active

    if msg.topic == mqtt_topic:
        sensor_value = int(msg.payload)
        print("Sensor Value:", sensor_value)

        if sensor_value == 1 and not file_operation_active:
            # Publish value 1 to control topic
            client.publish("Control/FaceRecognition", "1")
            file_operation_active = True
            snapshot()  # Call snapshot function
            crop_images()  # Call crop_images function
        elif sensor_value == 0 and file_operation_active:
            # Publish value 0 to control topic
            client.publish("Control/FaceRecognition", "0")
            file_operation_active = False


def connect_to_mqtt_broker():
    client = mqtt.Client()
    client.username_pw_set(mqtt_username, mqtt_password)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(mqtt_broker, mqtt_port, 60)

    client.loop_forever()


def snapshot():
    cap = cv2.VideoCapture("http://192.168.1.115:81/stream")
    if not cap.isOpened():
        print("Unable to connect to ESP32-CAM")
        exit()

    folder = "../../static/snap_picture"
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


def crop_images():
    face_cascade = cv2.CascadeClassifier('../../libs/haarcascade_frontalface_default.xml')
    path = "../../static/default_picture/*.*"
    img_list = glob.glob(path)
    output_folder = "../../static/crop_picture"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    def check_name(file):
        if len(file) >= 34:
            namefile = file[-5:-4]
        else:
            namefile = "default"
        return namefile

    for file in img_list:
        namefile = check_name(file)
        # Read image
        img = cv2.imread(file, 1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.4, 5)
        # Find face with maximum width
        max_w = 0
        best_frame = None
        for (x, y, w, h) in faces:
            if w > max_w:
                max_w = w
                best_frame = (x, y, w, h)
        print(namefile)
        # Check if any faces were detected
        if best_frame is not None:
            # Crop and save image
            x, y, w, h = best_frame
            roi_color = img[y:y+h, x:x+w]
            resized = cv2.resize(roi_color, (300, 300))
            cv2.imwrite(os.path.join(output_folder, namefile + ".jpg"), resized)
        else:
            print("ไม่สามารถ Detect ได้  : " + namefile + ' Path : ' + file)


if __name__ == "__main__":
    connect_to_mqtt_broker()
