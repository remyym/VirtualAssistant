import os
import re
import sys
import tempfile
from datetime import datetime
from re import Pattern
from typing import Any

import speech_recognition as speech
from gtts import gTTS as textToSpeech, gTTS
from pydub import AudioSegment
from pydub.playback import play
from speech_recognition import AudioData

from num2words import num2words

recognizer = speech.Recognizer()


def resource_path(relative_path: str) -> str:
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)

    return os.path.join(os.path.abspath("."), relative_path)


def symbols_to_word(message) -> Any:
    if not message:
        return

    new_message: str = message

    for character in message.split():
        mappings = {
            '+': 'plus',
            '-': 'minus',
            '*': 'times',
            '/': 'divide',
            '^': 'to the power of'
        }

        if character.isdigit():
            new_message = new_message.replace(character, num2words(character))
        elif mappings.get(character):
            new_message = new_message.replace(character, mappings.get(character))

    return new_message


def remove_symbols(s: str) -> str:
    new_string = re.sub(r'[^a-zA-Z0-9 ]+', '', s)

    return new_string


def format_data(text: str, data: dict) -> str:
    pattern: Pattern = re.compile(r"{([^}]*)}")
    matches: list[Any] = pattern.findall(text)

    return_string: str = text

    for match in matches:
        name, key = match.split('.')

        holder = data.get(name)

        if not holder:
            return ''

        replacement = holder.get(key)

        if not replacement:
            continue

        return_string = pattern.sub(replacement, return_string)

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
        if not message:
            print("Invalid message")
            return

        if send:
            print(message)

        with tempfile.TemporaryFile(suffix='.mp3', delete=True) as fp:
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

            return transcript
    except (speech.UnknownValueError, speech.WaitTimeoutError):
        pass
    except speech.RequestError as e:
        print(f"Error requesting results: {e}")


def listen_for_wake_word(wake_word: str) -> bool:
    try:
        with speech.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio: AudioData = recognizer.listen(source, phrase_time_limit=3, timeout=60)

            text: str = recognizer.recognize_google(audio)

            if wake_word.lower() in text.lower():
                return True
    except (speech.WaitTimeoutError, speech.UnknownValueError):
        return False
    except speech.RequestError as e:
        print(f"Error requesting results: {e}")
        return False


def get_input(message: str = "") -> str:
    try:
        user_input: str = input(message)

        return user_input
    except UnicodeDecodeError:
        exit(1)


def get_response(keep_symbols: bool = True) -> str:
    message: str = symbols_to_word(listen())

    if isinstance(message, str):
        if keep_symbols:
            return message.lower()
        elif not keep_symbols:
            return remove_symbols(message.lower())
