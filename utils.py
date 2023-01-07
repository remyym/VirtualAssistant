import re
import string
import tempfile

import speech_recognition as speech
from gtts import gTTS as textToSpeech
from pydub import AudioSegment
from pydub.playback import play

recognizer = speech.Recognizer()

recognizer.dynamic_energy_threshold = False
recognizer.energy_threshold = 400


def remove_symbols(s):
    s = re.sub(r'\W', '', s)
    translator = str.maketrans('', '', string.punctuation)
    return s.translate(translator)


def modify(modifier_types, text):
    for modifier_type in modifier_types:
        modifier = modifier_type.split()

        if modifier[0] == 'capitalize':
            if len(modifier) <= 1:
                return text.capitalize()

            modifier.remove(0)

            return modifier.format(*text)


def format_data(text, data):
    pattern = re.compile(r"{([^}]*)}")
    matches = pattern.findall(text)

    return_string = text

    for match in matches:
        replacement = data.get(match)

        if not replacement:
            continue

        return_string = return_string.replace("{" + match + "}", replacement)

    return return_string


def speak(message, send=False):
    if send:
        print(message)

    with tempfile.TemporaryFile(suffix='.mp3', delete=False) as fp:
        audio = textToSpeech(text=message, lang="en")

        audio.write_to_fp(fp)
        fp.seek(0)

        sound = AudioSegment.from_mp3(fp)
        play(sound)


def listen():
    try:
        with speech.Microphone() as source:
            print("Listening...")

            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio = recognizer.listen(source, timeout=10)

            transcript = recognizer.recognize_google(audio).replace('-', ' ')

            print(f"I heard \"{transcript}\".")

            return transcript
    except (speech.UnknownValueError, speech.WaitTimeoutError):
        return False
    except speech.RequestError as e:
        print("Error requesting results: {0}".format(e))
        return False


def listen_for_wake_word(wake_word):
    try:
        with speech.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio = recognizer.listen(source, phrase_time_limit=3)

            text = recognizer.recognize_google(audio)

            if wake_word.lower() in text.lower():
                return True
    except (speech.WaitTimeoutError, speech.UnknownValueError):
        return False
    except speech.RequestError as e:
        print("Error requesting results: {0}".format(e))
        return False


def get_input(message=""):
    try:
        user_input = input(message)

        return user_input
    except UnicodeDecodeError:
        exit(1)


def get_response(keep_symbols=True):
    message = listen()

    if message and type(message) is str:
        if keep_symbols:
            return message.lower()
        elif not keep_symbols:
            return remove_symbols(message.lower())
