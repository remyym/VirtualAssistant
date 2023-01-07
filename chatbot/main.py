import random
import re

from utils import format_data
from model import GenericModel


class GenericAssistant:
    def __init__(self, name, intents, sentences, user, handlers):
        self.name = name
        self.handlers = handlers

        self.message_history = []
        self.current_method = None

        self.intents, self.sentences, self.user = intents, sentences, user

        self.model = GenericModel(intents=self.intents)
        self.model.train()

    def __str__(self):
        return self.name

    def get_intent(self, tag):
        ints = None

        for intent in self.intents:
            if intent.get('tag') == tag:
                ints = intent

        return ints

    def get_methods(self, intent, params):
        methods = []

        for method in intent.get('methods'):
            if method in self.handlers.mappings:
                self.current_method = method
                result = self.handlers.mappings[method](params)

                if result:
                    methods.append(result)

        self.current_method = None

        return methods

    def get_random_response(self, intent):
        responses = intent.get('responses')

        if responses:
            filtered_responses = responses

            if self.message_history:
                last_message = self.message_history[-1]
                filtered_responses = [response for response in responses if response != last_message]

            return random.choice(filtered_responses)

    def request(self, message):
        predictions = self.model.predict_class(message)
        result = self.model.process(predictions)

        response = self.get_random_response(result)
        methods = self.get_methods(result, self.model.clean_up_sentence(message))

        return_list = []

        for method in methods:
            return_list.append(method)

        if response:
            response = format_data(response, self.user)
            return_list.append(response)

        return return_list, result
