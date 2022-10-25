import os
import sys
import threading
from PyQt5 import uic, Qt
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
import time
from multiprocessing import Process
from Audio.audio import Audio
import playsound
from Camera.video_eyes_detection import eyes_detect


# UI파일 연결
# 단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


lock = threading.Lock()

form = resource_path('static/main.ui')
form_class = uic.loadUiType(form)[0]

menu = {
    'korean': ['김치볶음밥', '김치치즈볶음밥', '소금덮밥', '제육덮밥', '뼈다귀해장국', '소고기미역국', '냉면', '간장불고기'],
    'bacban': ['제육정식', '간장불고기정식', '고등어정식'],
    'schoolfood': ['떡볶이', '라볶이', '라면', '기본김밥', '야채김밥', '참치김밥', '순대'],
    'Westernfood': ['크림파스타', '토마토파스타', '알리오올리오', '연어샐러드', '감바스'],
    'japanesefood': ['오므라이스', '왕돈까스', '치킨까스', '치즈돈까스', '냉모밀', '우동', '김치나베', '돈까스나베'],
    'beverage': ['물', '콜라', '사이다', '환타', '제로콜라', '제로사이다']
}
table_idx_lookup = {'korean': 0, 'bacban': 1, 'schoolfood': 2, 'Westernfood': 3, 'japanesefood': 4, 'beverage': 5}
menu_list = ['korean', 'bacban', 'schoolfood', 'Westernfood', 'japanesefood', 'beverage']

answer_list = ['아니', '아니오', '아니요', '네', '내', '넵', '냅', '넹', '냉', '넨', '낸', '웅', '응', '그래', '그레', '구래', '구레', '고래', '고레']
first_list = ['한식', '백반', '분식', '양식', '일식', '음료']
second_list = []


# 음성 인식 함수
def audio_routine(step):
    audio = Audio()
    text = audio.listen()
    text_correct = audio.text_correction(text)
    text_word_list = audio.detect_word(text_correct)

    # 음성 안내 확인 단계
    if step == 0:
        for i, t in enumerate(answer_list):
            print("i  - ", i, "// t -- ", t)
            if t in text_word_list:
                return i

    # 메뉴 선정 단계
    elif step == 1:
        for i, t in enumerate(first_list):
            if t in text_word_list:
                return i

    return -1


class Thread1(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def run(self):
        self.parent.stackedWidget.setCurrentIndex(2)


# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.n = 0
        self.setupUi(self)
        self.step = 0
        # 색 지정
        # self.centralwidget.setStyleSheet("background-color: white")
        # self.stackedWidget.setStyleSheet("background-color: white")
        self.title.setStyleSheet("Color : black")

        # 버튼에 기능을 연결하는 코드
        # 첫 화면에 있는 버튼
        self.stayButton.clicked.connect(self.stayButtonFunction)
        self.takeOutButton.clicked.connect(self.takeOutButtonFunction)
        self.audioButton.clicked.connect(self.audioButtonFunction)
        self.homeButton.clicked.connect(self.homeButtonFunction)

        # 메인 메뉴 화면에 있는 버튼
        self.menuButton_1.clicked.connect(self.menu1ButtonFunction)
        self.menuButton_2.clicked.connect(self.menu2ButtonFunction)
        self.menuButton_3.clicked.connect(self.menu3ButtonFunction)
        self.menuButton_4.clicked.connect(self.menu4ButtonFunction)
        self.menuButton_5.clicked.connect(self.menu5ButtonFunction)
        self.menuButton_6.clicked.connect(self.menu6ButtonFunction)

        # 메뉴 테이블 위젯 리스트
        self.tf_list = [self.tableWidget_1, self.tableWidget_2, self.tableWidget_3, self.tableWidget_4,
                        self.tableWidget_5, self.tableWidget_6]
        self.tf_list2 = [self.tableWidget_7, self.tableWidget_8, self.tableWidget_9, self.tableWidget_10,
                         self.tableWidget_11, self.tableWidget_12]

        # 테이블에 메뉴 세팅
        for k, v in menu.items():
            til = table_idx_lookup[k]
            self.set_menuTableWidgetData(self.tf_list[til], v)

        for k, v in menu.items():
            til = table_idx_lookup[k]
            self.set_menuTableWidgetData(self.tf_list2[til], v)

        # 처음 화면 세팅
        self.stackedWidget.setCurrentIndex(0)
        self.menuStackedWidget.setCurrentIndex(0)
        self.menuStackedWidget_Audio.setCurrentIndex(0)

        # self.stackedWidget.currentChanged.connect(self.changePage)

    # homeButton 이 눌리면 작동할 함수
    def homeButtonFunction(self):
        self.stackedWidget.setCurrentIndex(0)

    # stayButton 이 눌리면 작동할 함수
    def stayButtonFunction(self):
        self.stackedWidget.setCurrentIndex(1)

    # takeOutButton 이 눌리면 작동할 함수
    def takeOutButtonFunction(self):
        self.stackedWidget.setCurrentIndex(1)

    def play1(self):
        with lock:
            playsound.playsound('play1.mp3')

    def play2(self):
        with lock:
            playsound.playsound('play2.mp3')

    def audio1(self):
        self.n = audio_routine(0)

    def changead(self):
        print("음성안내 숫자 ", self.n)
        if self.n < 3:
            self.stackedWidget.setCurrentIndex(1)
        else:
            self.stackedWidget.setCurrentIndex(2)

    def change_index(self):
        self.stackedWidget.setCurrentIndex(2)

    # audioButton 이 눌리면 작동할 함수
    def audioButtonFunction(self):
        self.n = audio_routine(0)
        self.stackedWidget.setCurrentIndex(2)
        """
        th1 = threading.Thread(target=self.change_index)
        th1.start()

        # 음성 인식 루틴
        th2 = threading.Thread(target=self.play1)
        th2.start()
        th2.join()
        print("음성으로 안내받길 원하시나요?")
        th3 = threading.Thread(target=self.audio1)
        th3.start()
        th3.join()

        th4 = threading.Thread(target=self.changead)
        th4.start()
        th4.join()

        th5 = threading.Thread(target=self.play2)
        th5.start()
        th5.join()
        print("어떤 메뉴를 원하시나요? 한식, 백반, 분식, 양식, 일식, 음료")
        th6 = threading.Thread(target=self.audio1)
        th6.start()
        th6.join()
        n = audio_routine(1)
        if n == -1:
            self.stackedWidget.setCurrentIndex(1)
        else:
            self.StackedWidget.setCurrentIndex(n)
        """
    # 한식 버튼 함수
    def menu1ButtonFunction(self):
        self.menuStackedWidget.setCurrentIndex(0)

    # 백반 버튼 함수
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

    # 각 메뉴의 테이블 아이템 정의하는 함수
    def set_menuTableWidgetData(self, tf, v):
        n = 0
        r = 0
        for col, val in enumerate(v):
            item = QTableWidgetItem(val)
            item.setTextAlignment(4)

            if col > 9 and r == 1:
                r = 2
                n = 0
            elif col > 5 and r == 0:
                r = 1
                n = 0
            tf.setItem(r, n, item)
            n += 1


def window_start():
    app = QApplication(sys.argv)
    ex = WindowClass()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":

    p2 = Process(target=eyes_detect)
    p2.start()
    p2.join()

