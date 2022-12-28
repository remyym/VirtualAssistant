from util import speak


def main(text=""):
    message = None

    try:
        message = input(text)
    except UnicodeDecodeError:
        exit(1)

    if not message:
        print("Listening...")

        message = speak()
        print(f"I heard \"{message}\".")

    return message
