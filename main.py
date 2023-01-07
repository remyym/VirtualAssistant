import json
from pathlib import Path

from chatbot import GenericAssistant

from utils import speak, get_response, listen_for_wake_word
import handlers

data = {}

for file in Path('data').glob('*'):
    if file.suffix == '.json':
        with open(file) as f:
            data[file.stem] = json.loads(f.read())

intents, sentences, config, user = [data.get(key).get(key) for key in ['intents', 'sentences', 'config', 'user']]

alexa = GenericAssistant(name=config.get('name'), intents=intents, sentences=sentences, user=user, handlers=handlers)


def main():
    try:
        detection = False

        while True:
            if not detection:
                detection = listen_for_wake_word(config.get('wake_word'))
            else:
                greetings = alexa.get_random_response(alexa.get_intent('greetings'))
                alexa.message_history.append(greetings)

                speak(greetings, True)

                while True:
                    message = get_response()

                    if not message:
                        detection = False
                        break

                    responses, result = alexa.request(message)

                    farewell = False

                    for response in responses:
                        if response and result:
                            speak(response, True)

                            if result.get('tag') == 'farewell':
                                farewell = True

                    if farewell:
                        detection = False
                        break
    except KeyboardInterrupt:
        exit(1)


if __name__ == '__main__':
    main()
