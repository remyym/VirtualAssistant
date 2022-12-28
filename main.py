from chatbot import GenericAssistant

from util import speak, handle_input
import handlers

alexa = GenericAssistant(name='Alexa', data='data.json', handlers=handlers)

if __name__ == '__main__':
    greetings = alexa.get_response('greetings')
    speak(greetings, True)

    try:
        while True:
            message = handle_input()

            if not message:
                continue

            response, result = alexa.request(message)
            speak(response, True)

            if result.get('tag') == 'farewell':
                exit()
    except KeyboardInterrupt:
        exit(1)
