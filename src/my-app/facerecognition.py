import cv2
import os
import numpy as np


def train_face_recognizer():
    face_cascade = cv2.CascadeClassifier(
        '../../libs/haarcascade_frontalface_default.xml')
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    faces_folder = "../../static/recognition/faces"
    users = os.listdir(faces_folder)

    faces = []
    labels = []

    for i, user in enumerate(users):
        user_folder = os.path.join(faces_folder, user)
        images = os.listdir(user_folder)

        for image in images:
            image_path = os.path.join(user_folder, image)
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in face:
                faces.append(gray[y:y+h, x:x+w])
                labels.append(i)

    recognizer.train(faces, np.array(labels))
    recognizer.write("../../libs/trainer.yml")
    print("Face recognizer trained successfully!")


if __name__ == "__main__":
    train_face_recognizer()
