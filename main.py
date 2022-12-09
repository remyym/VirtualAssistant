import pyttsx3
from pyttsx3 import Engine

from Class import GenericAssistant
from Methods import Mappings

alexa = GenericAssistant(name='Alexa', intents='intents.json', intent_methods=Mappings)

engine: Engine = pyttsx3.init()
voices: object = engine.getProperty('voices')

engine.setProperty('rate', 180)
engine.setProperty('voice', voices[1].id)


def tts(msg):
    print(msg)

    engine.say(msg)
    engine.runAndWait()


if __name__ == '__main__':
    tts("Hey!")

    try:
        while True:
            message = None

            try:
                message = input()
            except UnicodeDecodeError:
                exit(1)

            if message:
                response, result = alexa.request(message)
                tts(response)

                if alexa.request_tag(result) == 'farewell':
                    exit(0)
    except KeyboardInterrupt:
        exit(1)
