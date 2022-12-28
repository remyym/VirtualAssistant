import json
import calendar
import random
from datetime import datetime

import winapps
from num2words import num2words


# Methods /
def m_open(params):
    for word in params[0]:
        for item in winapps.search_installed(word):
            print(item)


# \


def modify(modifier_types, text):
    for modifier_type in modifier_types:
        modifier = modifier_type.split()

        if modifier[0] == 'capitalize':
            if len(modifier) <= 1:
                return text.capitalize()

            modifier.remove(0)

            return modifier.format(*text)


def respond(tag, params):
    with open('data.json') as f:
        data = json.loads(f.read())

    sentence = None

    for dictionary in data['sentences']:
        if dictionary.get('tag') == tag:
            sentence = dictionary

    if not sentence:
        return

    if sentence['modifiers']:
        params = modify(sentence['modifiers'], params)

    response = sentence['response'].format(*params)

    print(response)


mappings = {
    'time': lambda: f"It's {datetime.now().strftime('%#I:%M %p')}.",
    'date': lambda: f"It's {datetime.now().strftime('%A')}, {calendar.month_name[datetime.now().month]}"
                    f"{datetime.now().strftime('%#d')}, {datetime.now().year}.",
    'dice': lambda: f"It's {str(num2words(random.randint(1, 6)))}.",
    'open': m_open
}
