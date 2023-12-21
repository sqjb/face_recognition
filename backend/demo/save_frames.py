import os.path

import cv2

path = "./test.mp4"
folder = os.path.join(".", "frames")

if __name__ == '__main__':
    if not os.path.exists(folder):
        os.makedirs(folder)

    cap = cv2.VideoCapture(path)
    cnt = 0
    while cap.isOpened():
        _, f = cap.read()
        if f is not None:
            cv2.imwrite(os.path.join(folder, f"frame_{cnt}.jpg"), f)
            cnt += 1
    cap.release()