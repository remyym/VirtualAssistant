import json

from chatbot import GenericAssistant
from handlers import mappings
from utils import speak, get_response, listen_for_wake_word, resource_path

with open(resource_path('resources/data/config.json')) as f:
    config = json.loads(f.read())

with open(resource_path('resources/data/profile.json')) as f:
    profile = json.loads(f.read())

with open(resource_path('resources/data/intents.json')) as f:
    intents = json.loads(f.read())

assistant: GenericAssistant = GenericAssistant(config, profile, intents, mappings)


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
                    message: str = get_response()

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
    except KeyboardInterrupt:
        exit(1)


if __name__ == '__main__':
    main()
