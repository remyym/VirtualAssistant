import random
import json
import re

from model import GenericModel


class GenericAssistant:
    def __init__(self, name, data, handlers):
        self.name = name
        self.handlers = handlers

        with open(data) as f:
            self.data = json.loads(f.read())

        self.model = GenericModel(intents=self.data['intents'])
        self.model.train()

    def __str__(self):
        return self.name

    def get_intent(self, tag):
        ints = None

        for intent in self.data['intents']:
            if intent.get('tag') == tag:
                ints = intent

        return ints

    def get_method(self, tag, params):
        if tag in self.handlers.mappings:
            return self.handlers.mappings[tag](params)

    def get_response(self, tag):
        intent = self.get_intent(tag)

        return random.choice(intent.get('responses'))

    def request(self, message):
        predictions = self.model.predict_class(message)
        result = self.model.process(predictions)
        response = self.get_response(result.get('tag'))

        # Check if there is a method
        method = self.get_method(result.get('tag'), self.model.clean_up_sentence(message))

        if method and not response:
            return method, result

        pattern = re.compile(r"{([^}]*)}")
        matches = pattern.findall(response)

        for match in matches:
            self.handlers.respond(result.get('tag'), match)

        return response, result
