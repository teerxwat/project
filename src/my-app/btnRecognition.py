import paho.mqtt.client as mqtt
import cv2
import numpy as np
import time
import os
import glob
import dlib
import pickle
import mysql.connector

# MQTT broker details
mqtt_broker = "server-mqtt.thddns.net"
mqtt_port = 3333
mqtt_username = "mqtt"
mqtt_password = "admin1234"
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
            snapshot()  # Call snapshot function
            sort_faces()  # Call sort_faces function
            process_images()
        elif sensor_value == 0 and file_operation_active:
            client.publish("Control/FaceRecognition", "0")
            file_operation_active = False

    elif msg.topic == topic_Temperature:
        temperature_value = float(msg.payload)
        print("Temperature Value:", temperature_value)
        # ทำสิ่งที่ต้องการด้วยค่า temperature_value ที่ได้รับมา
        # เช่น ส่งค่าไปยังอุปกรณ์อื่น หรือเก็บค่าลงฐานข้อมูล หรือประมวลผลอื่น ๆ


def connect_to_mqtt_broker():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_broker, mqtt_port, 60)
    client.loop_forever()


def snapshot():
    cap = cv2.VideoCapture("http://192.168.1.113:81/stream")
    if not cap.isOpened():
        print("Unable to connect to ESP32-CAM")
        exit()

    folder = "../../static/recognition/snap_picture_recognition"
    if not os.path.exists(folder):
        os.makedirs(folder)

    for i in range(10):
        ret, frame = cap.read()
        if not ret:
            print("Unable to capture frame from ESP32-CAM")
            exit()
        cv2.imwrite(os.path.join(folder, str(i) + ".jpg"), frame)
        print("Image " + str(i) + " saved successfully")
        time.sleep(0.01)  # delay for 1 millisecond

    cap.release()


def extract_face_features(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) == 0:
        return None
    x, y, w, h = faces[0]

    # Adjust the rectangle coordinates to include the entire head
    x -= int(w * 0.1)
    y -= int(h * 0.3)
    w += int(w * 0.2)
    h += int(h * 0.4)

    # Ensure the rectangle coordinates are within the image boundaries
    x = max(x, 0)
    y = max(y, 0)
    w = min(w, image.shape[1] - x)
    h = min(h, image.shape[0] - y)

    face = image[y:y+h, x:x+w]
    return face


def compute_face_quality(face):
    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)  # Compute average brightness of the face image
    # Compute sharpness of the face image using Laplacian variance
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    # Compute face quality as the average of brightness and sharpness
    face_quality = (brightness + sharpness) / 2
    return face_quality


def select_best_face(folder):
    face_images = []
    face_scores = []

    for filename in os.listdir(folder):
        image = cv2.imread(os.path.join(folder, filename))
        face = extract_face_features(image)
        if face is not None:
            face_images.append(face)
            # Replace with your face quality assessment function
            face_scores.append(compute_face_quality(face))

    if len(face_images) == 0:
        return None

    # Find the index of the face with the highest quality score
    best_score_index = np.argmax(face_scores)
    return face_images[best_score_index]


def sort_faces():
    selected_face = select_best_face(
        '../../static/recognition/snap_picture_recognition/')
    if selected_face is not None:
        if not os.path.exists('../../static/recognition/sort_picture_recognition'):
            os.makedirs('../../static/recognition/sort_picture_recognition')

        # Resize the selected face to 400x400
        resized_face = cv2.resize(selected_face, (300, 300))
        cv2.imwrite(
            '../../static/recognition/sort_picture_recognition/1.jpg', resized_face)
        print('Best face image saved in recognition/sort_picture_recognition/selected_face.jpg')
    else:
        print('No face detected in the images')


def process_images():
    # Create a client instance
    client = mqtt.Client()

    # Set the username and password
    client.username_pw_set("mqtt", "admin1234")

    # Connect to the broker
    client.connect("server-mqtt.thddns.net", 3333)

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

    image_folder = '../../static/recognition/sort_picture_recognition/'
    image_files = os.listdir(image_folder)

    def Select(idPerson):
        querySelectDetect = "SELECT first_name FROM tb_users WHERE id_user='" + idPerson + "'"
        mycursor.execute(querySelectDetect)
        myresultSelect = mycursor.fetchall()
        if myresultSelect:
            return myresultSelect[0][0]
        else:
            return '\033[91m' + 'ไม่พบข้อมูลในระบบ'

    def Insert(idPerson):
        queryInsertDateDetect = "INSERT INTO tb_userlogs(id_user, report_data, times_temp, temperature) VALUES (%(id_user)s, 'Data Report', NOW(), 0)"
        val = {'id_user': idPerson}
        print("Insert Query:", queryInsertDateDetect)
        print("Insert Values:", val)
        mycursor.execute(queryInsertDateDetect, val)
        cnx.commit()
        # client.publish("Control/FaceRecognition", "1")

    current_face = None
    last_reset_time = time.time()

    # Retrieve the list of user IDs from the database
    def CheckID(idPerson):
        queryGetUserIDs = "SELECT id_user FROM tb_users WHERE id_user = %(idPerson)s"
        val = {'idPerson': idPerson}
        mycursor.execute(queryGetUserIDs, val)
        myresult = mycursor.fetchall()
        return myresult

    for image_file in image_files:
        image_path = os.path.join(image_folder, image_file)
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            img_face = img[y-10:y+h+10, x-10:x+w+10]
            dets = detector(img_face, 1)

            for k, d in enumerate(dets):
                shape = sp(img_face, d)
                face_desc0 = model.compute_face_descriptor(img_face, shape, 1)
                d = []

                for face_desc in FACE_DESC:
                    d.append(np.linalg.norm(
                        np.array(face_desc) - np.array(face_desc0)))
                d = np.array(d)
                idx = np.argmin(d)

                if d[idx] < 0.3:
                    idPerson = FACE_NAME[idx]
                    name = Select(idPerson)
                    cv2.putText(img, name, (x, y-5),
                                cv2.FONT_ITALIC, 0.7, (0, 0, 255), 2)
                    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    # print(idPerson)
                    # Fetch the result from the CheckID function
                    result = CheckID(idPerson)
                    if result:  # Check if the result is not empty
                        Insert(idPerson)
                        current_face = idPerson  # Update the current face
                        print('\033[92m' + 'บันทึกข้อมูลของ : ' + name +
                              '\033[92m' + '   เรียบร้อยแล้ว' + '\033[0m')
                    else:
                        print('\033[91m' + 'ไม่มีข้อมูลในระบบ' + '\033[0m')

        # cv2.imshow('frame', img)
        cv2.waitKey(1)
        elapsed_time = time.time() - last_reset_time

        if elapsed_time > 60:
            current_face = None
            last_reset_time = time.time()


if __name__ == "__main__":
    connect_to_mqtt_broker()
    sort_faces()
    process_images()
