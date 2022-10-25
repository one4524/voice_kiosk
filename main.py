import os
import sys
from PyQt5 import uic
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
import time
import playsound

from Audio.audio_routine import audio_routine
from Camera.video_eyes_detection import eyes_detect


# UI파일 연결
# 단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


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


# 눈 인식 쓰레드
class EyesThread(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def run(self):
        eyes_detect()
        time.sleep(0.3)
        self.parent.audioButton.click()


# 오디오 쓰레드
class AudioThread(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.step_state = 0
        self.menu = menu

    def run(self):
        if self.step1() == 0:  # 음성 안내
            self.step_state = 1
            while True:
                n = self.step2()
                if n != -1:  # 메뉴 선택
                    self.step_state = 2
                    if self.step3(n) == 0:  # 음식 선택
                        self.step_state = 3
                        again_or_pay = self.step4()  # 추가 주문 or 결제
                        if again_or_pay == 1:
                            continue  # 추가 주문
                        elif again_or_pay == 0:
                            self.step5_final()  # 결제
                        else:
                            break
                    else:
                        break
                else:
                    break

    def step1(self):
        count = 0
        while count < 3:
            playsound.playsound("static/mp3_file/play1.mp3")
            print("음성으로 안내받길 원하시나요?")
            n = audio_routine(0)
            if n < 3:  # 대답이 부정 혹은 오류 일때
                if count < 2:  # 3번만 확인
                    playsound.playsound("static/mp3_file/again.mp3")
                    count += 1
                else:
                    self.parent.stackedWidget.setCurrentIndex(0)
                    return -1
            else:
                self.parent.stackedWidget.setCurrentIndex(2)
                return 0

    def step2(self):
        count = 0
        while count < 2:
            playsound.playsound("static/mp3_file/play2.mp3")

            print("어떤 메뉴를 원하시나요? 한식, 백반, 분식, 양식, 일식, 음료")
            n = audio_routine(1)
            if n == -1:
                if count < 1:  # 2번만 확인
                    playsound.playsound("static/mp3_file/again.mp3")
                    count += 1
                else:
                    self.parent.menuStackedWidget_Audio_Audio.setCurrentIndex(0)
                    return -1
            else:
                self.parent.menuStackedWidget_Audio.setCurrentIndex(n)
                return n

    def step3(self, m):
        count = 0
        while count < 2:
            print("해당 메뉴의 종류는 ~,~,~ 가 있습니다. 원하시는 메뉴를 말해주세요. ")
            if m == 0:
                playsound.playsound("static/mp3_file/menu1.mp3")
            elif m == 1:
                playsound.playsound("static/mp3_file/menu2.mp3")
            elif m == 2:
                playsound.playsound("static/mp3_file/menu3.mp3")
            elif m == 3:
                playsound.playsound("static/mp3_file/menu4.mp3")
            elif m == 4:
                playsound.playsound("static/mp3_file/menu5.mp3")
            elif m == 5:
                playsound.playsound("static/mp3_file/menu6.mp3")
            else:
                playsound.playsound("static/mp3_file/error.mp3")

            n, key = audio_routine(2)
            if n == -1:
                if count < 1:  # 2번만 확인
                    playsound.playsound("static/mp3_file/again.mp3")
                    count += 1
                else:
                    self.parent.menuStackedWidget_Audio.setCurrentIndex(0)
                    return -1
            else:
                self.order_insert(self.menu[key][n])
                print("선택 완료")
                playsound.playsound("static/mp3_file/choice_complete.mp3")
                return 0

    def step4(self):
        count = 0
        while count < 2:
            playsound.playsound("static/mp3_file/play4.mp3")
            print("추가 주문을 하시겠습니까? 아니면 결제하시겠습니까?")
            n = audio_routine(3)
            if n == -1:
                if count < 1:  # 2번만 확인
                    playsound.playsound("static/mp3_file/again.mp3")
                    count += 1
                else:
                    self.parent.menuStackedWidget_Audio.setCurrentIndex(0)
                    return -1
            elif n < 4:
                return 0
            else:
                return 1

    def step5_final(self):
        print("허리 부근 중앙 오른쪽에 카드 리더기가 있습니다. ")

        print("결제 완료")

    # 메뉴를 장바구니에 추가하는 함수
    def order_insert(self, m):
        self.parent.order_list.append(m)


# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.n = 0
        self.setupUi(self)
        self.step = 0
        self.order_list = []
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

        self.eyes_routine()

    # ------- init -------#

    # homeButton 이 눌리면 작동할 함수
    def homeButtonFunction(self):
        self.stackedWidget.setCurrentIndex(0)

    # stayButton 이 눌리면 작동할 함수
    def stayButtonFunction(self):
        self.stackedWidget.setCurrentIndex(1)

    # takeOutButton 이 눌리면 작동할 함수
    def takeOutButtonFunction(self):
        self.stackedWidget.setCurrentIndex(1)

    # 눈 인식 쓰레드 함수
    def eyes_routine(self):
        eyes_thread = EyesThread(self)
        eyes_thread.start()

    # 오디오 인식 쓰레드 함수
    def audio_routine(self):
        t = AudioThread(self)
        t.start()

    # audioButton 이 눌리면 작동할 함수
    def audioButtonFunction(self):
        # 음성 인식
        self.audio_routine()

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

            if col > 4 and r == 0:
                r = 1
                n = 0
            elif col > 9 and r == 1:
                r = 2
                n = 0
            elif col > 14 and r == 2:
                r = 3
                n = 0
            tf.setItem(r, n, item)
            n += 1


def window_start():
    app = QApplication(sys.argv)
    ex = WindowClass()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    window_start()
