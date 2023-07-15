from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import (
    ReminderScheduled,
    ReminderCancelled,
    SlotSet,
    EventType,
    FollowupAction,
)
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from datetime import datetime, timedelta
from utils.question import Question
from utils.answer import Answer
from utils.goals import Goals
from utils.other_utils import greet_according_to_time, get_last_bot_message
from dotenv import load_dotenv
import os
import inflect
import re

load_dotenv()
ordinal_generator = inflect.engine()
ordinal_index = []


class ActionShowDailyGoals(Action):
    """Shows the progress of a patient daily goals"""

    def name(self) -> Text:
        return "action_show_daily_goals"

    def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        user_id = tracker.sender_id
        user_info = Goals.retrieve_status_of_patient_daily_goals(user_id)
        tasks_todo = "\n"
        tasks_done = "\n"
        tasks_completed = 0
        for task in user_info:
            if user_info[task]["status"] == "True":
                tasks_completed += 1

                if task == "Weigh in":
                    details = f"""
                    - value: {user_info[task]['value']} kg
                    - nº measurements: {user_info[task]['number measurements']}\n"""

                elif task == "Read educational articles":
                    details = f"""
                    - nº: {user_info[task]['nº']}\n"""

                elif task == "Check blood pressure":
                    details = f"""
                    - systolic value: {user_info[task]['systolic']['value']} mm/Hg
                    - diastolic value: {user_info[task]['diastolic']['value']} mm/Hg
                    - nº measurements: {user_info[task]['number measurements']}\n"""
                elif task == "Measure glucose level":
                    details = f"""
                    - value: {user_info[task]['value']} mg/dl
                    - nº measurements: {user_info[task]['number measurements']}\n"""
                else:
                    details = "\n"

                tasks_done += f"✅ {task}{details}"
            else:
                tasks_todo += "❌ {}\n".format(task)

        total_tasks = len(user_info.keys())

        percentage = (tasks_completed / total_tasks) * 100

        text = f"Let's go, you can do better than {round(percentage,1)} %!\n"
        if percentage >= 50 and percentage < 100:
            text = f"Come on, you have {round(percentage,1)} % of the job done 💪!\n"
        elif percentage == 100:
            text = f"You rock, 💯 % of the job done 👏!\n"

        intent = tracker.get_intent_of_latest_message()
        greet_message = ""

        if intent == "greet":
            time = int(datetime.now().strftime("%H"))
            greet_message = greet_according_to_time(time)

        message = f"""{greet_message} Here are your Daily Goals 📝\n
                To do:
                    {tasks_todo} \nDone:\n {tasks_done}
                {text}"""

        dispatcher.utter_message(message)

        return []


class ActionTryToHelp(Action):
    """Try to help patient in his remaining daily tasks"""

    def name(self) -> Text:
        return "action_try_to_help"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        user_id = tracker.sender_id
        user_info = Goals.retrieve_status_of_patient_daily_goals(user_id)
        buttons = []

        for task in user_info:
            if user_info[task]["status"] == "False":
                if task.startswith("Weigh"):
                    buttons.append(
                        {
                            "title": "Explain the Importance of a Healthy Weight",
                            "payload": '/ask_about_weight{"topic":"' + "weight" + '"}',
                        }
                    )
                if task.startswith("Read"):
                    buttons.append(
                        {
                            "title": "Show Educational Articles",
                            "payload": "/view_article_types",
                        }
                    )
                if task.startswith("Check"):
                    buttons.append(
                        {
                            "title": "Explain the Importance of Blood Pressure Check",
                            "payload": '/ask_about_blood_pressure{"topic":"'
                            + "blood pressure"
                            + '"}',
                        }
                    )
                if task.startswith("Practise"):
                    buttons.append(
                        {
                            "title": "Talk about the Importance of Physical Exercise",
                            "payload": '/ask_about_exercise{"topic":"'
                            + "physical exercise"
                            + '"}',
                        }
                    )
                if task.startswith("Comply"):
                    buttons.append(
                        {
                            "title": "Discuss the Importance of a Healthy Diet",
                            "payload": '/ask_about_nutrition{"topic":"' + "diet" + '"}',
                        }
                    )
                if task.startswith("Measure"):
                    buttons.append(
                        {
                            "title": "Explain the Importance of Glucose Monitoring",
                            "payload": '/ask_about_glucose{"topic":"'
                            + "glucose levels"
                            + '"}',
                        }
                    )

        buttons.append({"title": "No need, thanks", "payload": "/refuse_help"})

        dispatcher.utter_message(
            text="How can I help you achieve your remaining goals?",
            buttons=buttons,
            button_type="vertical",
        )

        return []


