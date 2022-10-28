import os
import sys
from PyQt5 import uic
from PyQt5.QtCore import QThread, QEventLoop, QTimer, QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QListWidgetItem
import playsound
from Audio.audio_routine import audio_routine, delete_order
from Audio.tts import make_tts
from Camera.video import EyesThread
from db import insert_menus, insert_order, data_transform, create_table, drop_table


# UI파일 연결
# 단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


form = resource_path('static/main.ui')
form_class = uic.loadUiType(form)[0]

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


# 오디오 쓰레드
class AudioThread(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.menu = menu

    def run(self):
        state = False
        self.parent.button_set_enabled(False)
        if self.step1() == 0:  # 음성 안내
            while True:
                n = self.step2()
                if n != -1:  # 메뉴 선택
                    if self.step3(n) == 0:  # 음식 선택
                        again_or_pay = self.step4()  # 추가 주문 or 결제
                        if again_or_pay == 1:
                            continue  # 추가 주문
                        elif again_or_pay == 0:
                            state = True
                            self.step5_final()  # 결제
                            break
                        else:
                            break
                    else:
                        break
                else:
                    break

        if not state:
            # audio 루틴이 끝나면 실행
            self.parent.homeButton.click()

        self.parent.button_set_enabled(True)
        self.quit()

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
                    return -1
            else:
                self.parent.stackedWidget.setCurrentIndex(1)
                return 0

    def step2(self):
        count = 0
        while count < 2:
            playsound.playsound("static/mp3_file/play2.mp3")

            print("어떤 메뉴를 원하시나요? 한식, 중식, 분식, 양식, 일식, 음료")
            n = audio_routine(1)
            if n == -1:
                if count < 1:  # 2번만 확인
                    playsound.playsound("static/mp3_file/again.mp3")
                    count += 1
                else:
                    return -1
            elif n == 6:
                self.parent.menuStackedWidget.setCurrentIndex(0)
            elif n == 7:
                self.parent.menuStackedWidget.setCurrentIndex(1)
            else:
                self.parent.menuStackedWidget.setCurrentIndex(n)
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
                    return -1
            else:
                if key == menu_list[0]:
                    self.parent.cell_clicked_event1(0, n)
                elif key == menu_list[1]:
                    self.parent.cell_clicked_event2(0, n)
                elif key == menu_list[2]:
                    self.parent.cell_clicked_event3(0, n)
                elif key == menu_list[3]:
                    self.parent.cell_clicked_event4(0, n)
                elif key == menu_list[4]:
                    self.parent.cell_clicked_event5(0, n)
                elif key == menu_list[5]:
                    self.parent.cell_clicked_event6(0, n)

                print("선택 완료")
                playsound.playsound("static/mp3_file/choice_complete.mp3")
                return 0

    def step4(self):
        count = 0
        while count < 2:
            playsound.playsound("static/mp3_file/play4.mp3")
            print("추가 주문이나 삭제를 원하십니까? 아니면 결제하시겠습니까?")
            n = audio_routine(3)
            if n == -1:
                if count < 1:  # 2번만 확인
                    playsound.playsound("static/mp3_file/again.mp3")
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
                self.parent.select_list_item = delete_order(self.parent.order_list)
                self.parent.list_item_delete_event()

            else:
                return 1  # 추가 주문

    def step5_final(self):
        print("허리 부근 중앙 오른쪽에 카드 리더기가 있습니다.")
        print("결제 완료")
        self.parent.pay_button_clicked_event()


def reset():
    loop = QEventLoop()
    QTimer.singleShot(3000, loop.quit)  # msec
    loop.exec_()


# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.n = 0
        self.setupUi(self)
        self.audio_thread = AudioThread(self)
        self.eyes_thread = EyesThread(self)
        self.step = 0
        self.order_number = 0
        self.amount = 0
        self.order_list = []
        self.order_count_list = []
        self.select_list_item = -1

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
            til = table_idx_lookup[k]
            self.set_menuTableWidgetData(self.tf_list[til], v)

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
            item.setSizeHint(QSize(30, 30))
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
                item.setSizeHint(QSize(30, 30))
                item.setTextAlignment(4)
                self.selectMenuCountList.insertItem(self.select_list_item, item)

        self.calculation_money()

    def add_list_item(self, data):
        item = QListWidgetItem(data)
        item.setSizeHint(QSize(300, 30))
        item.setTextAlignment(4)
        self.selectMenuList.addItem(item)

    def add_list_item_count(self, data):
        item = QListWidgetItem(data)
        item.setSizeHint(QSize(30, 30))
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
            item.setSizeHint(QSize(30, 30))
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
    # db
    drop_table("menus")  # menus 테이블이 존재할 경우 삭제
    create_table()  # orders 와 menus 테이블 생성 but 이미 존재할 시 생성 안함
    insert_menus()  # 메뉴판 정보 저장

    # qt
    window_start()  # qt 시작
