# -*- coding:utf-8 -*-
import urllib3
import json
import base64
import speech_recognition as sr

from hanspell import spell_checker


class Audio:

    # 초기화
    def __init__(self):
        self.openApiURL_voice = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"  # 음성 인식 URL
        # openApiURL = "http://aiopen.etri.re.kr:8000/WiseNLU"  # 문어
        self.openApiURL_word = "http://aiopen.etri.re.kr:8000/WiseNLU_spoken"  # 구어 단어 인식 URL
        self.accessKey = "e1d17392-08c5-4578-b194-a1cb212d4f83"
        # audioFilePath = "AUDIO_FILE_PATH"
        self.languageCode = "korean"
        self.analysisCode = "morp"
        self.r = sr.Recognizer()  # 음석 인식 객체
        self.http = urllib3.PoolManager()  # http 객체

    # 음성 오타 수정
    @staticmethod
    def text_correction(text):
        collect_text = spell_checker.check(text)

        return collect_text.as_dict()['checked']

    # 단어 추출
    def detect_word(self, text):

        word_request_json = {
            "access_key": self.accessKey,
            "argument": {
                "text": text,
                "analysis_code": self.analysisCode
            }
        }

        response = self.http.request(
            "POST",
            self.openApiURL_word,
            headers={"Content-Type": "application/json; charset=UTF-8"},
            body=json.dumps(word_request_json)
        )

        print("[responseCode] " + str(response.status))
        print("[responseBody]")
        print(str(response.data, "utf-8"))

        json_obj = json.loads(str(response.data, "utf-8"))

        obj_morp = json_obj["return_object"]["sentence"][0]["morp"]

        print(obj_morp)

        nn_list = []
        for nn in obj_morp:
            print(nn["type"])
            if nn["type"] == 'NNG':
                nn_list.append(nn['lemma'])
                print(nn['lemma'])
            elif nn["type"] == 'NNP':
                nn_list.append(nn['lemma'])
                print(nn['lemma'])
            elif nn["type"] == 'NNB':
                nn_list.append(nn['lemma'])
                print(nn['lemma'])
            elif nn["type"] == 'IC':
                nn_list.append(nn['lemma'])
                print(nn['lemma'])
            else:
                print("no")

        return nn_list

    # 음성 듣기
    def listen(self):
        with sr.Microphone() as source:
            print("Say something!")
            audio = self.r.listen(source)

        audio_contents = base64.b64encode(audio.get_wav_data()).decode("utf8")

        voice_request_json = {
            "access_key": self.accessKey,
            "argument": {
                "language_code": self.languageCode,
                "audio": audio_contents
            }
        }

        response = self.http.request(
            "POST",
            self.openApiURL_voice,
            headers={"Content-Type": "application/json; charset=UTF-8"},
            body=json.dumps(voice_request_json)
        )

        print("[responseCode] " + str(response.status))
        print("[responseBody]")
        print(str(response.data, "utf-8"))

        json_obj = json.loads(str(response.data, "utf-8"))

        return json_obj["return_object"]['recognized']
