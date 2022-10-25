from flask import Flask, render_template
from threading import Thread
from multiprocessing import Process
import concurrent.futures

from Audio.audio_recognition import AudioRecognition
from Camera.video_eyes_detection import eyes_detect

app = Flask(__name__)


def aaa():
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future = executor.submit(eyes_detect, )

    if future.result():
        print("음성안내")


def start():
    audio_recognition = AudioRecognition()

    return audio_recognition


@app.route('/')
def main():

    p = Process(target=eyes_detect)
    p.start()
    p.join()
    return render_template('main.html')


@app.route('/screen')
def screen():
    return render_template('/screen.html')


@app.route('/audio')
def audio():
    text = audio_recognition.listen()

    return render_template('/audio.html')


@app.route('/menu')
def menu():
    t = Thread(target=eyes_detect)
    t.start()
    t.join()
    return render_template('/menu.html')


@app.route('/payment')
def pay():
    return render_template('/main.html')


if __name__ == "__main__":
    audio_recognition = AudioRecognition()
    audio_recognition.listen()
    # 앱 실행
    # app.run(host="127.0.0.1", port="8080")