class AskHealthFormAnswerAction(Action):
    """Ask the next question to a patient"""

    def name(self) -> Text:
        return "action_ask_health_form_answer"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        intent_of_last_user_message = tracker.get_intent_of_latest_message()

        if intent_of_last_user_message == "confirm_stop":
            # if the user confirms he wants to stop the questionnaire, the form is deactivated.
            return [SlotSet("requested_slot", None)]
        elif intent_of_last_user_message == "stop" or str(
            intent_of_last_user_message
        ).startswith("ask_"):
            return []

        buttons = None
        next_question = None
        user_id = tracker.sender_id
        next_question = Question.get_next_question(user_id)

        if next_question is not None:
            if next_question.repeated:
                dispatcher.utter_message(
                    text="C'mon don't try to cheat. Please, provide a valid answer."
                )

            if next_question.title:
                if next_question.button_choice:
                    buttons = []

                    for value in next_question.possible_values:
                        buttons.append(
                            {
                                "title": value.capitalize(),
                                "payload": '/answer_wellness_check{"health_form_answer":"'
                                + value
                                + '"}',
                            }
                        )

                dispatcher.utter_message(text=next_question.title, buttons=buttons)
                return []
            else:
                return [SlotSet("requested_slot", None)]

        return []


class ValidateHealthForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_health_form"

    async def extract_health_form_answer(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        """Extracts the response from the patient's message and maps it to the `health_form_answer` slot"""

        entities = tracker.latest_message.get("entities", [])
        intent_of_last_user_message = tracker.get_intent_of_latest_message()
        text_of_last_user_message = ""

        if len(entities) > 0:
            entity = [d for d in entities if d["entity"] == "health_form_answer"][0]
            text_of_last_user_message = entity["value"]
        elif str(intent_of_last_user_message).startswith("ask_"):
            text_of_last_user_message = intent_of_last_user_message
        elif intent_of_last_user_message == "stop":
            text_of_last_user_message = "stop"

        last_bot_question = get_last_bot_message(tracker.events)

        return {
            "health_form_answer": f"{last_bot_question}:{text_of_last_user_message}"
        }

    async def validate_health_form_answer(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validates `health_form_answer` slot value and sends the patient's answer to Promptly"""

        patient_id = tracker.sender_id
        info = slot_value.split(":")
        question = info[0]
        answer = info[1]

        if answer.startswith("ask_"):
            dispatcher.utter_message(response="utter_" + answer)
            dispatcher.utter_message(response="utter_stop")
        elif answer == "stop":
            dispatcher.utter_message(response="utter_stop")
        else:
            data = {"question_title": question, "patient_answer": answer}
            Answer.set_patient_answer(patient_id, data)

        # This is just an hack to allow the form to be active while all the questions are not answered yet.
        return {"health_form_answer": None}


class ActionShowAnswers(Action):
    """Show the patient's answers in the end of the questionnaire and sets alarming metrics, if existing"""

    def name(self) -> Text:
        return "action_show_answers"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        patient_id = tracker.sender_id
        answers = Answer.get_patient_answers(patient_id)
        response = ""
        alarming_metrics = []
        actions = []

        for answer in answers:
            response += "{} : {}\n".format(
                answer.question_title, (answer.patient_answer).capitalize()
            )
            if answer.alarming:
                alarming_metrics.append(answer.question_topic)

        dispatcher.utter_message(text="Your answers:\n" + response)

        if tracker.get_intent_of_latest_message() == "confirm_stop":
            time_gap = os.environ["TIME_GAP"]
            dispatcher.utter_message(
                f"I will remind you to continue the questionnaire later."
            )
            date = datetime.now() + timedelta(seconds=int(time_gap) + 10)
            reminder = ReminderScheduled(
                "show_wellness_check",
                trigger_date_time=date,
                entities=None,
                name="remind_questionnaire",
                kill_on_user_message=False,
            )
            actions.append(reminder)
        else:
            dispatcher.utter_message(
                "Nicely done, you have your information up to date. No need for reminders 😜"
            )
            actions.append(ReminderCancelled("remind_questionnaire"))

        if len(alarming_metrics) > 0:
            actions.extend(
                [
                    SlotSet("alarming_metrics", alarming_metrics),
                    FollowupAction("action_show_article_for_alarming_metrics"),
                ]
            )

        return actions


class ActionSetQuestionnaireReminder(Action):
    """Schedules a reminder to perform a health daily questionnaire"""

    def name(self) -> Text:
        return "action_set_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        time_gap = os.environ["TIME_GAP"]
        dispatcher.utter_message(
            f"I will remind you to answer the questionnaire in {time_gap} seconds."
        )
        date = datetime.now() + timedelta(seconds=int(time_gap))
        reminder = ReminderScheduled(
            "show_wellness_check",
            trigger_date_time=date,
            entities=None,
            name="remind_questionnaire",
            kill_on_user_message=False,
        )

        return [reminder]


class AskForMeasurementAction(Action):
    def name(self) -> Text:
        return "action_ask_measurement"

    def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        measurement = tracker.get_slot("update")
        last_bot_message = get_last_bot_message(tracker.events)

        if last_bot_message.startswith("Invalid"):

            for event in reversed(tracker.events):
                if event.get("event") == "bot" and (
                    event_text := event.get("text", "")
                ).startswith("Introduce the"):
                    dispatcher.utter_message(text=event_text)
                    break

            return []

        number_of_measurements = tracker.get_slot("number_of_measurements")
        time_ordinal = ""

        if number_of_measurements is not None and number_of_measurements > 0:
            measurement_index = ordinal_index.index(number_of_measurements) + 1
            time_ordinal = ordinal_generator.ordinal(ordinal_index[-measurement_index])
            message_text = f"Introduce the value of your {time_ordinal} {measurement} measurement of the day in the format 'X kg'."

            if "pressure" in str(measurement):
                if "diastolic" not in str(last_bot_message):
                    message_text = f"Introduce the diastolic (lowest) value of your {time_ordinal} {measurement} measurement of the day in the format 'X mm/Hg'."
                    dispatcher.utter_message(text=message_text)

                    return []

                message_text = f"Introduce the systolic (highest) value of your {time_ordinal} {measurement} measurement of the day in the format 'X mm/Hg'."

            elif measurement == "glucose":
                message_text = f"Introduce the value of your {time_ordinal} {measurement} measurement of the day in the format 'X mg/dl'."

            dispatcher.utter_message(text=message_text)

            return [SlotSet("number_of_measurements", number_of_measurements - 1)]

        return [
            SlotSet("requested_slot", None),
            SlotSet("number_of_measurements", None),
        ]


class ValidateMeasurementForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_measurementform"

    async def validate_number_of_measurements(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validates `number_of_measurements` slot value and sets a list of ordinal values to ask for the 'nth' measurement"""

        input_pattern = rf"^[1-9]+ measurement(s|)"

        if re.match(input_pattern, slot_value):
            number_of_measurements = [
                int(s) for s in slot_value.split() if s.isdigit()
            ][0]
            global ordinal_index
            ordinal_index = list(range(1, number_of_measurements + 1))

            return {"number_of_measurements": number_of_measurements}
        else:
            dispatcher.utter_message(text="Invalid answer.")

        return {"number_of_measurements": None}

    async def validate_measurement(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validates `measurement` slot value and sends the patient's answer to Promptly"""

        measurement = tracker.get_slot("update")
        input_pattern = rf"^[0-9]+ mm/Hg"

        if "glucose" in str(measurement) or "sugar" in str(measurement):
            input_pattern = rf"^[0-9]+ mg/dl"
        elif "weight" in str(measurement):
            input_pattern = rf"^[0-9]+ kg"

        if re.match(input_pattern, slot_value):
            metric_value = [int(s) for s in str(slot_value).split() if s.isdigit()][0]
            patient_id = tracker.sender_id
            blood_pressure_type = ""
            tasks = {
                "weight": "Weigh in",
                "glucose": "Measure glucose level",
                "blood pressure": "Check blood pressure",
            }

            if "pressure" in str(measurement):
                blood_pressure_type = "systolic"
                last_bot_message = get_last_bot_message(tracker.events)

                if "diastolic" in last_bot_message:
                    blood_pressure_type = "diastolic"

            response = Goals.edit_status_of_patient_daily_goals(
                patient_id,
                {
                    "metric": tasks[str(measurement)],
                    "value": metric_value,
                    "type": blood_pressure_type,
                },
            )

            if response == 200:
                dispatcher.utter_message(
                    text=f"Your {blood_pressure_type} {measurement} value, {slot_value}, was registered."
                )
        else:
            dispatcher.utter_message(text="Invalid answer.")

        return {"measurement": None}
