import cv2
import numpy as np
import dlib
import pickle
import mysql.connector
import time
import paho.mqtt.client as mqtt
import os


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
        # print("Insert Query:", queryInsertDateDetect)
        # print("Insert Values:", val)
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
                    print(idPerson)
                    # Fetch the result from the CheckID function
                    result = CheckID(idPerson)
                    if result:  # Check if the result is not empty
                        Insert(idPerson)
                        current_face = idPerson  # Update the current face
                        print('\033[92m' + 'บันทึกข้อมูลของ : ' +
                              name + '\033[92m' + '   เรียบร้อยแล้ว')
                    else:
                        print('\033[91m' + 'ไม่มีข้อมูลในระบบ')

        cv2.imshow('frame', img)
        cv2.waitKey(1)
        elapsed_time = time.time() - last_reset_time

        if elapsed_time > 60:
            current_face = None
            last_reset_time = time.time()


# Call the function
process_images()
