import cv2
import time

# https://www.youtube.com/watch?v=dJjzTo8_x3c&ab_channel=%EB%B9%B5%ED%98%95%EC%9D%98%EA%B0%9C%EB%B0%9C%EB%8F%84%EC%83%81%EA%B5%AD
# https://github.com/kairess/face_detection_comparison
# https://mslilsunshine.tistory.com/70

# load model
model_path = 'models/opencv_face_detector_uint8.pb'
config_path = 'models/opencv_face_detector.pbtxt'
net = cv2.dnn.readNetFromTensorflow(model_path, config_path)

conf_threshold = 0.7

frame_count, tt = 0, 0

cap = cv2.VideoCapture(0)  # 카메라 연결
if not cap.isOpened():
    print('Video open failed!')


while True:
    ret, frame = cap.read()  # 카메라 영상 읽기
    if not ret:
        break

    frame_count += 1

    start_time = time.time()

    # 노이즈 제거 - GaussianBlur 사용
    filter_frame = cv2.GaussianBlur(frame, (0, 0), 2.0)

    img = filter_frame.copy()
    h, w, _ = img.shape
    blob = cv2.dnn.blobFromImage(img, 1.0, (300, 300), [104, 117, 123], False, False)
    net.setInput(blob)

    # inference, find faces
    detections = net.forward()

    dst_img = []
    # postprocessing
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * w)
            y1 = int(detections[0, 0, i, 4] * h)
            x2 = int(detections[0, 0, i, 5] * w)
            y2 = int(detections[0, 0, i, 6] * h)

            # draw rects
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), int(round(h/150)), cv2.LINE_AA)
            cv2.putText(img, '%.2f%%' % (confidence * 100.), (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

            dst = img[x1:x2, y1:y2].copy()
            dst_img.insert(dst)
    # inference time
    tt += time.time() - start_time
    fps = frame_count / tt
    cv2.putText(img, 'FPS(dnn): %.2f' % (fps), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,
                cv2.LINE_AA)

    # visualize
    cv2.imshow('result', img)
    if cv2.waitKey(1) == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()

