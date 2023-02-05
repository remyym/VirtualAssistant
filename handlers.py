import calendar
import json
import random
from datetime import datetime
from typing import Any

import requests
from num2words import num2words
from requests import Response

from utils import get_time_of_day, get_response, speak

wolfram_appid: str = '59E9J5-XJ72RJUHP9'

oxford_appid: str = '1eae0a35'
oxford_appkey: str = '3bba5e41aa389aebbcaf9adca078cbb4'

language: str = 'en-us'


# Methods /
def wolfram(params: list) -> str:
    """
    Get short answer using WolframAlpha

    :type params: list
    """

    query: str = ' '.join(map(str, params))

    url: str = f'http://api.wolframalpha.com/v1/result?appid={wolfram_appid}&i={query}'
    response: Response = requests.get(url)

    if response.status_code == 200:
        return str(response.text)
    else:
        return "Please be more specific."


def define(params: list) -> str:
    """
    Get definition of word using the Oxford Dictionary

    :param params: list
    :return: str
    """

    word_id: str = params[1].lower()

    url = f'https://od-api.oxforddictionaries.com/api/v2/entries/{language}/{word_id}'

    headers: dict = {
        'app_id': oxford_appid,
        'app_key': oxford_appkey
    }

    response: Response = requests.get(url, headers=headers)

    if response.status_code == 200:
        text: dict = json.loads(response.text)

        results: list = text.get('results')

        entries: list = results[0].get('lexicalEntries')[0].get('entries')
        definitions: list = entries[0].get('senses')[0].get('definitions')

        if definitions:
            return definitions[0]
        else:
            return "Invalid word"


def joke(_: Any) -> tuple:
    """
    Tells a joke

    :param _: Any
    :return: tuple
    """

    url: str = 'https://v2.jokeapi.dev/joke/Any?safe-mode'
    params: dict = {'type': 'twopart'}

    response: Response = requests.get(url, params=params)
    text: dict = json.loads(response.text)

    if response.status_code == 200 and not text.get('error'):
        return text.get('setup'), text.get('delivery')
    else:
        speak("Jokes are unavailable at this time. Please try again later.", send=True)
# \


def rock_paper_scissors(_: Any) -> Any:
    """
    Play rock paper scissors

    :param _: Any
    :return: str
    """

    speak("Rock, paper, or scissors?", send=True)

    choices: list = ['rock', 'paper', 'scissors']
    outcomes: dict = {
        ('rock', 'scissors'): "You win!",
        ('paper', 'rock'): "You win!",
        ('scissors', 'paper'): "You win!",
    }

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


mappings: dict = {
    'time': lambda params: f"It's {datetime.now().strftime('%#I:%M %p')}.",
    'time_of_day': lambda params: f"Good {get_time_of_day(datetime.now())}!",
    'date': lambda params: f"It's {datetime.now().strftime('%A')}, {calendar.month_name[datetime.now().month]},"
                           f" {datetime.now().strftime('%#d')}, {datetime.now().year}.",
    'dice': lambda params: f"It's {str(num2words(random.randint(1, 6)))}.",
    'joke': joke,
    'wolfram_query': wolfram,
    'define': define,
    'rock_paper_scissors': rock_paper_scissors
}
