import json
import random
from abc import ABCMeta, ABC, abstractmethod
from typing import Any

import nltk
import numpy as np

from keras.layers import Dense, Dropout
from keras.models import Sequential
from keras.optimizers import SGD
from nltk.stem import WordNetLemmatizer

nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)

lemmatizer = WordNetLemmatizer()


class IAssistant(metaclass=ABCMeta):
    @abstractmethod
    def train_model(self):
        """ Implemented in child class """

    @abstractmethod
    def request_tag(self, message):
        """ Implemented in child class """

    @abstractmethod
    def request_method(self, message):
        """ Implemented in child class """

    @abstractmethod
    def request(self, message):
        """ Implemented in child class """


def clean_up_sentence(sentence) -> object:
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]

    return sentence_words


class GenericAssistant(IAssistant, ABC):
    def __init__(self, name, intents, intent_methods):
        self.name: str = name
        self.intents = json.loads(open(intents).read())
        self.intent_methods = intent_methods

        self.words, self.classes = [], []
        self.hist: object = None
        self.model = self.train_model()

    def __str__(self):
        return self.name

    def train_model(self):
        documents = []
        ignore = ['?', '!', '.', ',']

        for intent in self.intents['intents']:
            for pattern in intent['patterns']:
                word = nltk.word_tokenize(pattern)
                self.words.extend(word)

                documents.append((word, intent['tag']))
                if intent['tag'] not in self.classes:
                    self.classes.append(intent['tag'])

        self.words = [lemmatizer.lemmatize(word.lower()) for word in self.words if word not in ignore]

        self.words = sorted(list(set(self.words)))
        self.classes = sorted(list(set(self.classes)))

        training = []
        output_empty = [0] * len(self.classes)

        for doc in documents:
            bag = []
            word_patterns = doc[0]
            word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]

            for word in self.words:
                bag.append(1) if word in word_patterns else bag.append(0)

            output_row = list(output_empty)
            output_row[self.classes.index(doc[1])] = 1
            training.append([bag, output_row])

        random.shuffle(training)
        training = np.array(training)

        train_x = list(training[:, 0])
        train_y = list(training[:, 1])

        model = Sequential()
        model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(64, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(len(train_y[0]), activation='softmax'))

        sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
        model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

        hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)
        model.save("Model", hist)

        return model

    def _bag_of_words(self, sentence: object) -> object:
        sentence_words: Any = clean_up_sentence(sentence)

        bag = [0] * len(self.words)

        for s in sentence_words:
            for i, word in enumerate(self.words):
                if word == s:
                    bag[i] = 1

        return np.array(bag)

    def _predict_class(self, sentence: list) -> object:
        bow: object = self._bag_of_words(sentence)
        res: Any = self.model.predict(np.array([bow]))[0]

        error_threshold: float = 0.25
        results = [[i, r] for i, r in enumerate(res) if r > error_threshold]

        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []

        for r in results:
            return_list.append({'intent': self.classes[r[0]], 'probability': str(r[1])})

        return return_list

    def _process(self, intents: object) -> object:
        list_of_intents = self.intents['intents']

        try:
            tag = intents[0]['intent']
            result: object = None

            for intent in list_of_intents:
                if self.request_tag(intent) == tag:
                    result = intent
                    break
        except IndexError:
            result = list_of_intents['undefined']

        return result

    def request_tag(self, intent: object):
        return intent['tag']

    def request_method(self, ints: object):
        if ints[0]['intent'] in self.intent_methods.keys():
            return self.intent_methods[ints[0]['intent']]

        return None

    def request(self, message):
        ints = self._predict_class(message)
        result = self._process(ints)

        method = self.request_method(ints)

        if method is not None:
            return method(), result

        return random.choice(result['responses']), result
