import speech_recognition as sr
import base64
import urllib3
import json

openApiURL = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"
accessKey = "e1d17392-08c5-4578-b194-a1cb212d4f83"
audioFilePath = "AUDIO_FILE_PATH"
languageCode = "korean"

r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    audio = r.listen(source)


print(type(audio))


print(type(audio.get_wav_data()))


audioContents = base64.b64encode(audio.get_wav_data()).decode("utf8")


print(type(audioContents))

requestJson = {
    "access_key": accessKey,
    "argument": {
        "language_code": languageCode,
        "audio": audioContents
    }
}

http = urllib3.PoolManager()
response = http.request(
    "POST",
    openApiURL,
    headers={"Content-Type": "application/json; charset=UTF-8"},
    body=json.dumps(requestJson)
)

print("[responseCode] " + str(response.status))
print("[responBody]")
print(str(response.data, "utf-8"))