import os
import re
import string
import sys
import tempfile
from datetime import datetime

import speech_recognition as speech
from gtts import gTTS as textToSpeech, gTTS
from pydub import AudioSegment
from pydub.playback import play
from speech_recognition import AudioData

recognizer = speech.Recognizer()

recognizer.dynamic_energy_threshold = False
recognizer.energy_threshold = 400


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def remove_parentheses(s: str) -> str:
    return re.sub(r' *\(.*\) *', '', s)


def remove_symbols(s: str) -> str:
    s = re.sub(r'\W', '', s)
    translator = str.maketrans('', '', string.punctuation)

    return s.translate(translator)


# def modify(modifier_types: object, text: object) -> object:
#     for modifier_type in modifier_types:
#         modifier = modifier_type.split()
#
#         if modifier[0] == 'capitalize':
#             if len(modifier) <= 1:
#                 return text.capitalize()
#
#             modifier.remove(0)
#
#             return modifier.format(*text)


def format_data(text: str, data: dict) -> str:
    pattern = re.compile(r"{([^}]*)}")
    matches = pattern.findall(text)

    return_string = text

    for match in matches:
        name, key = match.split('.')

        holder = data.get(name)
        replacement = holder.get(key)

        if not replacement:
            continue

        return_string = return_string.replace("{" + match + "}", replacement)

    return return_string


def get_time_of_day(dt: datetime) -> str:
    hour: int = dt.hour

    if hour < 6:
        return "night"
    elif hour < 12:
        return "morning"
    elif hour < 18:
        return "afternoon"
    else:
        return "evening"


def speak(*messages: str, send: bool = False) -> None:
    if len(messages) == 1 and isinstance(messages[0], tuple):
        messages = messages[0]

    for message in messages:
        assert message, "Invalid message"

        if send:
            print(message)

        with tempfile.TemporaryFile(suffix='.mp3', delete=False) as fp:
            audio: gTTS = textToSpeech(text=message, lang="en")

            audio.write_to_fp(fp)
            fp.seek(0)

            sound: AudioSegment = AudioSegment.from_mp3(fp)
            play(sound)


def listen() -> str | bool:
    try:
        with speech.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)

            print("Listening...")

            audio: AudioData = recognizer.listen(source, phrase_time_limit=8, timeout=3)
            transcript: str = recognizer.recognize_google(audio).replace('-', ' ')

            print(f"I heard \"{transcript}\".")

            sound: AudioSegment = AudioSegment.from_mp3(resource_path('resources/sound/finish.mp3'))
            play(sound)

            return transcript
    except (speech.UnknownValueError, speech.WaitTimeoutError):
        return False
    except speech.RequestError as e:
        print("Error requesting results: {0}".format(e))
        return False


def listen_for_wake_word(wake_word: str) -> bool:
    try:
        with speech.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio: AudioData = recognizer.listen(source, phrase_time_limit=3, timeout=60)

            text: str = recognizer.recognize_google(audio)

            if wake_word.lower() in text.lower():
                sound: AudioSegment = AudioSegment.from_mp3(resource_path('resources/sound/start.mp3'))
                play(sound)

                return True
    except (speech.WaitTimeoutError, speech.UnknownValueError):
        return False
    except speech.RequestError as e:
        print("Error requesting results: {0}".format(e))
        return False


def get_input(message: str = "") -> str:
    try:
        user_input: str = input(message)

        return user_input
    except UnicodeDecodeError:
        exit(1)


def get_response(keep_symbols: bool = True) -> str:
    message: str = listen()

    if isinstance(message, str):
        if keep_symbols:
            return message.lower()
        elif not keep_symbols:
            return remove_symbols(message.lower())
