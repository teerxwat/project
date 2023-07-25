import cv2
import glob
from re import A, S
import numpy as np
import dlib
import os
import pickle

face_cascade = cv2.CascadeClassifier(
    '../../libs/haarcascade_frontalface_default.xml')
path = "../../static/default_picture/*.*"
img_number = 1  # Start an iterator for image number.
img_list = glob.glob(path)


def checkName(file):
    # print(file)
    if len(file) == 46:
        namefile = file[-17:-4]
    # elif len(file) == 35:
    #     namefile = file[-6:-4]
    # elif len(file) == 36:
    #     namefile = file[-7:-4]
    # elif len(file) == 37:
    #     namefile = file[-8:-4]
    # elif len(file) == 38:
    #     namefile = file[-9:-4]
    else:
        namefile = "default"
    return namefile


for file in img_list[0:25000]:
    namefile = checkName(file)
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
        cv2.imwrite("../../static/crop_picture/" + namefile + ".jpg", resized)
        img_number += 1
    else:
        print("ไม่สามารถ Detect ได้  : " + namefile + ' Path : ' + file)


path = '../../static/crop_picture/'
SaveFilePathModelTrand = '../../static/model/model.pk'
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor('../../libs/shape_predictor_68_face_landmarks.dat')
model = dlib.face_recognition_model_v1(
    '../../libs/dlib_face_recognition_resnet_model_v1.dat')
FACE_DESC = []
FACE_NAME = []
s = 0
for fn in os.listdir(path):
    s = s+1
    if fn.endswith('.jpg'):
        img = cv2.imread(path + fn)[:, :, ::-1]
        dets = detector(img, 2)
        for k, d in enumerate(dets):
            shape = sp(img, d)
            face_desc = model.compute_face_descriptor(img, shape, 2)
            FACE_DESC.append(face_desc)
            print('Loading...', fn)
            FACE_NAME.append(fn[:fn.index('.')])
pickle.dump((FACE_DESC, FACE_NAME), open(SaveFilePathModelTrand, 'wb'))
