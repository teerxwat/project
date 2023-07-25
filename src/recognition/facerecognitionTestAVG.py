import os
import cv2
import numpy as np
import dlib
import pickle
import mysql.connector
import time
import paho.mqtt.client as mqtt
import datetime


def process_image(file_path):
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
        open('../../static/Data/model/model.pk', 'rb'))

    def Select(idPerson):
        querySelectDetect = "SELECT first_name FROM tb_users WHERE studentid='" + idPerson + "'"
        mycursor.execute(querySelectDetect)
        myresultSelect = mycursor.fetchall()
        if myresultSelect:
            return myresultSelect[0][0]
        else:
            return '\033[91m' + 'ไม่พบข้อมูลในระบบ'

    def Insert(idPerson):
        queryInsertDateDetect = "INSERT INTO tb_user_logs(id_user, report_date, timestamp, temperature, year) VALUES (%(id_user)s, %(report_date)s, NOW(), 0, %(year)s)"
        val = {'id_user': idPerson, 'report_date': datetime.date.today(),
               'year': datetime.date.today().year}
        # print("Insert Query:", queryInsertDateDetect)
        # print("Insert Values:", val)
        mycursor.execute(queryInsertDateDetect, val)
        cnx.commit()

    def CheckID(idPerson):
        queryGetUserIDs = "SELECT id_user FROM tb_users WHERE studentid = %(idPerson)s"
        val = {'idPerson': idPerson}
        mycursor.execute(queryGetUserIDs, val)
        myresult = mycursor.fetchall()
        return myresult

    # Load the image
    frame = cv2.imread(file_path)

    # Process the image
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)
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
                    Insert(idPerson)
                    print('\033[92m' + 'บันทึกข้อมูลของ : ' +
                          name + '\033[92m' + '   เรียบร้อยแล้ว' + '\033[0m')
                else:
                    print('\033[91m' + 'ไม่มีข้อมูลในระบบ' + '\033[0m')

    # cv2.imshow('image', frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Directory path
directory = r'D:\Project\static\Data\pictuers'

# Process each image in the directory
for filename in os.listdir(directory):
    if filename.endswith('.jpg') or filename.endswith('.png'):
        file_path = os.path.join(directory, filename)
        process_image(file_path)
