import pyttsx3
import speech_recognition as sr
from speech_recognition import AudioData

import machine

engine = pyttsx3.init()


def speak(text):
    voices: object = engine.getProperty('voices')

    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()


speak("Hey!")

while True:
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening..")
        audio: AudioData = r.listen(source)

    try:
        message: str = r.recognize_google(audio)
        print('I heard \"' + message + '"')

        ints: object = machine.predict_class(message)
        response: object = machine.get_response(ints, machine.intents)

        print(response)
        speak(response)
    except sr.UnknownValueError:
        speak("Could you please repeat that?")
