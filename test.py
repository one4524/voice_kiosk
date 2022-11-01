# -*- coding:utf-8 -*-
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = "2"
import sys
import urllib3
import json
import base64
import speech_recognition as sr
from hanspell import spell_checker
import cv2
import dlib
import numpy as np
from imutils import face_utils
from tensorflow.keras.models import load_model
from PyQt5 import uic
from PyQt5.QtCore import Qt, QEventLoop, QTimer, QSize, QThread
from PyQt5.QtGui import QPixmap, QIcon, QFontDatabase, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QLabel, QWidget, QVBoxLayout
import sqlite3
import playsound
from gtts import gTTS
import pyaudio

pyaudio.get_portaudio_version()

"""
1. 기본
2. 텍스트 자모 유사도 분석
3. DB
4. 눈 인식 쓰레드
5. 오디오 클래스
6. 오디오 루틴
7. 오디오 쓰레드
8. 윈도우 클래스
"""

## ----------------------------- 기본 ---------------------------- ##

menu = {
    'korean': ['김치햄치즈볶음밥', '소금덮밥', '뼈다귀해장국', '소고기미역국', '냉면', '간장불고기', '제육볶음'],
    'chinese': ['짜장면', '짬뽕', '계란볶음밥', '탕수육', '군만두'],
    'schoolfood': ['떡볶이', '라볶이', '라면', '순대', '오므라이스', '야채김밥', '참치김밥'],
    'Westernfood': ['크림파스타', '토마토파스타', '알리오올리오', '연어샐러드', '감바스'],
    'japanesefood': ['왕돈까스', '치킨까스', '치즈돈까스', '냉모밀', '우동', '김치나베', '돈까스나베'],
    'beverage': ['물', '콜라', '사이다', '환타', '제로콜라', '제로사이다']
}
menu_price = {
    'korean': {'김치햄치즈볶음밥': 4500, '소금덮밥': 4500, '뼈다귀해장국': 4000, '소고기미역국': 4000, '냉면': 4000, '간장불고기': 4500, '제육볶음': 4500},
    'chinese': {'짜장면': 2500, '짬뽕': 2500, '계란볶음밥': 3800, '탕수육': 5000, '군만두': 3000},
    'schoolfood': {'떡볶이': 3000, '라볶이': 3000, '라면': 2500, '순대': 3000, '오므라이스': 3800, '야채김밥': 2000, '참치김밥': 2200},
    'Westernfood': {'크림파스타': 3000, '토마토파스타': 3000, '알리오올리오': 3000, '연어샐러드': 3000, '감바스': 3000},
    'japanesefood': {'왕돈까스': 4500, '치킨까스': 4500, '치즈돈까스': 4500, '냉모밀': 2500, '우동': 2500, '김치나베': 3500, '돈까스나베': 4000},
    'beverage': {'물': 1000, '콜라': 1000, '사이다': 1000, '환타': 1000, '제로콜라': 1000, '제로사이다': 1000}
}
table_idx_lookup = {'korean': 0, 'chinese': 1, 'schoolfood': 2, 'Westernfood': 3, 'japanesefood': 4, 'beverage': 5}
menu_list = ['korean', 'chinese', 'schoolfood', 'Westernfood', 'japanesefood', 'beverage']


def make_tts(text):
    tts_make = gTTS(text=text, lang='ko')

    tts_make.save(resource_path("test_files/order_list.mp3"))


# UI파일 연결
# 단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# python실행파일 디렉토리
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
form = resource_path(BASE_DIR + '/test_files/main.ui')
form_class = uic.loadUiType(form)[0]


def reset():
    loop = QEventLoop()
    QTimer.singleShot(3000, loop.quit)  # msec
    loop.exec_()


def compare_text(audio_word_list, compare_list):
    similarity_score = 10
    similarity_word_num = -1

    for audio_word in audio_word_list:
        for index, compare_word in enumerate(compare_list):
            similarity_score_tmp = jamo_levenshtein(audio_word, compare_word)
            # 유사도 거리가 일정 수준 가깝고, 기존 보다 가까울 경우에 인정
            if similarity_score_tmp <= 0.5 and similarity_score > similarity_score_tmp:
                similarity_score = similarity_score_tmp
                similarity_word_num = index
                print("similarity-- ", similarity_score, "/ keyword--", compare_word, "/ audio_word--", audio_word)

    if similarity_word_num != -1:
        return similarity_word_num
    else:
        return -1


## ---------------------------- 기본 끝 ---------------------------- ##

"""
1. 기본
2. 텍스트 자모 유사도 분석
3. DB
4. 눈 인식 쓰레드
5. 오디오 클래스
6. 오디오 루틴
7. 오디오 쓰레드
8. 윈도우 클래스
"""

## --------------------- 자모 유사도 분석 클래스 및 변수 시작 ------------------- ##

kor_begin = 44032
kor_end = 55203
chosung_base = 588
jungsung_base = 28
jaum_begin = 12593
jaum_end = 12622
moum_begin = 12623
moum_end = 12643

chosung_list = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ',
                'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

jungsung_list = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ',
                 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ',
                 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ',
                 'ㅡ', 'ㅢ', 'ㅣ']

