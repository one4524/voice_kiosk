import speech_recognition as sr


# audio file을 audio source로 사용합니다
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    audio = r.listen(source, phrase_time_limit=10)

# write audio to a WAV file
with open("microphone-results.wav", "wb") as f:
    f.write(audio.get_wav_data())
