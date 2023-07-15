from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import ReminderScheduled, ReminderCancelled, SlotSet, EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from datetime import datetime, timedelta
from dotenv import load_dotenv
from utils.medication import Medication
from utils.other_utils import get_last_bot_message
import inflect
import re

load_dotenv()
ordinal_generator = inflect.engine()
ordinal_index = []


class AskDaySchedules(Action):
    """Ask the times of day in which the patient will be reminded to take the medicine"""

    def name(self) -> Text:
        return "action_ask_schedule"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        last_bot_message = get_last_bot_message(tracker.events)

        if last_bot_message.startswith("Invalid"):

            for event in reversed(tracker.events):
                if event.get("event") == "bot" and (
                    event_text := event.get("text", "")
                ).startswith("Please, provide the time"):
                    dispatcher.utter_message(text=event_text)
                    break

            return []

        how_many_times = tracker.get_slot("how_many_times")
        permanent = tracker.get_slot("permanent")

        if how_many_times is not None and how_many_times > 0:
            measurement_index = ordinal_index.index(how_many_times) + 1
            time_ordinal = ordinal_generator.ordinal(ordinal_index[-measurement_index])
            dispatcher.utter_message(
                text=f"Please, provide the time of the {time_ordinal} dose in the format HH:mm."
            )

            return [SlotSet("how_many_times", how_many_times - 1)]

        elif permanent:
            # If the reminder is permanent, no need to ask for how many days the patient wants to receive the reminder.
            return [SlotSet("requested_slot", None)]

        dispatcher.utter_message(response="utter_ask_how_many_days")

        # This is just an hack to go forward to the next requested slot in the form by setting the value of the former requested slot to value different than 'None'.
        return [SlotSet("schedule", "schedule")]


class ValidateMedicationForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_medication_form"

    async def validate_medicine(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validates `medicine` slot value and sends it to Promptly"""

        patient_id = tracker.sender_id
        medicine = tracker.get_slot("medicine")
        response = Medication.set_medication(patient_id, str(medicine))

        if response == 200:
            return {"medicine": slot_value}

        return {"medicine": None}

    async def validate_dose(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validates `dose` slot value and sends it to Promptly"""

        dose_input_pattern = r"^[0-9]+ mg"

        if re.match(dose_input_pattern, slot_value):
            patient_id = tracker.sender_id
            data = {"medicine": tracker.get_slot("medicine"), "dose": slot_value}
            response = Medication.edit_medication(patient_id, data)

            if response == 200:
                return {"dose": slot_value}
        else:
            dispatcher.utter_message(text="Invalid answer.")

        return {"dose": None}

    async def validate_permanent(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validates `permanent` slot value and sends it to Promptly"""

        patient_id = tracker.sender_id
        permanent = "permanent" in slot_value.lower()
        data = {"medicine": tracker.get_slot("medicine"), "permanent": permanent}
        response = Medication.edit_medication(patient_id, data)

        if response == 200:
            return {"permanent": permanent}

        return {"permanent": None}

    async def validate_how_many_times(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validates `how_many_times` slot value and sends it to Promptly"""

        times_input_pattern = rf"^[1-9]+ time(s|)"

        if re.match(times_input_pattern, slot_value):
            number_times = [int(s) for s in slot_value.split() if s.isdigit()][0]
            global ordinal_index
            ordinal_index = list(range(1, number_times + 1))

            if number_times > 0:
                patient_id = tracker.sender_id
                data = {
                    "medicine": tracker.get_slot("medicine"),
                    "how_many_times": number_times,
                }
                response = Medication.edit_medication(patient_id, data)

                if response == 200:
                    return {"how_many_times": number_times}
        else:
            dispatcher.utter_message(text="Invalid answer.")

        return {"how_many_times": None}

    async def validate_schedule(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validates `schedule` slot value and sends it to Promptly"""

        try:
            datetime.strptime(slot_value, "%H:%M")
        except ValueError:
            dispatcher.utter_message(text="Invalid answer.")
        else:
            schedule_hours = slot_value.split(":")[0]
            schedule_minutes = slot_value.split(":")[1]
            current_date_time = datetime.now()
            schedule_date_time = current_date_time.replace(
                hour=int(schedule_hours), minute=int(schedule_minutes)
            )
            patient_id = tracker.sender_id
            date = schedule_date_time

            # If the time is not from today, set it for tomorrow.
            if schedule_date_time < current_date_time:
                date = schedule_date_time + timedelta(days=1)

            data = {
                "medicine": tracker.get_slot("medicine"),
                "schedule": date.strftime(f"%d/%m/%y, %H:%M"),
            }
            Medication.edit_medication(patient_id, data)

        # This is just an hack to allow the form to be active while all the schedule times are not answered yet.
        return {"schedule": None}

    async def validate_how_many_days(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validates `how_many_days` slot value and sends it to Promptly"""

        number_days_input_pattern = rf"^[0-9]+ day(s|)"

        if re.match(number_days_input_pattern, slot_value):
            number_days = [int(s) for s in slot_value.split() if s.isdigit()][0]
            patient_id = tracker.sender_id
            data = {
                "medicine": tracker.get_slot("medicine"),
                "how_many_days": number_days,
            }
            response = Medication.edit_medication(patient_id, data)

            if response == 200:
                return {"how_many_days": number_days}
        else:
            dispatcher.utter_message(text="Invalid answer.")

        return {"how_many_days": None}


class ActionSetAndShowReminderInfo(Action):
    """Create the reminders and reset the values from the medication form"""

    def name(self) -> Text:
        return "action_set_reminder_info"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        patient_id = tracker.sender_id
        medicine = tracker.get_slot("medicine")
        patient_medication = Medication.get_medication(patient_id, str(medicine))
        schedule_message = ""
        duration_message = f"This will occur permanently."
        result = [
            SlotSet(value, None)
            for value in [
                "medicine",
                "dose",
                "permanent",
                "schedule",
                "how_many_days",
                "how_many_times",
            ]
        ]

        if patient_medication is not None:
            for i, time in enumerate(patient_medication.schedule):
                entities = [
                    {"entity": "medicine", "value": medicine},
                    {"entity": "dose", "value": patient_medication.dose},
                    {"entity": "permanent", "value": patient_medication.permanent},
                ]
                time_ordinal = ordinal_generator.ordinal(i + 1)
                reminder = ReminderScheduled(
                    "show_medication_reminder",
                    trigger_date_time=datetime.strptime(time, f"%d/%m/%y, %H:%M"),
                    entities=entities,
                    name=f"remind_medication_{medicine}_{time}",
                    kill_on_user_message=False,
                )
                schedule_message += f"\t- {time_ordinal} dose: {time.split(', ')[1]}\n"
                result.append(reminder)

                if patient_medication.how_many_days is not None:
                    duration_message = f"This will occur for {patient_medication.how_many_days} days in a row."

                    for number_days in range(1, patient_medication.how_many_days):
                        trigger_date_time = datetime.strptime(
                            time, f"%d/%m/%y, %H:%M"
                        ) + timedelta(days=number_days)
                        trigger_date_time_string = trigger_date_time.strftime(
                            f"%d/%m/%y, %H:%M"
                        )
                        reminder = ReminderScheduled(
                            "show_medication_reminder",
                            trigger_date_time=trigger_date_time,
                            entities=entities,
                            name=f"remind_medication_{medicine}_{trigger_date_time_string}",
                            kill_on_user_message=False,
                        )
                        result.append(reminder)

            dispatcher.utter_message(
                f"I will remind you to take {patient_medication.dose} of {medicine} at:\n"
                + schedule_message
                + duration_message
            )

        return result


class ActionReactToMedicationReminder(Action):
    """Reminds the user to take the medication."""

    def name(self) -> Text:
        return "action_react_to_medication_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        patient_id = tracker.sender_id
        entities = tracker.latest_message.get("entities", [])

        if len(entities) > 0:
            medicine = [d for d in entities if d["entity"] == "medicine"][0]["value"]
            dose = [d for d in entities if d["entity"] == "dose"][0]["value"]
            permanent = [d for d in entities if d["entity"] == "permanent"][0]["value"]

            dispatcher.utter_message(f"Remember to take {dose} of {medicine}❗❗")

            # If the reminder is permanent, renew it for one more day.
            if permanent:
                patient_medication = Medication.get_medication(
                    patient_id, str(medicine)
                )

                if patient_medication is not None:
                    for time in patient_medication.schedule:
                        entities = [
                            {"entity": "medicine", "value": medicine},
                            {"entity": "dose", "value": dose},
                            {"entity": "permanent", "value": permanent},
                        ]
                        trigger_date_time = datetime.strptime(
                            time, f"%d/%m/%y, %H:%M"
                        ) + timedelta(days=1)
                        trigger_date_time_string = trigger_date_time.strftime(
                            f"%d/%m/%y, %H:%M"
                        )
                        reminder = ReminderScheduled(
                            "show_medication_reminder",
                            trigger_date_time=trigger_date_time,
                            entities=entities,
                            name=f"remind_medication_{medicine}_{trigger_date_time_string}",
                            kill_on_user_message=False,
                        )

                        return [reminder]

        return []


class ShowMedicationReminders(Action):
    """Show all the medication reminders from a given patient for him to choose which to cancel"""

    def name(self) -> Text:
        return "action_show_medication_reminders"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        patient_id = tracker.sender_id
        medicines = Medication.get_all_medicines(patient_id)
        buttons = []
        final_message = ""

        for medicine in medicines:
            schedule_message = ""
            duration = "permanent"

            if not medicine.permanent:
                duration = f"{medicine.how_many_days} days"

            initial_message = f"Medicine: {medicine.medicine}, dose: {medicine.dose}, duration: {duration}.\n"

            for i, time in enumerate(medicine.schedule):
                time_ordinal = ordinal_generator.ordinal(i + 1)
                schedule_message += f"\t- {time_ordinal} dose: {time.split(', ')[1]}\n"

            final_message += initial_message + schedule_message
            buttons.append(
                {
                    "title": f"Cancel {medicine.medicine} reminders.",
                    "payload": '/confirm_cancel_medication_reminder{"medicine":"'
                    + medicine.medicine
                    + '"}',
                }
            )

        buttons.append({"title": "No need, thanks.", "payload": "/refuse_help"})

        if final_message:
            dispatcher.utter_message("Your medication reminders 💊:\n" + final_message)
            dispatcher.utter_message(
                text="Which medicine reminders do you want to cancel ❌?",
                buttons=buttons,
                button_type="vertical",
            )
        else:
            dispatcher.utter_message("You have no medication reminders.")

        return []


class ForgetMedicationReminder(Action):
    """Cancels all the reminders for a given medicine."""

    def name(self) -> Text:
        return "action_forget_medication_reminder"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        if (
            tracker.get_intent_of_latest_message()
            == "confirm_cancel_medication_reminder"
        ):
            entities = tracker.latest_message.get("entities", [])

            if len(entities) > 0:
                medicine = [d for d in entities if d["entity"] == "medicine"][0][
                    "value"
                ]
                patient_id = tracker.sender_id
                reminders_for_that_medicine = []

                for event in reversed(tracker.events):
                    if (
                        event.get("event") == "reminder"
                        and event.get("intent") == "show_medication_reminder"
                    ):
                        medicines_of_reminder = [
                            d
                            for d in event.get("entities", [])
                            if d["entity"] == "medicine"
                        ]

                        if (
                            len(medicines_of_reminder) > 0
                            and medicines_of_reminder[0]["value"] == medicine
                        ):
                            reminders_for_that_medicine.append(event.get("name"))

                response = Medication.delete_medication(patient_id, medicine)

                if response == 200:
                    reminders_to_cancel = [
                        ReminderCancelled(reminder_name)
                        for reminder_name in reminders_for_that_medicine
                    ]
                    dispatcher.utter_message(
                        f"The reminders to take {medicine} were all cancelled ❌."
                    )

                    return reminders_to_cancel

        return []
