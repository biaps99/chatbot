from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionHelp(Action):
    """Returns the actions that can be performed by the chatbot"""

    def name(self) -> Text:
        return "action_help"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List:

        actions = [
            {"title": "Show Daily Goals", "payload": "/check_progress"},
            {"title": "Show Educational Articles", "payload": "/view_article_types"},
            {
                "title": "Talk about Blood Pressure Check",
                "payload": '/ask_about_blood_pressure{"topic":"'
                + "blood pressure"
                + '"}',
            },
            {
                "title": "Talk about the Importance of Physical Exercise",
                "payload": '/ask_about_exercise{"topic":"' + "physical exercise" + '"}',
            },
            {
                "title": "Discuss the Importance of a Healthy Diet",
                "payload": '/ask_about_nutrition{"topic":"' + "diet" + '"}',
            },
            {
                "title": "Explain the Importance of Glucose Monitoring",
                "payload": '/ask_about_glucose{"topic":"' + "glucose levels" + '"}',
            },
            {"title": "Show Health Questionnaire", "payload": "/show_wellness_check"},
            {
                "title": "Update Blood Pressure status",
                "payload": '/blood_update{"update":"' + "blood pressure" + '"}',
            },
            {
                "title": "Update Glucose status",
                "payload": '/glucose_update{"update":"' + "glucose" + '"}',
            },
            {
                "title": "Update Weight status",
                "payload": '/weight_update{"update":"' + "weight" + '"}',
            },
            {"title": "Medication reminders", "payload": "/reminders"},
            {"title": "Symptoms Update", "payload": "/symptoms_check"},
        ]

        dispatcher.utter_message(
            text="Can I help you in the following topics?",
            buttons=actions,
            button_type="vertical",
        )

        return []
