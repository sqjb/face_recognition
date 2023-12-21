"""
face recognition for video
"""
import os.path
import threading
import queue
import time

import cv2
import dlib
import numpy as np
from db import RepresentationDB

database = RepresentationDB(os.path.join("..", "reps.pkl"))
face_detector = dlib.get_frontal_face_detector()
face_predictor = dlib.shape_predictor("../models/shape_predictor_5_face_landmarks.dat")
face_rec = dlib.face_recognition_model_v1("../models/dlib_face_recognition_resnet_model_v1.dat")
_SOURCE = "./test.mp4"
_STOP = False


def read(q: queue.Queue):
    global _STOP
    cap = cv2.VideoCapture(_SOURCE)
    while cap.isOpened() and not _STOP:
        ret, frame = cap.read()
        if ret:
            h, w = frame.shape[:2]
            if h > 380 or w > 640:
                frame = cv2.resize(frame, [640, 380], dst=None, interpolation=cv2.INTER_LINEAR)
            try:
                q.put(frame, block=True, timeout=2)
            except queue.Full:
                print("frame queue still full after 2 seconds waiting, exit")
                _STOP = True
    cap.release()


def face_v1(fq: queue.Queue, dq: queue.Queue):
    lbs = []  # last bbox list
    cbs = []  # current bbox list
    names = []
    interval = 8
    force_interval = 60
    global _STOP
    frame_cnt = 0
    while not _STOP:
        f = fq.get()
        try:
            if frame_cnt % interval == 0:
                print(f"detect on frame:{frame_cnt}")
                rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
                # update lbs and cbs
                # lbs = cbs
                cbs = face_detector(rgb)
            elif len(lbs) != len(cbs) or frame_cnt % force_interval == 0:
                names = []
                for k, box in enumerate(cbs):
                    rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
                    lm = face_predictor(rgb, box)
                    c = dlib.get_face_chip(rgb, lm, size=150)
                    descriptor = face_rec.compute_face_descriptor(c)
                    _, r = database.find_one(np.array(descriptor), 0.5)
                    name = r.name if r is not None else "unknown"
                    names.append(name)
                lbs = cbs

            # draw bbox and names
            for k, box in enumerate(cbs):
                tl = box.tl_corner()
                br = box.br_corner()
                cv2.rectangle(f, [tl.x, tl.y], [br.x, br.y], color=(0, 255, 0), thickness=2)
                if len(names) == len(cbs):
                    cv2.putText(f, names[k], [tl.x, tl.y], fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.0,
                                color=(0, 255, 0),
                                thickness=2)

            frame_cnt += 1
            dq.put(f, block=True, timeout=2)
        except BaseException as e:
            print(e)
            _STOP = True
            break


def display(q: queue.Queue):
    global _STOP
    cv2.namedWindow("display", cv2.WINDOW_AUTOSIZE)
    base = time.time()
    while True:
        f = q.get()
        # draw FPS
        fps = f"FPS: {1. / (time.time() - base):.2f}"
        cv2.putText(f, fps, [10, 30], fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.0, color=(0, 255, 0),
                    thickness=2)
        base = time.time()

        # draw image
        cv2.imshow("display", f)
        if cv2.waitKey(1) & 0xff == ord('q'):
            break
    _STOP = True
    cv2.destroyAllWindows()


if __name__ == '__main__':
    q1 = queue.Queue(maxsize=25)
    q2 = queue.Queue(maxsize=25)
    ths = [
        threading.Thread(target=read, args=(q1,)),
        threading.Thread(target=face_v1, args=(q1, q2,)),
        threading.Thread(target=display, args=(q2,))
    ]

    [th.start() for th in ths]

    while not _STOP:
        time.sleep(2)
    print("program exit normally")
