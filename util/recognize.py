import speech_recognition as speech

recognizer = speech.Recognizer()


def main():
    with speech.Microphone() as source:
        audio = recognizer.listen(source)
    try:
        message = recognizer.recognize_google(audio)

        return message
    except speech.UnknownValueError:
        return None
