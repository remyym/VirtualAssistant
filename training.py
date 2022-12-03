import random
import json
import pickle
from typing import List, Any, Tuple

import numpy as np

import nltk
from nltk.stem import WordNetLemmatizer

from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import SGD

wnl = WordNetLemmatizer()

intents: object = json.loads(open('intents.json').read())

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

words = [wnl.lemmatize(word) for word in words if word not in ignore]

words = sorted(set(words))
classes = sorted(set(classes))

pickle.dump(words, open("words.pkl", 'wb'))
pickle.dump(words, open("classes.pkl", 'wb'))

training: list[Any] = []
output_empty: list[int] = [0] * len(classes)

for document in documents:
    bag: list[int] = []
    word_patterns: list[str] = document[0]
    word_patterns = [wnl.lemmatize(word.lower()) for word in word_patterns]
    for word in words:
        bag.append(1) if word in word_patterns else bag.append(0)

    output_row: list[int] = list(output_empty)
    # output_row[classes.index(document[1])]
