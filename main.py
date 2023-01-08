import json
from pathlib import Path

from chatbot import GenericAssistant
from handlers import mappings
from utils import speak, get_response, listen_for_wake_word

data: dict = {}

for file in Path('data').glob('*'):
    if file.suffix == '.json':
        with open(file) as f:
            data[file.stem] = json.loads(f.read())

config: dict
profile: dict
intents: dict

config, profile, intents = [data.get(key) for key in ['config', 'profile', 'intents']]
assistant: GenericAssistant = GenericAssistant(config, profile, intents, mappings)


def main():
    try:
        # Don't listen again:

        # first_time = True
        # while True:
        #     if first_time:
        #         first_time = False
        #         print("Listening for wake word...")
        #     detection = listen_for_wake_word(config.get('wake_word'))
        #
        #     if detection:
        #         message = get_response()
        #
        #         if not message:
        #             first_time = True
        #             continue
        #
        #         responses, result = assistant.request(message)
        #
        #         if responses and result:
        #             for response in responses:
        #                 if isinstance(response, tuple):
        #                   speak(response, send=True)
        #
        #         first_time = True

        # Normal:

        detection: bool = False
        first_time: bool = True

        while True:
            if not detection:
                if first_time:
                    print("Listening for the wake word...")
                    first_time = False
                detection = listen_for_wake_word(config.get('wake_word'))
            else:
                assistant.say('greetings')

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
