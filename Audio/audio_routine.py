from Audio.audio import Audio
from Text.text import compare_text

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
    '소고기미역국': ['소', '고기', '미역', '미역국'],
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

        print("1단계")
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

        print("2단계")
        # 2단계
        for i, t in enumerate(first_list):
            if t in text_word_list:
                return i

        # 텍스트 유사도 분석
        similarity_num = compare_text(text_word_list, first_list)
        if similarity_num != -1:
            return similarity_num


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
                    print("keyword-- ", keyword)
                    # 키워드 비교
                    if keyword in text_word_list:
                        return i

                # 텍스트 유사도 분석
                similarity_num = compare_text(text_word_list, menu_keyword[food])
                if similarity_num != -1:
                    return i

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

    return -1
