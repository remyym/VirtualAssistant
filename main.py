import pyttsx3
from pyttsx3 import Engine

from Class import GenericAssistant
from Methods import Mappings

alexa = GenericAssistant(name='Alexa', intents='intents.json', intent_methods=Mappings)

engine: Engine = pyttsx3.init()
voices: object = engine.getProperty('voices')

engine.setProperty('rate', 175)
engine.setProperty('voice', voices[1].id)


def text_to_speach(msg):
    print(msg)

    engine.say(msg)
    engine.runAndWait()


text_to_speach("Hey!")

while True:
    message = input()
    response, result = alexa.request(message)

    text_to_speach(response)

    if alexa.request_tag(result) == 'farewell':
        exit()
