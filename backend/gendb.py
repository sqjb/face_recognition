import os.path
import pickle
import time

from tqdm import tqdm
import cv2
import dlib
import numpy as np

from settings import IMAGE_FOLDER, DB_FILE, IMAGE_TYPE
import db
face_detector = dlib.get_frontal_face_detector()
face_predictor = dlib.shape_predictor("./models/shape_predictor_5_face_landmarks.dat")
face_rec = dlib.face_recognition_model_v1("./models/dlib_face_recognition_resnet_model_v1.dat")

if __name__ == '__main__':
    """
        create 'repdb.pkl' according image folder..
    """
    reps = []
    try:
        for person_name in tqdm(os.listdir(IMAGE_FOLDER)):
            for image_name in os.listdir(os.path.join(IMAGE_FOLDER, person_name)):
                file_name = os.path.join(IMAGE_FOLDER, person_name, image_name)
                if not file_name.lower().endswith(IMAGE_TYPE):
                    print(f"\nskip unsupported image type: {file_name}")
                    continue
                else:
                    im = cv2.imread(file_name)
                    rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
                    dets = face_detector(rgb)
                    if len(dets) != 1:
                        print(f"{len(dets)} face in image {file_name}, support one face in image")
                        continue
                    landmarks = face_predictor(rgb, dets[0])
                    face = dlib.get_face_chip(rgb, landmarks, size=150)
                    descriptor = face_rec.compute_face_descriptor(face)
                    # desc = np.array(descriptor)
                    rep = db.Representation(person_name, file_name, int(time.time()), np.array(descriptor))
                    reps.append(rep)
    except BaseException as e:
        print(e)
    finally:
        if len(reps) > 0:
            print(f"save {len(reps)} faces...")
            with open(DB_FILE, "wb") as f:
                pickle.dump(reps, f)
