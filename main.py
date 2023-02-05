import json
import os

from chatbot import GenericAssistant
from handlers import mappings
from utils import speak, get_response, listen_for_wake_word, resource_path

data: {dict} = {}

with open(resource_path('resources\\intents.json')) as file:
    intents = json.load(file)

for filename in os.listdir(resource_path('resources\\data')):
    if filename.endswith('.json'):
        with open(resource_path(os.path.join('resources\\data', filename))) as json_file:
            json_data: dict = json.load(json_file)
            data[filename.removesuffix('.json')] = json_data

config: dict = data.get('config')
name: str = config.get('name') or 'Alexa'

assistant: GenericAssistant = GenericAssistant(name, data, intents, mappings)


def main():
    try:
        # Normal voice detection:

        detection: bool = False
        first_time: bool = True

        while True:
            if not detection:
                if first_time:
                    print("Listening for the wake word...")
                    first_time = False
                detection = listen_for_wake_word(config.get('wake_word'))
            else:
                while detection:
                    message: str = get_response(keep_symbols=False)

                    if not message:
                        detection, first_time = False, True
                        break

                    responses: list
                    result: dict

                    responses, result = assistant.request(message)

                    if responses and result:
                        for response in responses:
                            speak(response, send=True)

                        if result.get('tag') == 'farewell':
                            detection, first_time = False, True

        # Input

        # while True:
        #     message: str = get_response()
        #
        #     if not message:
        #         continue
        #
        #     responses: list
        #     result: dict
        #
        #     responses, result = assistant.request(message)
        #
        #     if responses and result:
        #         for response in responses:
        #             speak(response, send=True)
    except KeyboardInterrupt:
        exit(1)


if __name__ == '__main__':
    main()
