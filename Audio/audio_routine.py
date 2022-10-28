from Audio.audio import Audio

menu = {
    'korean': ['김치햄치즈볶음밥', '소금덮밥', '뼈다귀해장국', '소고기미역국', '냉면', '간장불고기', '제육볶음'],
    'chinese': ['짜장면', '짬뽕', '계란볶음밥', '탕수육', '군만두'],
    'schoolfood': ['떡볶이', '라볶이', '라면', '순대', '오므라이스', '야채김밥', '참치김밥'],
    'Westernfood': ['크림파스타', '토마토파스타', '알리오올리오', '연어샐러드', '감바스'],
    'japanesefood': ['왕돈까스', '치킨까스', '치즈돈까스', '냉모밀', '우동', '김치나베', '돈까스나베'],
    'beverage': ['물', '콜라', '사이다', '환타', '제로콜라', '제로사이다']
}

answer_list = ['아니', '아니오', '아니요', '네', '내', '넵', '냅', '넹', '냉', '웅', '응', '그래', '그레', '구래', '고래', '좋아', '음성']
cancel_list = ['취소', '다시', '취수', '홈', '처음', '캔슬']
first_list = ['한식', '백반', '분식', '양식', '일식', '음료', '한', '분']
second_list = menu
third_list = ['결제', '결재', '끝', '그만', '주문', '추가', '메뉴', '음식']


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

    # 음식 선정 단계
    elif step == 2:
        for key, value in second_list.items():
            for i, t in enumerate(value):
                if t in text_word_list:
                    return i, key

    # 추가 주문 및 결제 선택 단계
    elif step == 3:
        for i, t in enumerate(third_list):
            if t in text_word_list:
                return i

    if step == 2:
        return -1, 'korean'
    else:
        return -1
