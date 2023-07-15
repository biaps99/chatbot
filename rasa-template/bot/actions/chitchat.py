from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionChitchat(Action):
    """Returns the chitchat utterance dependent on the patient intent"""

    def name(self) -> Text:
        return "action_chitchat"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List:

        intent = tracker.get_intent_of_latest_message()

        # retrieve the correct chitchat utterance dependent on the intent
        if intent in [
            "ask_whatismyname",
            "ask_builder",
            "ask_weather",
            "ask_howdoing",
            "ask_howold",
            "ask_languagesbot",
            "ask_restaurant",
            "ask_time",
            "ask_wherefrom",
            "ask_whoami",
            "handleinsult",
            "telljoke",
            "ask_name",
        ]:
            dispatcher.utter_message(response=f"utter_{intent}")

        return []
