# 텍스트 유사도 분석 함수
import Text.text_levenshtein


def compare_text(audio_word_list, compare_list):
    similarity_score = 10
    similarity_word_num = -1

    for audio_word in audio_word_list:
        for index, compare_word in enumerate(compare_list):
            similarity_score_tmp = Text.text_levenshtein.jamo_levenshtein(audio_word, compare_word)
            # 유사도 거리가 일정 수준 가깝고, 기존 보다 가까울 경우에 인정
            if similarity_score_tmp <= 0.5 and similarity_score > similarity_score_tmp:
                similarity_score = similarity_score_tmp
                similarity_word_num = index
                print("similarity-- ", similarity_score, "/ keyword--", compare_word, "/ audio_word--", audio_word)

    if similarity_word_num != -1:
        return similarity_word_num
    else:
        return -1
