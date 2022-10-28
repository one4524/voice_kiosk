from Audio.audio import Audio

menu = {
    'korean': ['김치햄치즈볶음밥', '소금덮밥', '뼈다귀해장국', '소고기미역국', '냉면', '간장불고기', '제육볶음'],
    'chinese': ['짜장면', '짬뽕', '계란볶음밥', '탕수육', '군만두'],
    'schoolfood': ['떡볶이', '라볶이', '라면', '순대', '오므라이스', '야채김밥', '참치김밥'],
    'Westernfood': ['크림', '토마토', '알리오', '연어 샐러드', '감바스'],
    'japanesefood': ['왕돈까스', '치킨까스', '치즈돈까스', '냉모밀', '우동', '김치나베', '돈까스나베'],
    'beverage': ['물', '콜라', '사이다', '환타', '제로콜라', '제로사이다']
}

answer_list = ['아니', '아니오', '아니요', '네', '내', '넵', '냅', '넹', '냉', '웅', '응', '그래', '그레', '구래', '고래', '좋아', '음성']
cancel_list = ['취소', '다시', '취수', '홈', '처음', '캔슬', '취사']
first_list = ['한식', '중식', '분식', '양식', '일식', '음료', '한', '분']
second_list = menu
third_list = ['결제', '결재', '끝', '그만', '주문', '추가', '메뉴', '음식', '삭제']


def delete_order(order_list):
    audio = Audio()
    text = audio.listen()
    text_correct = audio.text_correction(text)
    text_word_list = audio.detect_word(text_correct)

    for i, m in enumerate(order_list):
        for _, v in menu.items():
            if m in v:
                return i

    return -1


# 음성 인식 함수
def audio_routine(step):
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
            print("i  - ", i, "// t -- ", t)
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
            print("i  - ", i, "// t -- ", t)
            if t in text_word_list:
                return i

    # 음식 선정 단계
    elif step == 2:
        # 취소 확인
        for _, t in enumerate(cancel_list):
            if t in text_word_list:
                return -1

        # 3단계
        for key, value in second_list.items():
            for i, t in enumerate(value):
                print("i  - ", i, "// t -- ", t)
                if t in text_word_list:
                    return i, key

    # 추가 주문 및 결제 선택 단계
    elif step == 3:
        # 취소 확인
        for _, t in enumerate(cancel_list):
            if t in text_word_list:
                return -1

        # 4단계
        for i, t in enumerate(third_list):
            print("i  - ", i, "// t -- ", t)
            if t in text_word_list:
                return i

    if step == 2:
        return -1, 'korean'
    else:
        return -1
