import base64
import json
import os.path
import random
import threading
import time

import cv2
import dlib
import numpy as np
import flask
from flask import Flask, render_template, request
from flask_cors import CORS
from db import RepresentationDB
from dataclasses import dataclass
import queue

face_detector = dlib.get_frontal_face_detector()
face_predictor = dlib.shape_predictor("./models/shape_predictor_5_face_landmarks.dat")
face_rec = dlib.face_recognition_model_v1("./models/dlib_face_recognition_resnet_model_v1.dat")

database = RepresentationDB("./reps.pkl")
app = Flask("face recognition", static_folder='images')
CORS(app)


@app.route("/image", methods=['POST'])
def post_image():
    thr_conf = 0.4
    file = request.files.get('image')
    buf = file.stream.read()
    image = cv2.imdecode(np.frombuffer(buf, np.uint8), cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    dets = face_detector(rgb)
    if len(dets) == 0:
        return {
            'result': False,
            'message': 'no face in image'
        }
    elif len(dets) > 1:
        return {
            'result': False,
            'message': f'support only one face in image, detected {len(dets)} faces'
        }
    landmarks = face_predictor(rgb, dets[0])
    face = dlib.get_face_chip(rgb, landmarks, size=150)
    descriptor = face_rec.compute_face_descriptor(face)
    dist, r = database.find_one(np.array(descriptor), thr_conf)
    if r is not None:
        return {
            'result': True,
            'message': 'find face successfully',
            'data': {
                'name': r.name,
                'path': r.image_path,
                'registered_at': r.registered_at,
                'distance': dist
            }
        }
    else:
        return {
            'result': False,
            'message': f'not find face with distance threshold = {thr_conf}'
        }


@app.route("/faces", methods=['GET'])
def get_faces():
    page_size = request.args.get('page_size', 0, type=int)
    page_no = request.args.get('page_no', 0, type=int)

    if page_size == 0:
        reps, total = database.findAll()
    else:
        reps, total = database.find(page_no, page_size)
    ret = []
    for rep in reps:
        ret.append({
            'name': rep.name,
            'path': rep.image_path,
            'registered_at': rep.registered_at
        })

    return {'data': ret, 'total': total}


@app.route("/video/upload", methods=['POST'])
def video_upload():
    try:
        file = request.files.get('file')
        tempdir = os.path.join(".", "temp")
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)
        filename = os.path.join(tempdir, f'upload_{int(time.time())}_{file.filename}')
        file.save(filename)
        return {'result': True, 'message': 'success', 'data': filename}
    except BaseException as e:
        return {'result': False, 'message': str(e)}


def create_sse_message(message_type: str, image_str: str, extra: dict = None):
    return 'data:{}\n\n'.format(json.dumps({'type': message_type, 'image': image_str, 'extra': extra}))


def cv2_to_base64(image):
    image1 = cv2.imencode('.jpg', image)[1]
    image_code = str(base64.b64encode(image1))[2:-1]
    return "data:image/jpeg;base64," + image_code


def read_frame(source: str | int, q: queue.Queue):
    cap = cv2.VideoCapture(source)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            h, w = frame.shape[:2]
            if h > 380 or w > 640:
                frame = cv2.resize(frame, [640, 380], dst=None, interpolation=cv2.INTER_LINEAR)
            try:
                q.put(frame, block=True, timeout=2)
            except queue.Full:
                print("frame queue still full after 2 seconds waiting, exit")
                break
    cap.release()


def face(fq: queue.Queue, dq: queue.Queue):
    lbs = []  # last bbox list
    cbs = []  # current bbox list
    names = []
    chips = []
    interval = 8
    force_interval = 60
    frame_cnt = 0
    while True:
        try:
            f = fq.get()
            if frame_cnt % interval == 0:
                rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
                cbs = face_detector(rgb)
            elif len(lbs) != len(cbs) or frame_cnt % force_interval == 0:
                # face changed, run recognition
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
            break


@app.route("/video", methods=['GET'])
def play():
    # generator
    def generator(rq: queue.Queue):
        while True:
            try:
                image = rq.get(block=True, timeout=2)
                if image is not None:
                    code = cv2_to_base64(image)
                    yield create_sse_message("image", code)
            except BaseException as e:
                print(e)
                break

    file = request.args.get('file')
    q1 = queue.Queue(maxsize=25)
    q2 = queue.Queue(maxsize=25)
    ths = [
        threading.Thread(target=read_frame, args=(file, q1,)),
        threading.Thread(target=face, args=(q1, q2,))
    ]
    [th.start() for th in ths]
    if file is None:
        return flask.Response(create_sse_message('error', ''), mimetype='text/event-stream')
    else:
        return flask.Response(generator(q2), mimetype='text/event-stream')


@app.route("/camera", methods=['GET'])
def camera():
    def generator(rq: queue.Queue):
        while True:
            try:
                image = rq.get(block=True, timeout=10)
                if image is not None:
                    code = cv2_to_base64(image)
                    yield create_sse_message("image", code)
            except BaseException as e:
                print(e)
                break

    # test camera
    cap = cv2.VideoCapture(0)
    if cap is None or not cap.isOpened():
        return flask.Response(
            create_sse_message(
                'error',
                '',
                'unable to open camera'),
            mimetype='text/event-stream'
        )
    cap.release()
    q1 = queue.Queue(maxsize=25)
    q2 = queue.Queue(maxsize=25)
    ths = [
        threading.Thread(target=read_frame, args=(0, q1,)),
        threading.Thread(target=face, args=(q1, q2,))
    ]
    [th.start() for th in ths]

    return flask.Response(generator(q2), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run()
