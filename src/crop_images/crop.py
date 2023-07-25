import cv2
import glob

face_cascade = cv2.CascadeClassifier('../../libs/haarcascade_frontalface_default.xml')
path = "../../static/default_picture/*.*"
img_number = 1  # Start an iterator for image number.
img_list = glob.glob(path)


def checkName(file):
    if len(file) == 34:
        namefile = file[-5:-4]
    elif len(file) == 35:
        namefile = file[-6:-4]
    elif len(file) == 36:
        namefile = file[-7:-4]
    elif len(file) == 37:
        namefile = file[-8:-4]
    elif len(file) == 38:
        namefile = file[-9:-4]
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
