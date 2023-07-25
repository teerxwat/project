import cv2
import os


def extract_face_features(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        '../../libs/haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) == 0:
        return None
    x, y, w, h = faces[0]
    face = image[y:y+h, x:x+w]
    return face


def select_best_face(folder):
    face_images = []
    for filename in os.listdir(folder):
        image = cv2.imread(os.path.join(folder, filename))
        face = extract_face_features(image)
        if face is not None:
            face_images.append(face)
    if len(face_images) == 0:
        return None
    return face_images[0]


selected_face = select_best_face('../../static/snap_picture/')
if selected_face is not None:
    if not os.path.exists('../../static/snap_picture/temp_picture'):
        os.makedirs('../../static/snap_picture/temp_picture')
    cv2.imwrite(
        '../../static/snap_picture/temp_picture/selected_face.jpg', selected_face)
    print('Best face image saved in temp_picture/selected_face.jpg')
else:
    print('No face detected in the images')
