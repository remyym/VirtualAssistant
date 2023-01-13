import os
import random
import warnings
from typing import Any

import nltk
from keras.layers import Dense, Dropout
from keras.models import Sequential
from keras.optimizers import SGD
from nltk.stem import WordNetLemmatizer
from numpy import ndarray, array

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

ignore = ['?', '!', '.', ',']


class GenericModel:
    def __init__(self, intents: dict):
        # Set variables
        self.intents = intents

        # Define training data
        self.words = []
        self.classes = []
        self.model = None

        self.lemmatizer = WordNetLemmatizer()

    def train(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            sgd: SGD = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)

        documents: list = []
        training: ndarray | list = []

        for intent in self.intents:
            for pattern in intent['patterns']:
                word: list[str] = nltk.word_tokenize(pattern)
                self.words.extend(word)

                documents.append((word, intent['tag']))
                if intent['tag'] not in self.classes:
                    self.classes.append(intent['tag'])

        self.words = list(
            map(lambda w: self.lemmatizer.lemmatize(w.lower()), filter(lambda w: w not in ignore, self.words)))

        self.words = sorted(list(set(self.words)))
        self.classes = sorted(list(set(self.classes)))

        output_empty: list[int] = [0] * len(self.classes)

        for doc in documents:
            word_patterns: list = doc[0]
            word_patterns = list(map(lambda w: self.lemmatizer.lemmatize(w.lower()), word_patterns))

            bag: list[int] = list(map(lambda w: 1 if w in word_patterns else 0, self.words))

            output_row: list[int] = list(output_empty)
            output_row[self.classes.index(doc[1])] = 1
            training.append([bag, output_row])

        random.shuffle(training)
        training = array(training, dtype=object)

        train_x: list[Any] | list | Any = list(training[:, 0])
        train_y: list[Any] | list | Any = list(training[:, 1])

        self.model = Sequential()

        self.model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(len(train_y[0]), activation='softmax'))

        self.model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
        self.model.fit(array(train_x), array(train_y), epochs=200, batch_size=5, verbose=1)

        self.model.save('Model/save')

    def clean_up_sentence(self, sentence: str) -> list:
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [self.lemmatizer.lemmatize(word.lower()) for word in sentence_words]

        return sentence_words

    def bag_of_words(self, sentence: str) -> ndarray:
        sentence_words = self.clean_up_sentence(sentence)

        bag: list[int] = [0] * len(self.words)

        for s in sentence_words:
            for i, word in enumerate(self.words):
                if word == s:
                    bag[i] = 1

        return array(bag)

    def predict_class(self, sentence: str) -> list:
        bow: ndarray = self.bag_of_words(sentence)
        res: Any = self.model.predict(array([bow]))[0]

        error_threshold: float = 0.25
        results: list = [[i, r] for i, r in enumerate(res) if r > error_threshold]

        results.sort(key=lambda x: x[1], reverse=True)
        return_list: list = []

        for r in results:
            return_list.append({'intent': self.classes[r[0]], 'probability': str(r[1])})

        return return_list

    def process(self, intents: list) -> dict:
        list_of_intents: dict = self.intents

        try:
            tag: str = intents[0].get('intent')
            result: dict | None = None

            for intent in list_of_intents:
                if intent.get('tag') == tag:
                    result = intent

                    break
        except IndexError:
            result = list_of_intents['undefined']

        return result
