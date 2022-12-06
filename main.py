import pyttsx3
import speech_recognition as sr

from pathlib import Path
from pyttsx3 import Engine
from keras.models import load_model

import json
import warnings

import training
from chatbot import Chatbot

intents: object = json.loads(open(Path() / 'intents.json').read())
network = Path('Network')

words, classes, documents = training.sort()

try:
    model = load_model("Model")
except IOError:
    model = training.train(words, classes, documents)

data = [words, classes, documents, model]
alexa = Chatbot(name='Alexa', intents=intents, data=data)

engine: Engine = pyttsx3.init()
voices: object = engine.getProperty('voices')

engine.setProperty('rate', 150)
engine.setProperty('voice', voices[1].id)

recognizer = sr.Recognizer()


def text_to_speach(msg):
    print(msg)

    engine.say(msg)
    engine.runAndWait()


def get_response(msg):
    new = None

    try:
        prediction = alexa.predict_class(msg)
    except ValueError:
        warnings.warn("ValueError: Input 0 of layer \"sequential\" is incompatible with the layer: retraining model")

        new = training.train(words, classes, documents)
        prediction = alexa.predict_class(msg)

    res: object = alexa.get_response(prediction)

    return prediction, res, new


text_to_speach("Hey!")

while True:
    message = input()

    # with sr.Microphone() as source:
    #     print("Listening..")
    #
    #     audio: sr.AudioData = recognizer.listen(source)
    # try:
    #     message: str = recognizer.recognize_google(audio)
    #     print('I heard \"' + message + '"')
    #
    #     ints, response, new_model = get_response(message)
    #     if new_model:
    #         model = new_model
    #         data = [words, classes, documents, model]
    #
    #     text_to_speach(response)
    # except sr.UnknownValueError:
    #     text_to_speach("Could you please repeat that?")

    ints, response, new_model = get_response(message)
    if new_model:
        model = new_model
        data = [words, classes, documents, model]

    print(ints)

    text_to_speach(response)
