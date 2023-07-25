from re import A, S
import numpy as np
import cv2
import dlib
import os
import pickle
path = '../../static/crop_picture/'
SaveFilePathModelTrand = '../../static/model/model.pk'
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(
    'D:\Project\libs\shape_predictor_68_face_landmarks.dat')
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
