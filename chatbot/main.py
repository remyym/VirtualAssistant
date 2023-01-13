import random
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Any

from model import GenericModel
from utils import format_data, speak


class GenericAssistant:
    def __init__(self, config: dict, profile: dict, intents: dict, mappings: dict):
        # Set variables
        self.config = config
        self.profile = profile
        self.intents = intents
        self.mappings = mappings

        # Set data
        self.data = {'config': self.config, 'profile': self.profile}

        # Cache
        self.message_history = []
        self.current_method = None

        # Train
        self.model = GenericModel(intents=self.intents)
        self.model.train()

    def __str__(self) -> str:
        return self.config.get('name')

    def say(self, tag: str) -> None:
        greetings: str = self.get_random_response(self.get_intent(tag))
        self.message_history.append(greetings)

        speak(greetings, send=True)

    def get_intent(self, tag: str) -> Any:
        ints: Any = None

        for intent in self.intents:
            if intent.get('tag') == tag:
                ints = intent

        return ints

    def get_random_response(self, intent: dict) -> str:
        assert isinstance(intent, dict), "Invalid intent"

        responses: list = intent.get('responses')

        if responses:
            filtered_responses: list = responses

            if self.message_history:
                last_message: str = self.message_history[-1]
                filtered_responses = [response for response in responses if response != last_message]

            return random.choice(filtered_responses)

    def call_methods(self, intent: dict, params: list) -> list:
        methods: list = []

        for method in intent.get('methods'):
            if method in self.mappings:
                with ThreadPoolExecutor() as executor:
                    self.current_method = method

                    thread: Future = executor.submit(self.mappings[method], params)
                    result: object = thread.result()

                    if result:
                        methods.append(result)

        self.current_method = None

        return methods

    def request(self, message: str) -> (list, str):
        name: str = self.config.get('name')

        if name in message:
            message.replace(name, '')

        predictions: list = self.model.predict_class(message)
        result: Any = self.model.process(predictions)

        random_response: str = self.get_random_response(result)
        method_params: list[str] = self.model.clean_up_sentence(message)

        for word in method_params:
            for pattern in result.get('patterns'):
                if word in pattern and word in method_params:
                    method_params.remove(word)

        method_responses: list = self.call_methods(result, method_params)

        return_list: list = []

        for method_response in method_responses:
            return_list.append(method_response)

        if random_response:
            response: str = format_data(random_response, self.data)
            return_list.append(response)

        return return_list, result
