from gtts import gTTS

t1 = "음성으로 안내받길 원하시나요?"
t2 = "어떤 메뉴를 원하시나요? 한식, 백반, 분식, 양식, 일식, 음료"

tts = gTTS(text=t1, lang='ko')

tts.save("play1.mp3")

tts2 = gTTS(text=t2, lang='ko')

tts2.save("play2.mp3")

