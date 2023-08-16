import paho.mqtt.client as mqtt
import cv2
import numpy as np
import time
import os
import glob
import dlib
import pickle
import mysql.connector
import datetime

# MQTT broker details -Home
# mqtt_broker = "server-mqtt.thddns.net"
# mqtt_port = 3333
# mqtt_username = "mqtt"
# mqtt_password = "admin1234"
# mqtt_topic = "sensor/detect"
# topic_Temperature = "sensor/Temperature"

# MQTT broker details -AS Point
mqtt_broker = "192.168.0.28"
mqtt_port = 1883
mqtt_username = ""
mqtt_password = ""
mqtt_topic = "sensor/detect"
topic_Temperature = "sensor/Temperature"

# Flag to keep track of file operation
file_operation_active = False

# MySQL database connection
cnx = mysql.connector.connect(
    host="localhost", port=3306, user="root", password="", database="db_facerecognition")
mycursor = cnx.cursor()

# Initialize face recognition models and data
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor('../../libs/shape_predictor_68_face_landmarks.dat')
model = dlib.face_recognition_model_v1(
    '../../libs/dlib_face_recognition_resnet_model_v1.dat')
FACE_DESC, FACE_NAME = pickle.load(open('../../static/model/model.pk', 'rb'))

# Initialize face detection cascade classifier
face_cascade = cv2.CascadeClassifier(
    '../../libs/haarcascade_frontalface_default.xml')

# MQTT client setup
client = mqtt.Client()
client.username_pw_set(mqtt_username, mqtt_password)


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    client.subscribe(mqtt_topic)
    client.subscribe(topic_Temperature)


def on_message(client, userdata, msg):
    global file_operation_active

    if msg.topic == mqtt_topic:
        sensor_value = int(msg.payload)
        print("Sensor Value:", sensor_value)

        if sensor_value == 1 and not file_operation_active:
            client.publish("Control/FaceRecognition", "1")
            file_operation_active = True
            RecognitionForVideo()
        elif sensor_value == 0 and file_operation_active:
            client.publish("Control/FaceRecognition", "0")
            file_operation_active = False

    elif msg.topic == topic_Temperature:
        temperature_value = float(msg.payload)
        print("Temperature Value:", temperature_value)
        # Perform actions based on temperature value
        # ...
        global temperature
        temperature = temperature_value


def connect_to_mqtt_broker():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_broker, mqtt_port, 60)
    client.loop_forever()


