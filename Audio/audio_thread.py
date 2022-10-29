# 오디오 쓰레드
from PyQt5.QtCore import QThread
import playsound

from Audio.audio_routine import audio_routine, delete_order
from Audio.tts import make_tts


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
            playsound.playsound("static/mp3_file/play1.mp3")
            print("음성으로 안내받길 원하시나요?")
            n = audio_routine(0)
            if n < 3:  # 대답이 부정 혹은 오류 일때
                if count < 1:  # 2번만 확인
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
            else:
                self.parent.menuStackedWidget.setCurrentIndex(n)
                return n

    def step3(self, m):
        count = 0
        while count < 2:
            print("해당 메뉴의 종류는 여러 음식이 있습니다. 원하시는 메뉴를 말해주세요. ")
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
                return -1

            key = self.menu_list[m]
            n = audio_routine(2, key)
            if n == -1:
                if count < 1:  # 2번만 확인
                    playsound.playsound("static/mp3_file/again.mp3")
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
