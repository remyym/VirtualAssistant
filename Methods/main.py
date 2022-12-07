from datetime import datetime
import calendar


def time():
    now = datetime.now()
    return f"It's {now.strftime('%#I:%M %p')}."


def date():
    now = datetime.now()

    return f"It's {datetime.now().strftime('%A')}, {calendar.month_name[now.month]} {now.strftime('%#d')}, {now.year}."


Mappings = {'time': time, 'date': date}