def RecognitionForVideo():
    # Create a client instance
    client = mqtt.Client()

    # Set the username and password
    # client.username_pw_set("mqtt", "admin1234")

    # Set the username and password
    client.username_pw_set("", "")

    # Connect to the broker
    # client.connect("server-mqtt.thddns.net", 3333)

    # Connect to the broker
    client.connect("192.168.0.28", 1883)

    client_led = mqtt.Client()
    client_led.username_pw_set(mqtt_username, mqtt_password)
    client_led.connect(mqtt_broker, mqtt_port)

    cnx = mysql.connector.connect(
        host="localhost", port=3306, user="root", password="", database="db_facerecognition")
    mycursor = cnx.cursor()
    face_detector = cv2.CascadeClassifier(
        '../../libs/haarcascade_frontalface_default.xml')

    detector = dlib.get_frontal_face_detector()
    sp = dlib.shape_predictor(
        '../../libs/shape_predictor_68_face_landmarks.dat')
    model = dlib.face_recognition_model_v1(
        '../../libs/dlib_face_recognition_resnet_model_v1.dat')
    FACE_DESC, FACE_NAME = pickle.load(
        open('../../static/model/model.pk', 'rb'))

    cap = cv2.VideoCapture('http://192.168.0.51:81/stream')

    # cam pc
    # cap = cv2.VideoCapture('0')

    last_insert_time = time.time()
    insert_interval = 60  # Time interval for data insertion (in seconds)

    start_time = time.time()  # Store the starting time

    last_insert_time = time.time()
    insert_interval = 60  # Time interval for data insertion (in seconds)

    def Select(idPerson):
        querySelectDetect = "SELECT first_name FROM tb_users WHERE studentid='" + idPerson + "'"
        mycursor.execute(querySelectDetect)
        myresultSelect = mycursor.fetchall()
        if myresultSelect:
            return myresultSelect[0][0]
        else:
            return '\033[91m' + 'ไม่พบข้อมูลในระบบ'

    def Insert(idPerson, temperature):
        queryInsertDateDetect = "INSERT INTO tb_user_logs(id_user, report_date, timestamp, temperature, year) VALUES (%(id_user)s, %(report_date)s, NOW(), %(temperature)s, %(year)s)"
        val = {'id_user': idPerson, 'report_date': datetime.date.today(),
               'temperature': temperature, 'year': datetime.date.today().year}
        # print("Insert Query:", queryInsertDateDetect)
        # print("Insert Values:", val)
        # if temperature >= 35.4 and temperature <= 37.4:
        if temperature >= 30 and temperature <= 37.4:
            client_led.publish("control/led", "1")
        else:
            client_led.publish("control/led", "2")
        mycursor.execute(queryInsertDateDetect, val)
        cnx.commit()

    def CheckID(idPerson):
        queryGetUserIDs = "SELECT id_user FROM tb_users WHERE studentid = %(idPerson)s"
        val = {'idPerson': idPerson}
        mycursor.execute(queryGetUserIDs, val)
        myresult = mycursor.fetchall()
        return myresult

    current_face = None
    insert_counter = 0  # Counter for successful insertions
    max_insertions = 1  # Maximum number of insertions

    mqtt_value_sent = False

    while True:
        _, frame = cap.read()
        if frame is not None:
            if not mqtt_value_sent:
                client.publish("control/led", "4")
                mqtt_value_sent = True
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, 1.3, 5)

            # Check if 10 seconds have passed since the camera was turned on
            if time.time() - start_time > 5:
                print("Exiting the function due to timeout")
                client_led.publish("control/led", "3")
                cap.release()
                cv2.destroyAllWindows()
                return

            for (x, y, w, h) in faces:
                img = frame[y-10:y+h+10, x-10:x+w+10][:, :, ::-1]
                dets = detector(img, 1)
                for k, d in enumerate(dets):
                    shape = sp(img, d)
                    face_desc0 = model.compute_face_descriptor(img, shape, 1)
                    d = []
                    for face_desc in FACE_DESC:
                        d.append(np.linalg.norm(
                            np.array(face_desc) - np.array(face_desc0)))
                    d = np.array(d)
                    idx = np.argmin(d)
                    if d[idx] < 0.3:
                        idPerson = FACE_NAME[idx]
                        name = Select(idPerson)
                        cv2.putText(frame, name, (x, y-5),
                                    cv2.FONT_ITALIC, 0.7, (0, 0, 255), 2)
                        cv2.rectangle(frame, (x, y), (x+w, y+h),
                                      (0, 0, 255), 2)
                        print(idPerson)
                        result = CheckID(idPerson)
                        if result:
                            Insert(idPerson, temperature)
                            insert_counter += 1
                            print('\033[92m' + 'บันทึกข้อมูลของ : ' +
                                  name + '\033[92m' + '   เรียบร้อยแล้ว' + '\033[0m')
                            # client_led.publish("control/led", "1")
                            if insert_counter >= max_insertions:
                                cap.release()
                                cv2.destroyAllWindows()
                                return
                        else:
                            print('\033[91m' +
                                  'ไม่พบข้อมูลในฐานข้อมูล' + '\033[0m')
                            client_led.publish("control/led", "3")
                            cv2.destroyAllWindows()
                            return
            cv2.imshow('frame', frame)
            cv2.waitKey(1)


if __name__ == "__main__":
    connect_to_mqtt_broker()
