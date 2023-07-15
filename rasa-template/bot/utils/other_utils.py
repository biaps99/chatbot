from typing import List, Dict, Any, Text


def greet_according_to_time(time: int):
    """Returns a greet message according to the given time of the day"""

    if 4 <= time <= 12:
        greet_message = "Good morning!"
    elif 12 < time <= 18:
        greet_message = "Good afternoon!"
    elif 18 < time <= 20:
        greet_message = "Good evening!"
    else:
        greet_message = "Good night!"

    return greet_message


def get_last_bot_message(events: List[Dict[Text, Any]]):
    """Returns the last bot message according to Rasa's tracker events"""
    last_bot_message = ""

    for event in reversed(events):
        if event.get("event") == "bot":
            last_bot_message = event.get("text", "")
            break

    return last_bot_message
