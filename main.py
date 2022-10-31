import os
import sys
from PyQt5 import uic
from PyQt5.QtCore import Qt, QEventLoop, QTimer, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QLabel, QWidget, QVBoxLayout
from Audio.audio_thread import AudioThread
from Camera.video_thread import EyesThread
from DB.db import insert_menus, insert_order, data_transform, create_table, drop_table


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

        # 매장 이용 버튼 설정
        stay_pixmap = QPixmap('./static/stay.png')  # QPixmap 생성
        stay_pixmap = stay_pixmap.scaled(195, 200, Qt.IgnoreAspectRatio)  # 이미지 크기 변경
        stay_icon = QIcon()  # QIcon 생성
        stay_icon.addPixmap(stay_pixmap)  # 아이콘에 이미지 설정

        self.stay2Button.setIcon(stay_icon)  # Pushbutton에 아이콘 설정
        self.stay2Button.clicked.connect(self.stayButtonFunction)

        # 테이그아웃 버튼 설정
        takeout_pixmap = QPixmap('./static/pickup.png')  # QPixmap 생성
        takeout_pixmap = takeout_pixmap.scaled(195, 200, Qt.IgnoreAspectRatio)  # 이미지 크기 변경

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
        self.homeButton.setEnabled(True)
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
            cell_widget.setLayout(QVBoxLayout())
            cell_pixmap_label = QLabel(self)
            cell_text_label = QLabel(self)
            pixmap = QPixmap(f'./static/menu_img/{val}.png')  # QPixmap 생성
            pixmap = pixmap.scaled(120, 160, Qt.KeepAspectRatio)  # 이미지 크기 변경
            cell_pixmap_label.setPixmap(pixmap)
            cell_text_label.setAlignment(Qt.AlignCenter)
            cell_text_label.setText(val)

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

"""
# 테이블에 넣을 커스텀 위젯 클래스 - 이미지와 텍스트 함께 존재
class CustomWidget(QWidget):
    def __init__(self, text, img, parent=None):
        QWidget.__init__(self, parent)

        self._text = text
        self._img = img

        self.setLayout(QVBoxLayout())
        self.lbPixmap = QLabel(self)
        self.lbText = QLabel(self)
        self.lbText.setAlignment(Qt.AlignCenter)

        self.layout().addWidget(self.lbPixmap)
        self.layout().addWidget(self.lbText)

        self.initUi()

    def initUi(self):
        self.lbPixmap.setPixmap(QPixmap(self._img).scaled(self.lbPixmap.size(), Qt.KeepAspectRatio))
        self.lbText.setText(self._text)

    @pyqtProperty(str)
    def img(self):
        return self._img

    @img.setter
    def total(self, value):
        if self._img == value:
            return
        self._img = value
        self.initUi()

    @pyqtProperty(str)
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if self._text == value:
            return
        self._text = value
        self.initUi()
"""

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
