import time

import cv2
import dlib
import numpy as np

from db import RepresentationDB

database = RepresentationDB("./reps.pkl")

face_detector = dlib.get_frontal_face_detector()
face_predictor = dlib.shape_predictor("./models/shape_predictor_5_face_landmarks.dat")
face_rec = dlib.face_recognition_model_v1("./models/dlib_face_recognition_resnet_model_v1.dat")

if __name__ == '__main__':
    dist_thr = 0.5
    path = "datas/test.png"

    t1 = time.time()
    image = cv2.imread(path)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    dets = face_detector(rgb)
    for i, det in enumerate(dets):
        lm = face_predictor(rgb, det)
        face = dlib.get_face_chip(rgb, lm, size=150)
        descriptor = face_rec.compute_face_descriptor(face)
        dist, r = database.find_one(np.array(descriptor), dist_thr)
        if r is not None:
            print(dist, r.name, r.image_path)
        else:
            print(f"not find face by thr:{dist_thr}")
    t2 = time.time()
    print(f"search {len(dets)} faces in {t2 - t1}s")
