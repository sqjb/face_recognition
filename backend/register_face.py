import os.path
import time

import cv2
import dlib
import numpy as np

from settings import IMAGE_FOLDER
from db import Representation, add
face_detector = dlib.get_frontal_face_detector()
face_predictor = dlib.shape_predictor("./models/shape_predictor_5_face_landmarks.dat")
face_rec = dlib.face_recognition_model_v1("./models/dlib_face_recognition_resnet_model_v1.dat")


def register_one_face(name: str, image_file: str):
    try:
        image = cv2.imread(image_file)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        dets = face_detector(rgb)
        if len(dets) != 1:
            print(f"{len(dets)} face in image , support one face in image")
        landmarks = face_predictor(rgb, dets[0])
        chip = dlib.get_face_chip(rgb, landmarks, size=150)
        descriptor = face_rec.compute_face_descriptor(chip)
        # save image
        folder = os.path.join(IMAGE_FOLDER, name)
        if not os.path.exists(folder):
            os.mkdir(folder)
        image_path = os.path.join(folder, f"{int(time.time())}.jpg")
        ret = cv2.imwrite(image_path, image)
        if ret:
            rep = Representation(name, image_path, np.array(descriptor))
            if add(rep):
                print(f"add {name} face {image_path} successfully..")
    except BaseException as e:
        print(e)


if __name__ == '__main__':
    register_one_face("xietingfeng", "./datas/xtf.jpg")
