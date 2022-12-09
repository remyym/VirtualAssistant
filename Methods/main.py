from datetime import datetime
from num2words import num2words

import calendar
import random


# Methods /
def time():
    now = datetime.now()

    return f"It's {now.strftime('%#I:%M %p')}."


def date():
    now = datetime.now()

    return f"It's {datetime.now().strftime('%A')}, {calendar.month_name[now.month]} {now.strftime('%#d')}, {now.year}."


def dice():
    word = str(num2words(random.randint(1, 6)))

    return f"It's {word.capitalize()}."
# \


Mappings = {'time': time, 'date': date, 'dice': dice}
Expressions = {'user': 'name'}
