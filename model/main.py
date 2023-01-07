import os
import random
import warnings

import nltk
import numpy as np
from keras.layers import Dense, Dropout
from keras.models import Sequential
from keras.optimizers import SGD
from nltk.stem import WordNetLemmatizer

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

ignore = ['?', '!', '.', ',', "'", '-']


class GenericModel:
    def __init__(self, intents):
        self.intents = intents

        # Define training data
        self.words = []
        self.classes = []
        self.model = None

        self.hist = None
        self.lemmatizer = WordNetLemmatizer()

    def train(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)

        documents = []
        training = []

        for intent in self.intents:
            for pattern in intent['patterns']:
                word = nltk.word_tokenize(pattern)
                self.words.extend(word)

                documents.append((word, intent['tag']))
                if intent['tag'] not in self.classes:
                    self.classes.append(intent['tag'])

        self.words = list(
            map(lambda w: self.lemmatizer.lemmatize(w.lower()), filter(lambda w: w not in ignore, self.words)))

        self.words = sorted(list(set(self.words)))
        self.classes = sorted(list(set(self.classes)))

        output_empty = [0] * len(self.classes)

        for doc in documents:
            word_patterns = doc[0]
            word_patterns = list(map(lambda w: self.lemmatizer.lemmatize(w.lower()), word_patterns))

            bag = list(map(lambda w: 1 if w in word_patterns else 0, self.words))

            output_row = list(output_empty)
            output_row[self.classes.index(doc[1])] = 1
            training.append([bag, output_row])

        random.shuffle(training)
        training = np.array(training, dtype=object)

        train_x = list(training[:, 0])
        train_y = list(training[:, 1])

        self.model = Sequential()
        self.model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(len(train_y[0]), activation='softmax'))
        self.model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

        self.model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)

        self.model.save('Model/save')

    def clean_up_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [self.lemmatizer.lemmatize(word.lower()) for word in sentence_words]

        return sentence_words

    def bag_of_words(self, sentence):
        sentence_words = self.clean_up_sentence(sentence)

        bag = [0] * len(self.words)

        for s in sentence_words:
            for i, word in enumerate(self.words):
                if word == s:
                    bag[i] = 1

        return np.array(bag)

    def predict_class(self, sentence):
        bow = self.bag_of_words(sentence)
        res = self.model.predict(np.array([bow]))[0]

        error_threshold = 0.25
        results = [[i, r] for i, r in enumerate(res) if r > error_threshold]

        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []

        for r in results:
            return_list.append({'intent': self.classes[r[0]], 'probability': str(r[1])})

        return return_list

    def process(self, intents):
        list_of_intents = self.intents

        try:
            tag = intents[0]['intent']
            result = None

            for intent in list_of_intents:
                if intent['tag'] == tag:
                    result = intent

                    break
        except IndexError:
            result = list_of_intents['undefined']

        return result
