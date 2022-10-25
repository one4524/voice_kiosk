import cv2
import dlib
import numpy as np
from imutils import face_utils
from keras.models import load_model
import tensorflow


# https://github.com/kairess/eye_blink_detector
# https://github.com/davisking/dlib-models
# https://www.youtube.com/watch?v=tpWVyJqehG4&ab_channel=%EB%B9%B5%ED%98%95%EC%9D%98%EA%B0%9C%EB%B0%9C%EB%8F%84%EC%83%81%EA%B5%AD

# pip install opencv-python
# pip install imutils
# conda install tensorflow

# https://cmake.org/download/ 에서 cmake 설치
# pip install cmake

# visual studio c++ 관련 빌드 도구와 cmake 도구 설치
# https://visualstudio.microsoft.com/ko/visual-cpp-build-tools/

# dlib 설치
# https://velog.io/@siyeon-hwang/anaconda-dlib-%EC%84%A4%EC%B9%98%ED%95%98%EA%B8%B0
# 아래 순서대로 설치
# conda install -c conda-forge dlib
# conda install -c conda-forge/label/cf201901 dlib
# conda install -c conda-forge/label/cf202003 dlib

def crop_eye(gray, eye_points):
    IMG_SIZE = (34, 26)
    x1, y1 = np.amin(eye_points, axis=0)
    x2, y2 = np.amax(eye_points, axis=0)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

    w = (x2 - x1) * 1.2
    h = w * IMG_SIZE[1] / IMG_SIZE[0]

    margin_x, margin_y = w / 2, h / 2

    min_x, min_y = int(cx - margin_x), int(cy - margin_y)
    max_x, max_y = int(cx + margin_x), int(cy + margin_y)

    eye_rect = np.rint([min_x, min_y, max_x, max_y]).astype(np.int)

    eye_img = gray[eye_rect[1]:eye_rect[3], eye_rect[0]:eye_rect[2]]

    return eye_img, eye_rect


def eyes_detect():
    IMG_SIZE = (34, 26)

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('Camera/models/shape_predictor_68_face_landmarks.dat')

    model = load_model('Camera/models/2018_12_17_22_58_35.h5')
    model.summary()

    # main
    # cap = cv2.VideoCapture('Camera/woman.mp4')
    cap = cv2.VideoCapture(0)  # 카메라 연결

    if not cap.isOpened():
        print('Video open failed!')


    count = 0
    while cap.isOpened():
        ret, img_ori = cap.read()

        if not ret:
            break

        img_ori = cv2.resize(img_ori, dsize=(0, 0), fx=0.5, fy=0.5)

        img = img_ori.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = detector(gray)

        for face in faces:
            shapes = predictor(gray, face)
            shapes = face_utils.shape_to_np(shapes)

            eye_img_l, eye_rect_l = crop_eye(gray, eye_points=shapes[36:42])
            eye_img_r, eye_rect_r = crop_eye(gray, eye_points=shapes[42:48])

            eye_img_l = cv2.resize(eye_img_l, dsize=IMG_SIZE)
            eye_img_r = cv2.resize(eye_img_r, dsize=IMG_SIZE)
            eye_img_r = cv2.flip(eye_img_r, flipCode=1)

            # cv2.imshow('l', eye_img_l)
            # cv2.imshow('r', eye_img_r)

            eye_input_l = eye_img_l.copy().reshape((1, IMG_SIZE[1], IMG_SIZE[0], 1)).astype(np.float32) / 255.
            eye_input_r = eye_img_r.copy().reshape((1, IMG_SIZE[1], IMG_SIZE[0], 1)).astype(np.float32) / 255.

            pred_l = model.predict(eye_input_l)
            pred_r = model.predict(eye_input_r)

            # visualize
            state_l = 'O %.1f' if pred_l > 0.1 else '- %.1f'
            state_r = 'O %.1f' if pred_r > 0.1 else '- %.1f'

            state_l = state_l % pred_l
            state_r = state_r % pred_r

            if pred_l < 0.3 and pred_r < 0.3:
                count += 1

            cv2.rectangle(img, pt1=tuple(eye_rect_l[0:2]), pt2=tuple(eye_rect_l[2:4]), color=(255, 255, 255),
                          thickness=2)
            cv2.rectangle(img, pt1=tuple(eye_rect_r[0:2]), pt2=tuple(eye_rect_r[2:4]), color=(255, 255, 255),
                          thickness=2)

            cv2.putText(img, state_l, tuple(eye_rect_l[0:2]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(img, state_r, tuple(eye_rect_r[0:2]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow('result', img)
        if cv2.waitKey(1) == ord('q'):
            break

        if count > 16:
            return True
