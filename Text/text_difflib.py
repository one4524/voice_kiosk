import difflib


# difflib 라이브러리를 이용한 텍스트 비교
def similar(answer_string, input_string):
    answer_bytes = bytes(answer_string, 'utf-8')
    input_bytes = bytes(input_string, 'utf-8')
    answer_bytes_list = list(answer_bytes)
    input_bytes_list = list(input_bytes)
    sm = difflib.SequenceMatcher(None, answer_bytes_list, input_bytes_list)

    return sm.ratio()


"""
if __name__ == "__main__":
    a = "키오스크 안내 시스템"
    b = "키오스키 안녕 시스템"
    #similarity = similar(a, b)
"""
