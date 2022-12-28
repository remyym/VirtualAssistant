import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('rate', 180)
engine.setProperty('voice', voices[1].id)


def main(msg, prnt=False):
    if prnt:
        print(msg)

    engine.say(msg)
    engine.runAndWait()
