# -*- coding:utf-8 -*-
import urllib3
import json
import base64
import speech_recognition as sr

from hanspell import spell_checker


class AudioRecognition:

    # 초기화
    def __init__(self):
        self.openApiURL = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"
        self.accessKey = "e1d17392-08c5-4578-b194-a1cb212d4f83"
        # audioFilePath = "AUDIO_FILE_PATH"
        self.languageCode = "korean"
        self.r = sr.Recognizer()
        self.http = urllib3.PoolManager()

    # 음성 듣기
    def listen(self):
        with sr.Microphone() as source:
            print("Say something!")
            audio = self.r.listen(source)

        audioContents = base64.b64encode(audio.get_wav_data()).decode("utf8")

        requestJson = {
            "access_key": self.accessKey,
            "argument": {
                "language_code": self.languageCode,
                "audio": audioContents
            }
        }

        response = self.http.request(
            "POST",
            self.openApiURL,
            headers={"Content-Type": "application/json; charset=UTF-8"},
            body=json.dumps(requestJson)
        )

        print("[responseCode] " + str(response.status))
        print("[responseBody]")
        print(str(response.data, "utf-8"))

        json_obj = json.loads(str(response.data, "utf-8"))

        return json_obj["return_object"]['recognized']
