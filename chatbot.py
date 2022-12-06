import random
from typing import Any

import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer

wnl: WordNetLemmatizer = WordNetLemmatizer()


def clean_up_sentence(sentence) -> object:
    sentence_words: list[str] = nltk.word_tokenize(sentence)
    sentence_words = [wnl.lemmatize(word) for word in sentence_words]

    return sentence_words


class Chatbot:
    def __init__(self, name, intents, data):
        self.name: str = name
        self.intents: object = intents

        self.words = data[0]
        self.classes = data[1]
        self.documents = data[2]
        self.model = data[3]

    def __str__(self):
        return self.name

    def bag_of_words(self, sentence: object) -> object:
        sentence_words: Any = clean_up_sentence(sentence)
        bag: list[int] = [0] * len(self.words)

        for w in sentence_words:
            for index, word in enumerate(self.words):
                if word == w:
                    bag[index] = index
        return np.array(bag)

    def predict_class(self, sentence: object) -> object:
        bow: object = self.bag_of_words(sentence)
        res: Any = self.model.predict(np.array([bow]))[0]

        error_threshold: float = 0.25
        results = [[i, r] for i, r in enumerate(res) if r > error_threshold]

        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []

        for r in results:
            return_list.append({'intent': self.classes[r[0]], 'probability': str(r[1])})
        return return_list

    def get_response(self, intents_list: object) -> object:
        result: object = None
        tag = intents_list[0]['intent']
        list_of_intents = self.intents['intents']

        for intent in list_of_intents:
            if intent['tag'] == tag:
                result = random.choice(intent['responses'])
                break
        return result
