import json
import random
from pathlib import Path
from typing import Any

import nltk
import numpy as np

from nltk.stem import WordNetLemmatizer
from keras.layers import Dense, Dropout
from keras.models import Sequential
from keras.optimizers import SGD

wnl: WordNetLemmatizer = WordNetLemmatizer()

root = Path('.')
network = root / 'Network'

intents: object = json.loads(open(root / 'intents.json').read())


def sort():
    words: list[str] = []
    classes: list[Any] = []
    documents: list[tuple[list[str], Any]] = []
    ignore: list[str] = ['?', '!', '.', ',']

    for intent in intents['intents']:
        for pattern in intent['patterns']:
            word_list: list[str] = nltk.word_tokenize(pattern)
            words.extend(word_list)
            documents.append((word_list, intent['tag']))
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    words = [wnl.lemmatize(word) for word in words if ignore not in word]

    words = sorted(set(words))
    classes = sorted(set(classes))

    return words, classes, documents


def train(words, classes, documents):
    training: Any = []
    output_empty: list[int] = [0] * len(classes)

    for document in documents:
        bag: list[int] = []
        word_patterns: list[str] = document[0]
        word_patterns = [wnl.lemmatize(word.lower()) for word in word_patterns]
        for word in words:
            bag.append(1) if word in word_patterns else bag.append(0)

        output_row: list[int] = list(output_empty)
        output_row[classes.index(document[1])] = 1
        training.append([bag, output_row])

    random.shuffle(training)
    training = np.array(training, dtype=object)

    train_x: list[list[list[int]]] = list(training[:, 0])
    train_y: list[list[list[int]]] = list(training[:, 1])

    model: Sequential = Sequential()
    model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(len(train_y[0]), activation='softmax'))

    sgd: SGD = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

    hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)
    model.save("Model", hist)

    return model
