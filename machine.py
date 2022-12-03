import json
import pickle
import random
from typing import Any

import nltk
import numpy as np
from keras.models import load_model
from nltk.stem import WordNetLemmatizer

wnl: WordNetLemmatizer = WordNetLemmatizer()

intents: object = json.loads(open('intents.json').read())

words: Any = pickle.load(open('words.pkl', 'rb'))
classes: object = pickle.load(open('classes.pkl', 'rb'))
model: Any | None = load_model('model.h5')


def clean_up_sentence(sentence) -> object:
    sentence_words: list[str] = nltk.word_tokenize(sentence)
    sentence_words = [wnl.lemmatize(word) for word in sentence_words]

    return sentence_words


def bag_of_words(sentence: object) -> object:
    sentence_words: Any = clean_up_sentence(sentence)
    bag: list[int] = [0] * len(words)

    for w in sentence_words:
        for index, word in enumerate(words):
            if word == w:
                bag[index] = index
    return np.array(bag)


def predict_class(sentence: object) -> object:
    bow: object = bag_of_words(sentence)
    res: Any = model.predict(np.array([bow]))[0]

    error_threshold: float = 0.25
    results: list[list[Any]] = [[i, r] for i, r in enumerate(res) if r > error_threshold]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list: list[dict[str, str | Any]] = []

    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list


def get_response(intents_list: object, intents_json: object) -> object:
    result: object = None
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']

    for intent in list_of_intents:
        if intent['tag'] == tag:
            result = random.choice(intent['responses'])
            break
    return result
