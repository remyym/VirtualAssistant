import json
import calendar
import random
from datetime import datetime
from utils import get_response, speak

import winapps
from num2words import num2words

library = {
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
def m_open(params):
    for word in params[0]:
        for item in winapps.search_installed(word):
            print(item)


def rock_paper_scissors(_):
    speak("Rock, paper, or scissors?", True)

    game = library.get('games').get('rps')

    choices = game.get('choices')
    outcomes = game.get('outcomes')

    user_choice = get_response()

    for word in user_choice.split(' '):
        if word in choices:
            computer_choice = random.choice(choices)

            print(f"{'─' * 20}\nYou chose: {user_choice} \nI chose: {computer_choice}\n{'─' * 20}")

            if user_choice == computer_choice:
                result = "It's a tie."
            else:
                result = outcomes.get((user_choice, computer_choice), "I win!")

            if result:
                speak(result, True)

            break
# \


mappings = {
    'time': lambda params: f"It's {datetime.now().strftime('%#I:%M %p')}.",
    'date': lambda params: f"It's {datetime.now().strftime('%A')}, {calendar.month_name[datetime.now().month]},"
                           f" {datetime.now().strftime('%#d')}, {datetime.now().year}.",
    'dice': lambda params: f"It's {str(num2words(random.randint(1, 6)))}.",
    'open': m_open,
    'rock_paper_scissors': rock_paper_scissors
}
