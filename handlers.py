import calendar
import json
import random
import subprocess
from datetime import datetime
from typing import Any

import requests
import wikipedia
from num2words import num2words
from requests import Response

from utils import remove_parentheses, get_time_of_day, get_response, speak

library: dict = {
    'games': {
        'rps': {
            'choices': ['rock', 'paper', 'scissors'],
            'outcomes': {
                ('rock', 'scissors'): "You win!",
                ('paper', 'rock'): "You win!",
                ('scissors', 'paper'): "You win!",
            }
        }
    }
}


# Methods /
def open_app(params: list) -> None:
    # if params:
    #     for word in params[0]:
    #         for item in winapps.search_installed(word):
    #             print(item)

    subprocess.run(['start', f'{params[0]}.exe'], shell=True)


def rps(_: Any | None) -> None | str:
    speak("Rock, paper, or scissors?", send=True)

    game: dict = library.get('games').get('rps')

    choices: list = game.get('choices')
    outcomes: dict = game.get('outcomes')

    user_choice: str = get_response()

    if user_choice:
        for word in user_choice.split(' '):
            if word in choices:
                computer_choice: str = random.choice(choices)

                print(f"{'─' * 20}\nYou chose: {word} \nI chose: {computer_choice}\n{'─' * 20}")

                if word == computer_choice:
                    result: str = "It's a tie."
                else:
                    result: str = outcomes.get((word, computer_choice), "I win!")

                if result:
                    speak(result, send=True)

                return

    return 'Please choose either "rock, "paper", or "scissors".'


def search_wikipedia(params: str) -> str:
    try:
        return remove_parentheses(wikipedia.summary(params, sentences=1))
    except wikipedia.DisambiguationError:
        return "Please be more specific."


def joke(_: Any | None) -> object:
    url: str = "https://v2.jokeapi.dev/joke/Any?safe-mode"
    params: dict = {'blacklistFlags': 'nsfw,religious,political,racist,sexist,explicit', 'type': 'twopart'}

    response: Response = requests.request("GET", url, params=params)
    text: dict = json.loads(response.text)

    if response.status_code == 200 and not text.get('error'):
        return text.get('setup'), text.get('delivery')
    else:
        speak("Jokes are unavailable at this time. Please try again later.", send=True)
# \


mappings = {
    'time': lambda params: f"It's {datetime.now().strftime('%#I:%M %p')}.",
    'time_of_day': lambda params: f"Good {get_time_of_day(datetime.now())}!",
    'date': lambda params: f"It's {datetime.now().strftime('%A')}, {calendar.month_name[datetime.now().month]},"
                           f" {datetime.now().strftime('%#d')}, {datetime.now().year}.",
    'dice': lambda params: f"It's {str(num2words(random.randint(1, 6)))}.",
    'open': open_app,
    'wikipedia': search_wikipedia,
    'rps': rps,
    'joke': joke
}