jongsung_list = [
    ' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ',
    'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ',
    'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ',
    'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

jaum_list = ['ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄸ', 'ㄹ',
             'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ',
             'ㅃ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

moum_list = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ',
             'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']


def levenshtein(s1, s2, cost=None, debug=False):
    if len(s1) < len(s2):
        return levenshtein(s2, s1, debug=debug)

    if len(s2) == 0:
        return len(s1)

    if cost is None:
        cost = {}

    # changed
    def substitution_cost(c1, c2):
        if c1 == c2:
            return 0
        return cost.get((c1, c2), 1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            # Changed
            substitutions = previous_row[j] + substitution_cost(c1, c2)
            current_row.append(min(insertions, deletions, substitutions))

        if debug:
            print(current_row[1:])

        previous_row = current_row

    return previous_row[-1]


def compose(chosung, jungsung, jongsung):
    char = chr(
        kor_begin +
        chosung_base * chosung_list.index(chosung) +
        jungsung_base * jungsung_list.index(jungsung) +
        jongsung_list.index(jongsung)
    )
    return char


def decompose(c):
    if not character_is_korean(c):
        return None
    i = ord(c)
    if (jaum_begin <= i <= jaum_end):
        return (c, ' ', ' ')
    if (moum_begin <= i <= moum_end):
        return (' ', c, ' ')

    # decomposition rule
    i -= kor_begin
    cho = i // chosung_base
    jung = (i - cho * chosung_base) // jungsung_base
    jong = (i - cho * chosung_base - jung * jungsung_base)
    return (chosung_list[cho], jungsung_list[jung], jongsung_list[jong])


def character_is_korean(c):
    i = ord(c)
    return ((kor_begin <= i <= kor_end) or
            (jaum_begin <= i <= jaum_end) or
            (moum_begin <= i <= moum_end))


def jamo_levenshtein(s1, s2, debug=False):
    if len(s1) < len(s2):
        return jamo_levenshtein(s2, s1, debug)

    if len(s2) == 0:
        return len(s1)

    def substitution_cost(c1, c2):
        if c1 == c2:
            return 0
        return levenshtein(decompose(c1), decompose(c2)) / 3

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            # Changed
            substitutions = previous_row[j] + substitution_cost(c1, c2)
            current_row.append(min(insertions, deletions, substitutions))

        if debug:
            print(['%.3f' % v for v in current_row[1:]])

        previous_row = current_row

    return previous_row[-1]


## --------------------- 자모 유사도 분석 클래스 및 변수 끝 ------------------- ##

"""
1. 기본
2. 텍스트 자모 유사도 분석
3. DB
4. 눈 인식 쓰레드
5. 오디오 클래스
6. 오디오 루틴
7. 오디오 쓰레드
8. 윈도우 클래스
"""

## --------------------- DB 함수 및 변수 시작 ------------------- ##
# db 경로
db_path = resource_path(BASE_DIR + '/etridb.db')


# db_path = os.getenv('HOME') + '/etridb.db'


# 테이블 생성
def create_table():
    # db와 연결
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 테이블 생성
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id integer primary key autoincrement,
            order_number integer not null,
            menu text not null,
            amount integer not null,
            time timestamp default current_timestamp
        );
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS menus (
            menu text primary key,
            category text not null,
            price integer not null
        );
    """)

    # 테이블이 생성 되었는지 출력하여 확인
    c.execute('SELECT * FROM sqlite_master WHERE type="table" AND name="orders";')
    table_list = c.fetchall()
    for i in table_list:
        for j in i:
            print(j)
    c.execute('SELECT * FROM sqlite_master WHERE type="table" AND name="menus";')
    table_list = c.fetchall()
    for i in table_list:
        for j in i:
            print(j)

    # db와 연결 종료
    conn.close()


# DB에 메뉴 목록 insert
def insert_menus():
    # db와 연결
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # insert 쿼리
    INSERT_SQL = "INSERT INTO menus(menu, category, price) VALUES (?, ?, ?);"
    # 데이터 한 번에 여러개 추가
    data = (
        ("김치햄치즈볶음밥", "한식", 4500),
        ("소금덮밥", "한식", 4500),
        ("뼈다귀해장국", "한식", 4000),
        ("소고기미역국", "한식", 4000),
        ("냉면", "한식", 4000),
        ("간장불고기", "한식", 4500),
        ("제육볶음", "한식", 4500),
        ("짜장면", "중식", 2500),
        ("짬뽕", "중식", 2500),
        ("계란볶음밥", "중식", 3800),
        ("탕수육", "중식", 5000),
        ("군만두", "중식", 3000),
        ("떡볶이", "분식", 3000),
        ("라볶이", "분식", 3000),
        ("라면", "분식", 2500),
        ("순대", "분식", 3000),
        ("오므라이스", "분식", 3800),
        ("야채김밥", "분식", 2000),
        ("참치김밥", "분식", 2200),
        ("크림파스타", "양식", 3000),
        ("토마토파스타", "양식", 3000),
        ("알리오올리오", "양식", 3000),
        ("연어샐러드", "양식", 3000),
        ("감바스", "양식", 3000),
        ("왕돈까스", "일식", 4500),
        ("치킨까스", "일식", 4500),
        ("치즈돈까스", "일식", 4500),
        ("냉모밀", "일식", 2500),
        ("우동", "일식", 2500),
        ("김치나베", "일식", 3500),
        ("돈까스나베", "일식", 4000),
        ("물", "음료", 1000),
        ("콜라", "음료", 1000),
        ("사이다", "음료", 1000),
        ("환타", "음료", 1000),
        ("제로콜라", "음료", 1000),
        ("제로사이다", "음료", 1000)
    )
    c.executemany(INSERT_SQL, data)
    # 커밋 해야 실제로 db에 반영됨
    conn.commit()
    # 제대로 실행되었는지 출력하여 확인
    c.execute('SELECT * FROM menus;')
    item_list = c.fetchall()
    for i in item_list:
        print(i)

    # db와 연결 종료
    conn.close()


# DB에 주문 내역 insert
def insert_order(data):
    # db와 연결
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # insert 쿼리
    INSERT_SQL = "INSERT INTO orders(order_number, menu, amount) VALUES (?, ?, ?);"
    # 데이터 한 번에 여러개 추가
    c.executemany(INSERT_SQL, data)
    # 커밋 해야 실제로 db에 반영됨
    conn.commit()
    # 제대로 실행되었는지 출력하여 확인
    print("===== db =====")
    c.execute('SELECT * FROM orders;')
    item_list = c.fetchall()
    for i in item_list:
        print(i)

    # db와 연결 종료
    conn.close()


# DB에서 메뉴 정보 가져오기
def menu_info(category):
    # 메뉴 정보 저장할 변수
    menu_info = []
    # db와 연결
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # select 쿼리
    SELECT_SQL = 'SELECT menu FROM menus WHERE category = "%s";' % category

    # select로 가져오기
    c.execute(SELECT_SQL)
    menu_info = c.fetchall()

    # db와 연결 종료
    conn.close()
    return menu_info


# 테이블 삭제
def drop_table(table_name):
    # db와 연결
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 테이블이 이미 존재할 경우 삭제\
    # ex) orders  / menus
    c.execute(f"DROP TABLE IF EXISTS {table_name}")

    # db와 연결 종료
    conn.close()


# DB 삽입을 위한 데이터
def data_transform(order_number, order_list, order_count_list):
    data = []
    for i in range(len(order_list)):
        data.append((order_number, order_list[i], order_count_list[i]))
    return data


## --------------------- DB 함수 및 변수 시작 ------------------- ##

"""
1. 기본
2. 텍스트 자모 유사도 분석
3. DB
4. 눈 인식 쓰레드
5. 오디오 클래스
6. 오디오 루틴
7. 오디오 쓰레드
8. 윈도우 클래스
"""


## --------------------눈 검출 쓰레드 끝------------------------------ ##
# 눈 인식 쓰레드
class EyesThread(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.IMG_SIZE = (34, 26)
        self.power = True

    def run(self):
        self.power = True
        if self.eyes_detect():
            self.parent.audioButton.click()  # 오디오 안내 버튼 클릭 - 음성 안내 실행

    def stop(self):
        self.power = False
        self.wait(200)

    def crop_eye(self, gray, eye_points):
        x1, y1 = np.amin(eye_points, axis=0)
        x2, y2 = np.amax(eye_points, axis=0)
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

        w = (x2 - x1) * 1.2
        h = w * self.IMG_SIZE[1] / self.IMG_SIZE[0]

        margin_x, margin_y = w / 2, h / 2

        min_x, min_y = int(cx - margin_x), int(cy - margin_y)
        max_x, max_y = int(cx + margin_x), int(cy + margin_y)

        eye_rect = np.rint([min_x, min_y, max_x, max_y]).astype(np.int64)

        eye_img = gray[eye_rect[1]:eye_rect[3], eye_rect[0]:eye_rect[2]]

        return eye_img, eye_rect

    def eyes_detect(self):
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(resource_path(BASE_DIR + '/test_files/shape_predictor_68_face_landmarks.dat'))

        model = load_model(resource_path(BASE_DIR + '/test_files/2018_12_17_22_58_35.h5'))
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
            h, w, _ = img.shape
            img_matrix = cv2.getRotationMatrix2D((w / 2, h / 2), 270, 1)
            img_affine = cv2.warpAffine(img, img_matrix, (w, h))
            gray = cv2.cvtColor(img_affine, cv2.COLOR_BGR2GRAY)

            faces = detector(gray)

            for face in faces:
                shapes = predictor(gray, face)
                shapes = face_utils.shape_to_np(shapes)

                eye_img_l, eye_rect_l = self.crop_eye(gray, eye_points=shapes[36:42])
                eye_img_r, eye_rect_r = self.crop_eye(gray, eye_points=shapes[42:48])

                eye_img_l = cv2.resize(eye_img_l, dsize=self.IMG_SIZE)
                eye_img_r = cv2.resize(eye_img_r, dsize=self.IMG_SIZE)
                eye_img_r = cv2.flip(eye_img_r, flipCode=1)

                # cv2.imshow('l', eye_img_l)
                # cv2.imshow('r', eye_img_r)

                eye_input_l = eye_img_l.copy().reshape((1, self.IMG_SIZE[1], self.IMG_SIZE[0], 1)).astype(
                    np.float32) / 255.
                eye_input_r = eye_img_r.copy().reshape((1, self.IMG_SIZE[1], self.IMG_SIZE[0], 1)).astype(
                    np.float32) / 255.

                pred_l = model.predict(eye_input_l)
                pred_r = model.predict(eye_input_r)

                # visualize
                # state_l = 'O %.1f' if pred_l > 0.1 else '- %.1f'
                # state_r = 'O %.1f' if pred_r > 0.1 else '- %.1f'

                # state_l = state_l % pred_l
                # state_r = state_r % pred_r

                if pred_l < 0.2 and pred_r < 0.2:
                    # print("eyes--", count)
                    count += 1
                elif pred_l > 0.7 or pred_r > 0.7:
                    count = 0

            """
                cv2.rectangle(img, pt1=tuple(eye_rect_l[0:2]), pt2=tuple(eye_rect_l[2:4]), color=(255, 255, 255),
                              thickness=2)
                cv2.rectangle(img, pt1=tuple(eye_rect_r[0:2]), pt2=tuple(eye_rect_r[2:4]), color=(255, 255, 255),
                              thickness=2)

                cv2.putText(img, state_l, tuple(eye_rect_l[0:2]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(img, state_r, tuple(eye_rect_r[0:2]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow('result', img)
            if cv2.waitKey(1) == ord('q'):
                break
            """
            if not self.power:
                cap.release()
                break

            if count > 25:
                return True

        cap.release()

## --------------------눈 검출 클래스 끝------------------------------ ##

"""
1. 기본
2. 텍스트 자모 유사도 분석
3. DB
4. 눈 인식 쓰레드
5. 오디오 클래스
6. 오디오 루틴
7. 오디오 쓰레드
8. 윈도우 클래스
"""


## --------------------- 오디오 음성 인식 ----------------------- ##

# 오디오 음성 인식 클래스
class Audio:

    # 초기화
    def __init__(self):
        self.openApiURL_voice = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"  # 음성 인식 URL
        # openApiURL = "http://aiopen.etri.re.kr:8000/WiseNLU"  # 문어
        self.openApiURL_word = "http://aiopen.etri.re.kr:8000/WiseNLU_spoken"  # 구어 단어 인식 URL
        self.accessKey = "e1d17392-08c5-4578-b194-a1cb212d4f83"
        # audioFilePath = "AUDIO_FILE_PATH"
        self.languageCode = "korean"
        self.analysisCode = "morp"
        self.r = sr.Recognizer()  # 음석 인식 객체
        self.http = urllib3.PoolManager()  # http 객체

    # 음성 오타 수정
    @staticmethod
    def text_correction(text):
        collect_text = spell_checker.check(text)

        return collect_text.as_dict()['checked']

    # 단어 추출
    def detect_word(self, text):

        word_request_json = {
            "access_key": self.accessKey,
            "argument": {
                "text": text,
                "analysis_code": self.analysisCode
            }
        }

        response = self.http.request(
            "POST",
            self.openApiURL_word,
            headers={"Content-Type": "application/json; charset=UTF-8"},
            body=json.dumps(word_request_json)
        )

        print("[responseCode] " + str(response.status))
        print("[responseBody]")
        print(str(response.data, "utf-8"))

        json_obj = json.loads(str(response.data, "utf-8"))

        obj_morp = json_obj["return_object"]["sentence"][0]["morp"]

        print(obj_morp)

        nn_list = []
        for nn in obj_morp:
            print(nn["type"])
            if nn["type"] == 'NNG':
                nn_list.append(nn['lemma'])
                print(nn['lemma'])
            elif nn["type"] == 'NNP':
                nn_list.append(nn['lemma'])
                print(nn['lemma'])
            elif nn["type"] == 'NNB':
                nn_list.append(nn['lemma'])
                print(nn['lemma'])
            elif nn["type"] == 'IC':
                nn_list.append(nn['lemma'])
                print(nn['lemma'])
            else:
                print("no")

        return nn_list

    # 음성 듣기
    def listen(self):
        with sr.Microphone() as source:
            print("Say something!")
            audio = self.r.listen(source, phrase_time_limit=5)

            text = self.r.recognize_google(audio, language='ko')
            print("audio__ ", text)
            return text

    """
            audio_contents = base64.b64encode(audio.get_wav_data()).decode("utf8")

            voice_request_json = {
                "access_key": self.accessKey,
                "argument": {
                    "language_code": self.languageCode,
                    "audio": audio_contents
                }
            }

            response = self.http.request(
                "POST",
                self.openApiURL_voice,
                headers={"Content-Type": "application/json; charset=UTF-8"},
                body=json.dumps(voice_request_json)
            )

            print("[responseCode] " + str(response.status))
            print("[responseBody]")
            print(str(response.data, "utf-8"))

            json_obj = json.loads(str(response.data, "utf-8"))

            return json_obj["return_object"]['recognized']

    """

menu = {
    'korean': ['김치햄치즈볶음밥', '소금덮밥', '뼈다귀해장국', '소고기미역국', '냉면', '간장불고기', '제육볶음'],
    'chinese': ['짜장면', '짬뽕', '계란볶음밥', '탕수육', '군만두'],
    'schoolfood': ['떡볶이', '라볶이', '라면', '순대', '오므라이스', '야채김밥', '참치김밥'],
    'Westernfood': ['크림파스타', '토마토파스타', '알리오올리오', '연어샐러드', '감바스'],
    'japanesefood': ['왕돈까스', '치킨까스', '치즈돈까스', '냉모밀', '우동', '김치나베', '돈까스나베'],
    'beverage': ['물', '콜라', '사이다', '환타', '제로콜라', '제로사이다']
}

menu_keyword = {
    '김치햄치즈볶음밥': ['김치', '햄', '치즈', '볶음밥'],
    '소금덮밥': ['소금', '덮밥'],
    '뼈다귀해장국': ['뼈다귀', '해장국', '해장'],
    '소고기미역국': ['소고기', '미역', '미역국'],
    '냉면': ['냉', '면', '냉면'],
    '간장불고기': ['간장', '불', '불고기'],
    '제육볶음': ['제육', '볶음'],
    '짜장면': ['짜장', '자장', '자장가', '짜장면', '자장면', '면'],
    '짬뽕': ['짬', '짬뽕', '뽕'],
    '계란볶음밥': ['계란', '볶음', '볶음밥'],
    '탕수육': ['탕', '탕수육', '수육'],
    '군만두': ['군', '만두', '군만두'],
    '떡볶이': ['떡', '떡볶이'],
    '라볶이': ['라볶이'],
    '라면': ['라', '라면'],
    '순대': ['순대', '순', '대'],
    '오므라이스': ['오므라이스', '라이스'],
    '야채김밥': ['야채', '김밥', '야채김밥'],
    '참치김밥': ['참치', '참치김밥'],
    '크림파스타': ['크림', '그림'],
    '토마토파스타': ['토마토', '파스타'],
    '알리오올리오': ['알리오', '올리오', '올리'],
    '연어샐러드': ['연어', '샐러드'],
    '감바스': ['감바스', '감'],
    '왕돈까스': ['왕', '돈까스'],
    '치킨까스': ['치킨'],
    '치즈돈까스': ['치즈'],
    '냉모밀': ['냉', '모밀'],
    '우동': ['우동', '우', '동'],
    '김치나베': ['김치', '김치나베', '나베'],
    '돈까스나베': ['돈가스나베', '돈까스나베'],
    '물': ['물'],
    '콜라': ['콜라', '콜'],
    '사이다': ['사이다', '사이', '다'],
    '환타': ['환타'],
    '제로콜라': ['제로콜라', '제로'],
    '제로사이다': ['제로사이다']
}

answer_list = ['아니', '아니오', '아니요', '네', '내', '넵', '냅', '넹', '냉', '웅', '응', '그래', '그레', '구래', '고래', '좋아', '음성']
cancel_list = ['취소', '다시', '취수', '홈', '처음', '캔슬', '취사']
first_list = ['한식', '중식', '분식', '양식', '일식', '음료']
second_list = menu
third_list = ['결제', '결재', '끝', '그만', '주문', '추가', '메뉴', '음식', '삭제']


# 음성 인식 함수
def audio_routine(step, menu_name=None, order_list=None):
    audio = Audio()
    text = audio.listen()
    text_correct = audio.text_correction(text)
    text_word_list = audio.detect_word(text_correct)

    # 음성 안내 확인 단계
    if step == 0:
        # 취소 확인
        for _, t in enumerate(cancel_list):
            if t in text_word_list:
                return -1

        # 1단계
        for i, t in enumerate(answer_list):
            if t in text_word_list:
                return i

    # 메뉴 선정 단계
    elif step == 1:
        # 취소 확인
        for _, t in enumerate(cancel_list):
            if t in text_word_list:
                return -1

        # 2단계
        for i, t in enumerate(first_list):
            if t in text_word_list:
                return i

        # 텍스트 유사도 분석
        similarity_num = compare_text(text_word_list, first_list)
        if similarity_num != -1:
            return similarity_num
        else:
            return -1

    # 음식 선정 단계
    elif step == 2:
        # 취소 확인
        for _, t in enumerate(cancel_list):
            if t in text_word_list:
                return -1

        # 3단계
        if menu_name is not None:
            for i, food in enumerate(second_list[menu_name]):
                for keyword in menu_keyword[food]:
                    # 키워드 비교
                    if keyword in text_word_list:
                        return i

                # 텍스트 유사도 분석
                similarity_num = compare_text(text_word_list, menu_keyword[food])
                if similarity_num != -1:
                    return i
                else:
                    return -1

        else:
            for key, value in second_list.items():
                for i, food in enumerate(value):
                    for keyword in menu_keyword[food]:
                        if keyword in text_word_list:
                            return i, key

    # 추가 주문 및 결제 선택 단계
    elif step == 3:
        # 취소 확인
        for _, t in enumerate(cancel_list):
            if t in text_word_list:
                return -1

        # 4단계
        for i, t in enumerate(third_list):
            if t in text_word_list:
                return i

        # 텍스트 유사도 분석
        similarity_num = compare_text(text_word_list, third_list)
        if similarity_num != -1:
            return similarity_num
        else:
            return -1

    # 삭제할 음식 선택 단계
    elif step == 4:
        if order_list is not None:
            for index, order in enumerate(order_list):
                for keyword in menu_keyword[order]:
                    # 키워드 비교
                    if keyword in text_word_list:
                        return index

                # 텍스트 유사도 분석
                similarity_num = compare_text(text_word_list, menu_keyword[order])
                if similarity_num != -1:
                    return index
                else:
                    return -1

    return -1


# pip install playsound

## ------------------ 오디오 쓰레드 ---------------- ##

class AudioThread(QThread):
    def __init__(self, parent, menu):
        super().__init__(parent)
        self.parent = parent
        self.menu = menu
        self.menu_list = ['korean', 'chinese', 'schoolfood', 'Westernfood', 'japanesefood', 'beverage']

    def run(self):
        state = False
        self.parent.button_set_enabled(False)
        if self.step1() == 0:  # 음성 안내
            while True:
                n = self.step2()
                if n != -1:  # 메뉴 선택
                    if self.step3(n) == 0:  # 음식 선택
                        step4_loop = False
                        while True:
                            again_or_pay = self.step4()  # 추가 주문 or 결제
                            if again_or_pay == 1:
                                step4_loop = True
                                break  # 추가 주문
                            elif again_or_pay == 0:
                                state = True
                                self.step5_final()  # 결제
                                break
                            elif again_or_pay == 2:  # 삭제
                                continue
                            else:
                                break
                        if step4_loop:
                            continue  # 추가 주문
                        else:
                            break
                    else:
                        break
                else:
                    break
        else:
            self.parent.eyes_routine()

        if not state:
            # audio 루틴이 끝나면 실행
            self.parent.homeButton.click()

        self.parent.button_set_enabled(True)
        self.quit()

    def step1(self):
        count = 0
        while count < 3:
            playsound.playsound(resource_path(BASE_DIR + "/test_files/play1.mp3"))
            print("음성으로 안내받길 원하시나요?")
            n = audio_routine(0)
            if n < 3:  # 대답이 부정 혹은 오류 일때
                if count < 1:  # 2번만 확인
                    playsound.playsound(resource_path(BASE_DIR + "/test_files/again.mp3"))
                    count += 1
                else:
                    return -1
            else:
                self.parent.stackedWidget.setCurrentIndex(1)
                return 0

    def step2(self):
        count = 0
        while count < 2:
            playsound.playsound(resource_path(BASE_DIR + "/test_files/play2.mp3"))

            print("어떤 메뉴를 원하시나요? 한식, 중식, 분식, 양식, 일식, 음료")
            n = audio_routine(1)
            if n == -1:
                if count < 1:  # 2번만 확인
                    playsound.playsound(resource_path(BASE_DIR + "/test_files/again.mp3"))
                    count += 1
                else:
                    return -1
            else:
                self.parent.menuStackedWidget.setCurrentIndex(n)
                return n

    def step3(self, m):
        count = 0
        while count < 2:
            print("해당 메뉴의 종류는 여러 음식이 있습니다. 원하시는 메뉴를 말해주세요. ")
            if m == 0:
                playsound.playsound(resource_path(BASE_DIR + "/test_files/menu1.mp3"))
            elif m == 1:
                playsound.playsound(resource_path(BASE_DIR + "/test_files/menu2.mp3"))
            elif m == 2:
                playsound.playsound(resource_path(BASE_DIR + "/test_files/menu3.mp3"))
            elif m == 3:
                playsound.playsound(resource_path(BASE_DIR + "/test_files/menu4.mp3"))
            elif m == 4:
                playsound.playsound(resource_path(BASE_DIR + "/test_files/menu5.mp3"))
            elif m == 5:
                playsound.playsound(resource_path(BASE_DIR + "/test_files/menu6.mp3"))
            else:
                playsound.playsound(resource_path(BASE_DIR + "/test_files/error.mp3"))
                return -1

            key = self.menu_list[m]
            n = audio_routine(2, menu_name=key)
            if n == -1:
                if count < 1:  # 2번만 확인
                    playsound.playsound(resource_path(BASE_DIR + "/test_files/again.mp3"))
                    count += 1
                else:
                    return -1
            else:
                if key == self.menu_list[0]:
                    self.parent.cell_clicked_event1(0, n)
                elif key == self.menu_list[1]:
                    self.parent.cell_clicked_event2(0, n)
                elif key == self.menu_list[2]:
                    self.parent.cell_clicked_event3(0, n)
                elif key == self.menu_list[3]:
                    self.parent.cell_clicked_event4(0, n)
                elif key == self.menu_list[4]:
                    self.parent.cell_clicked_event5(0, n)
                elif key == self.menu_list[5]:
                    self.parent.cell_clicked_event6(0, n)

                print("선택 완료")
                playsound.playsound(resource_path(BASE_DIR + "/test_files/choice_complete.mp3"))
                return 0

    def step4(self):
        count = 0
        while count < 2:
            playsound.playsound(resource_path(BASE_DIR + "/test_files/play4.mp3"))
            print("추가 주문이나 삭제를 원하십니까? 아니면 결제하시겠습니까?")
            n = audio_routine(3)
            if n == -1:
                if count < 1:  # 2번만 확인
                    playsound.playsound(resource_path(BASE_DIR + "/test_files/again.mp3"))
                    count += 1
                else:
                    return -1
            elif n < 4:
                return 0  # 결제
            elif n >= 8:  # 삭제
                tts_text = "주문 목록은 "
                for order in self.parent.order_list:
                    tts_text += (order + ", ")
                tts_text += "입니다. 어떤 메뉴를 삭제하시겠습니까?"
                make_tts(tts_text)
                # tts 재생
                playsound.playsound(resource_path(BASE_DIR + "/test_files/order_list.mp3"))
                # 삭제할 음식 이름 음성 받기
                success_delete_num = audio_routine(4, order_list=self.parent.order_list)
                if success_delete_num != -1:
                    self.parent.select_list_item = success_delete_num
                    self.parent.list_item_delete_event()
                    print("삭제 성공")
                    playsound.playsound(resource_path(BASE_DIR + "/delete_success.mp3"))
                else:
                    playsound.playsound(resource_path(BASE_DIR + "/test_files/delete_fail.mp3"))
                    print("삭제 실패")

                return 2

            else:
                return 1  # 추가 주문

    def step5_final(self):
        print("허리 부근 중앙 오른쪽에 카드 리더기가 있습니다.")
        print("결제 완료")
        self.parent.pay_button_clicked_event()


## ------------------ 오디오 쓰레드 끝 ----------------------------- ##

"""
1. 기본
2. 텍스트 자모 유사도 분석
3. DB
4. 눈 인식 쓰레드
5. 오디오 클래스
6. 오디오 루틴
7. 오디오 쓰레드
8. 윈도우 클래스
"""


## ------------------- Window Class 시작 ------------------------------ ##
# 화면을 구성하는 Class 선언
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.n = 0
        self.setupUi(self)
        self.audio_thread = AudioThread(self, menu)
        self.eyes_thread = EyesThread(self)
        self.step = 0
        self.order_number = 0
        self.amount = 0
        self.order_list = []
        self.order_count_list = []
        self.select_list_item = -1

        self.start.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.setStyleSheet("background-color: rgb(255, 255, 255);")
        font = self.menuStackedWidget.font()
        font.setPointSize(20)
        self.menuStackedWidget.setStyleSheet('font-size:20px;')

        # 매장 이용 버튼 설정
        stay_pixmap = QPixmap(resource_path(BASE_DIR + '/test_files/stay.png'))  # QPixmap 생성
        stay_pixmap = stay_pixmap.scaled(300, 300, Qt.IgnoreAspectRatio)  # 이미지 크기 변경
        stay_icon = QIcon()  # QIcon 생성
        stay_icon.addPixmap(stay_pixmap)  # 아이콘에 이미지 설정

        self.stay2Button.setIcon(stay_icon)  # Pushbutton에 아이콘 설정
        self.stay2Button.clicked.connect(self.stayButtonFunction)

        # 테이그아웃 버튼 설정
        takeout_pixmap = QPixmap(resource_path(BASE_DIR + '/test_files/pickup.png'))  # QPixmap 생성
        takeout_pixmap = takeout_pixmap.scaled(300, 300, Qt.IgnoreAspectRatio)  # 이미지 크기 변경

        takeout_icon = QIcon()  # QIcon 생성
        takeout_icon.addPixmap(takeout_pixmap)  # 아이콘에 이미지 설정

        self.takeout2Button.setIcon(takeout_icon)  # Pushbutton에 아이콘 설정
        self.takeout2Button.clicked.connect(self.takeOutButtonFunction)

        # 버튼에 기능을 연결하는 코드
        # 첫 화면에 있는 버튼
        self.stayButton.clicked.connect(self.stayButtonFunction)
        self.takeOutButton.clicked.connect(self.takeOutButtonFunction)
        self.audioButton.clicked.connect(self.audioButtonFunction)
        self.homeButton.clicked.connect(self.homeButtonFunction)

        # 메뉴 버튼 클릭 이벤트
        self.menuButton_1.clicked.connect(self.menu1ButtonFunction)
        self.menuButton_2.clicked.connect(self.menu2ButtonFunction)
        self.menuButton_3.clicked.connect(self.menu3ButtonFunction)
        self.menuButton_4.clicked.connect(self.menu4ButtonFunction)
        self.menuButton_5.clicked.connect(self.menu5ButtonFunction)
        self.menuButton_6.clicked.connect(self.menu6ButtonFunction)

        # 메뉴 테이블 위젯 리스트
        self.tf_list = [self.tableWidget_1, self.tableWidget_2, self.tableWidget_3, self.tableWidget_4,
                        self.tableWidget_5, self.tableWidget_6]
        # 테이블에 메뉴 세팅
        for k, v in menu.items():
            table_index = table_idx_lookup[k]
            font = self.tf_list[table_index].font()
            font.setPointSize(20)
            self.tf_list[table_index].setStyleSheet(
                "selection-color: rgb(58, 134, 255); selection-background-color: white;")
            self.set_menuTableWidgetData(self.tf_list[table_index], v)

        # 메뉴 테이블 셀 클릭 이벤트
        self.tableWidget_1.cellClicked.connect(self.cell_clicked_event1)
        self.tableWidget_2.cellClicked.connect(self.cell_clicked_event2)
        self.tableWidget_3.cellClicked.connect(self.cell_clicked_event3)
        self.tableWidget_4.cellClicked.connect(self.cell_clicked_event4)
        self.tableWidget_5.cellClicked.connect(self.cell_clicked_event5)
        self.tableWidget_6.cellClicked.connect(self.cell_clicked_event6)

        # pay(결제) 창 이벤트
        self.selectMenuList.itemClicked.connect(self.list_item_selected_event)
        self.selectMenuCountList.itemClicked.connect(self.list_item_selected_event)
        self.deleteMenuButton.clicked.connect(self.list_item_delete_event)
        self.payButton.clicked.connect(self.pay_button_clicked_event)
        self.addCountButton.clicked.connect(self.item_count_add_event)
        self.deleteCountButton.clicked.connect(self.item_count_minus_event)

        # 처음 화면 세팅
        self.stackedWidget.setCurrentIndex(0)
        self.menuStackedWidget.setCurrentIndex(0)
        self.homeButton.setEnabled(False)
        self.eyes_routine()

    # ------- init -------#

    # 메인 화면 버튼 활성화 함수
    def button_set_enabled(self, bool_button):
        self.stayButton.setEnabled(bool_button)
        self.takeOutButton.setEnabled(bool_button)
        self.audioButton.setEnabled(bool_button)

    # ------ 메뉴 셀 클릭 이벤트 함수들 ------ #

    def cell_clicked_event1(self, row, col):
        index = row * 5 + col
        column = menu_list[0]
        if index < len(menu[column]):
            data = menu[column][index]
            self.check_same_menu(data)
            self.calculation_money()

    def cell_clicked_event2(self, row, col):
        index = row * 5 + col
        column = menu_list[1]
        if index < len(menu[column]):
            data = menu[column][index]
            self.check_same_menu(data)
            self.calculation_money()

    def cell_clicked_event3(self, row, col):
        index = row * 5 + col
        column = menu_list[2]
        if index < len(menu[column]):
            data = menu[column][index]
            self.check_same_menu(data)
            self.calculation_money()

    def cell_clicked_event4(self, row, col):
        index = row * 5 + col
        column = menu_list[3]
        if index < len(menu[column]):
            data = menu[column][index]
            self.check_same_menu(data)
            self.calculation_money()

    def cell_clicked_event5(self, row, col):
        index = row * 5 + col
        column = menu_list[4]
        if index < len(menu[column]):
            data = menu[column][index]
            self.check_same_menu(data)
            self.calculation_money()

    def cell_clicked_event6(self, row, col):
        index = row * 5 + col
        column = menu_list[5]
        if index < len(menu[column]):
            data = menu[column][index]
            self.check_same_menu(data)
            self.calculation_money()

    # 아이템 개수 추가 이벤트
    def item_count_add_event(self):
        if self.select_list_item >= 0:
            self.order_count_list[self.select_list_item] += 1
            self.selectMenuCountList.takeItem(self.select_list_item)
            item = QListWidgetItem(str(self.order_count_list[self.select_list_item]))
            item.setSizeHint(QSize(50, 50))
            item.setTextAlignment(4)
            self.selectMenuCountList.insertItem(self.select_list_item, item)
            self.calculation_money()

    # 아이템 개수 빼기 이벤트
    def item_count_minus_event(self):
        if self.select_list_item >= 0:
            if self.order_count_list[self.select_list_item] == 1:
                self.selectMenuCountList.takeItem(self.select_list_item)
                self.selectMenuList.takeItem(self.select_list_item)
            else:
                self.order_count_list[self.select_list_item] -= 1
                self.selectMenuCountList.takeItem(self.select_list_item)
                item = QListWidgetItem(str(self.order_count_list[self.select_list_item]))
                item.setSizeHint(QSize(50, 50))
                item.setTextAlignment(4)
                self.selectMenuCountList.insertItem(self.select_list_item, item)

        self.calculation_money()

    def add_list_item(self, data):
        item = QListWidgetItem(data)
        item.setSizeHint(QSize(300, 50))
        item.setTextAlignment(4)
        self.selectMenuList.addItem(item)

    def add_list_item_count(self, data):
        item = QListWidgetItem(data)
        item.setSizeHint(QSize(50, 50))
        item.setTextAlignment(4)
        self.selectMenuCountList.addItem(item)

    # 같은 음식을 눌렀을 때 중복인지 체크하는 함수
    def check_same_menu(self, data):
        same = False
        index = -1
        for i, d in enumerate(self.order_list):
            if data == d:
                same = True
                index = i

        if not same:
            self.order_list.append(data)
            self.order_count_list.append(1)
            self.add_list_item(data)
            self.add_list_item_count(str(1))
        else:
            self.order_count_list[index] += 1
            self.selectMenuCountList.takeItem(index)
            item = QListWidgetItem(str(self.order_count_list[index]))
            item.setSizeHint(QSize(50, 50))
            item.setTextAlignment(4)
            self.selectMenuCountList.insertItem(index, item)

    # ------ 메뉴 셀 클릭 이벤트 함수들 end ------ #

    # ---- pay(결제) 창 관련 함수들 ---- #
    def list_item_selected_event(self):
        select_item_row = self.selectMenuList.currentRow()
        self.select_list_item = select_item_row
        print(select_item_row)

    def list_item_delete_event(self):
        if self.select_list_item != -1:
            self.order_list.pop(self.select_list_item)
            self.order_count_list.pop(self.select_list_item)
            self.selectMenuList.takeItem(self.select_list_item)
            self.selectMenuCountList.takeItem(self.select_list_item)
            self.select_list_item = -1
            self.calculation_money()

    def pay_button_clicked_event(self):
        # db에 주문 내역 저장
        insert_order(data_transform(self.order_number, self.order_list, self.order_count_list))
        self.order_number += 1
        self.stackedWidget.setCurrentIndex(2)
        reset()
        self.homeButtonFunction()

    def calculation_money(self):
        self.amount = 0
        for index, order in enumerate(self.order_list):
            for menu_cal in menu_price.keys():
                if order in menu_price[menu_cal]:
                    print(index, order)
                    self.amount += menu_price[menu_cal][order] * self.order_count_list[index]
                    self.money_label.setText(str(self.amount))

    # ---- pay(결제) 창 관련 함수들 end ---- #

    # homeButton 이 눌리면 작동할 함수
    def homeButtonFunction(self):
        self.stackedWidget.setCurrentIndex(0)
        self.menuStackedWidget.setCurrentIndex(0)
        self.homeButton.setEnabled(False)
        self.order_list.clear()
        self.order_count_list.clear()
        self.selectMenuList.clear()
        self.selectMenuCountList.clear()
        self.select_list_item = -1
        self.amount = 0
        self.tableWidget_1.clearSelection()
        self.tableWidget_2.clearSelection()
        self.tableWidget_3.clearSelection()
        self.tableWidget_4.clearSelection()
        self.tableWidget_5.clearSelection()
        self.tableWidget_6.clearSelection()
        self.eyes_routine()

    # stayButton 이 눌리면 작동할 함수
    def stayButtonFunction(self):
        self.eyes_thread.stop()
        self.stackedWidget.setCurrentIndex(1)
        self.homeButton.setEnabled(True)

    # takeOutButton 이 눌리면 작동할 함수
    def takeOutButtonFunction(self):
        self.eyes_thread.stop()
        self.stackedWidget.setCurrentIndex(1)
        self.homeButton.setEnabled(True)

    # audioButton 이 눌리면 작동할 함수
    def audioButtonFunction(self):
        # 음성 인식
        self.eyes_thread.stop()
        self.audio_routine()

    # 한식 버튼 함수
    def menu1ButtonFunction(self):
        self.menuStackedWidget.setCurrentIndex(0)

    # 중식 버튼 함수
    def menu2ButtonFunction(self):
        self.menuStackedWidget.setCurrentIndex(1)

    # 분식 버튼 함수
    def menu3ButtonFunction(self):
        self.menuStackedWidget.setCurrentIndex(2)

    # 양식 버튼 함수
    def menu4ButtonFunction(self):
        self.menuStackedWidget.setCurrentIndex(3)

    # 일식 버튼 함수
    def menu5ButtonFunction(self):
        self.menuStackedWidget.setCurrentIndex(4)

    # 음료 버튼 함수
    def menu6ButtonFunction(self):
        self.menuStackedWidget.setCurrentIndex(5)

    # 눈 인식 쓰레드 함수
    def eyes_routine(self):
        self.eyes_thread.start()

    # 오디오 인식 쓰레드 함수
    def audio_routine(self):
        self.audio_thread.start()

    # 각 메뉴의 테이블 아이템 정의하는 함수
    def set_menuTableWidgetData(self, table_widget, value_list):
        count = 0
        row = 0

        # 테이블에 넣을 커스텀 위젯 클래스 - 이미지와 텍스트 함께 존재
        for col, val in enumerate(value_list):
            cell_widget = QWidget(self)
            font = cell_widget.font()
            font.setPointSize(20)
            cell_widget.setLayout(QVBoxLayout())
            cell_pixmap_label = QLabel(self)
            cell_text_label = QLabel(self)
            pixmap = QPixmap(resource_path(BASE_DIR + f'/test_files/{val}.png'))  # QPixmap 생성
            pixmap = pixmap.scaled(192, 256, Qt.KeepAspectRatio)  # 이미지 크기 변경
            cell_pixmap_label.setPixmap(pixmap)
            cell_text_label.setAlignment(Qt.AlignCenter)
            cell_text_label.setText(val)
            cell_text_label.setStyleSheet('font-size:20px;')

            cell_widget.layout().addWidget(cell_pixmap_label)
            cell_widget.layout().addWidget(cell_text_label)

            if col > 4 and row == 0:
                row = 1
                count = 0
            elif col > 9 and row == 1:
                row = 2
                count = 0
            elif col > 14 and row == 2:
                row = 3
                count = 0
            table_widget.setCellWidget(row, count, cell_widget)
            count += 1


## -------------------------Window Class 끝------------------------ ##

# Qt Gui 화면 Window 실행 함수
def window_start():
    app = QApplication(sys.argv)
    fontDB = QFontDatabase()
    fontDB.addApplicationFont(resource_path('test_files/NanumGothic.ttf'))
    app.setFont(QFont('NanumGothic'))
    ex = WindowClass()

    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    # db
    drop_table("menus")  # menus 테이블이 존재할 경우 삭제
    create_table()  # orders 와 menus 테이블 생성 but 이미 존재할 시 생성 안함
    insert_menus()  # 메뉴판 정보 저장

    # qt
    window_start()  # qt 시작
