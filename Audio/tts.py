from gtts import gTTS

t1 = "음성으로 안내받기를 원하시나요?"
t2 = "메뉴는 한식, 백반, 분식, 양식, 일식, 음료 중 어떤 것을 원하시나요?"
t3 = "선택 완료했습니다."
t4 = "음식 추가 주문을 하시겠습니까? 아니면 결제하시겠습니까?"
m1 = "한식 메뉴의 종류는 '김치햄치즈볶음밥', '소금덮밥', '뼈다귀해장국', '소고기미역국', '냉면', '간장불고기', '제육볶음' 있습니다. 원하시는 메뉴를 말해주세요."
m2 = "중식 메뉴의 종류는 '짜장면', '짬뽕', '계란볶음밥', '탕수육', '군만두' 있습니다. 원하시는 메뉴를 말해주세요."
m3 = "분식 메뉴의 종류는 '떡볶이', '라볶이', '라면', '순대', '오므라이스', '야채김밥', '참치김밥' 있습니다. 원하시는 메뉴를 말해주세요."
m4 = "양식 메뉴의 종류는 '크림파스타', '토마토파스타', '알리오올리오', '연어샐러드', '감바스'  있습니다. 원하시는 메뉴를 말해주세요."
m5 = "일식 메뉴의 종류는 '왕돈까스', '치킨까스', '치즈돈까스', '냉모밀', '우동', '김치나베', '돈까스나베' 있습니다. 원하시는 메뉴를 말해주세요."
m6 = "음료 메뉴의 종류는 '물', '콜라', '사이다', '환타', '제로콜라', '제로사이다' 있습니다. 원하시는 메뉴를 말해주세요."

err = "잘못된 메뉴입니다."
again = "다시 말해주세요."


tts = gTTS(text=t1, lang='ko')

tts.save("play1.mp3")

tts2 = gTTS(text=t2, lang='ko')

tts2.save("play2.mp3")

tts3 = gTTS(text=t3, lang='ko')

tts3.save("choice_complete.mp3")

tts4 = gTTS(text=t4, lang='ko')

tts4.save("play4.mp3")

menu1 = gTTS(text=m1, lang='ko')

menu1.save("menu1.mp3")

menu2 = gTTS(text=m2, lang='ko')

menu2.save("menu2.mp3")
menu3 = gTTS(text=m3, lang='ko')

menu3.save("menu3.mp3")
menu4 = gTTS(text=m4, lang='ko')

menu4.save("menu4.mp3")
menu5 = gTTS(text=m5, lang='ko')

menu5.save("menu5.mp3")
menu6 = gTTS(text=m6, lang='ko')

menu6.save("menu6.mp3")

error = gTTS(text=err, lang='ko')
error.save("error.mp3")

again_tts = gTTS(text=again, lang='ko')

again_tts.save("again.mp3")
