from typing import Any, Text, Dict, List, Union
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from dotenv import load_dotenv
from utils.symptoms import Symptoms
import inflect
import re


load_dotenv()
ordinal_generator = inflect.engine()
ordinal_index = []


class AskForSymptomsName(Action):
    """Ask the name of the symptom or symptoms like "tiredness"/"increased thirst"""

    def name(self) -> Text:
        return "action_ask_symptom"

    def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        buttons = []
        number_of_symptoms = tracker.get_slot("number_of_symptoms")
        time_ordinal = ""

        if number_of_symptoms and number_of_symptoms > 0:
            symptoms_index = ordinal_index.index(number_of_symptoms) + 1
            time_ordinal = ordinal_generator.ordinal(ordinal_index[-symptoms_index])
            message_text = f"What is the name of the {time_ordinal} symptom you are experiencing? Choose one or write in the format: 'I feel X'."
            buttons = [
                {
                    "payload": '/answer_symptom{"symptom": "Increased Thirst"}',
                    "title": "Increased Thirst",
                },
                {
                    "payload": '/answer_symptom{"symptom": "Fatigue/Tiredness"}',
                    "title": "Fatigue/Tiredness",
                },
                {
                    "payload": '/answer_symptom{"symptom": "Unexpected Weight Loss"}',
                    "title": "Unexpected Weight loss",
                },
                {
                    "payload": '/answer_symptom{"symptom": "Increased Hunger"}',
                    "title": "Increased Hunger",
                },
                {
                    "payload": '/answer_symptom{"symptom": "Increased Urination"}',
                    "title": "Increased Urination",
                },
                {
                    "payload": '/answer_symptom{"symptom": "Blurred Vision"}',
                    "title": "Blurred Vision",
                },
            ]
            dispatcher.utter_message(
                text=message_text,
                buttons=buttons,
                button_type="vertical",
            )
            return [SlotSet("number_of_symptoms", number_of_symptoms - 1)]

        return [
            SlotSet("number_of_symptoms", None),
        ]


class AskForSymptomsIntensity(Action):
    """Ask the intensity of the symptom in the scale from 1 to 10"""

    def name(self) -> Text:
        return "action_ask_intensity"

    def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        symptom = tracker.get_slot("symptom")
        message_text = f"On a scale from 1 (lowest intensity) to 10 (highest intensity), how would you describe your '{symptom}' symptom? Write in the format 'X intensity'."

        dispatcher.utter_message(text=message_text)
        return []


class AskForDurationAction(Action):
    """Ask the duration of the symptom in minutes, hours or days"""

    def name(self) -> Text:
        return "action_ask_duration"

    def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        symptom = tracker.get_slot("symptom")
        message_text = f"How long have you been experiencing '{symptom}'? Write in the format 'X minutes/hours/days'."

        dispatcher.utter_message(text=message_text)
        return []


class ValidateSymptomForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_symptoms_form"

    async def validate_number_of_symptoms(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validates `number_of_symptoms` slot value and sets a list of ordinal values to ask for the 'nth' symptoms"""

        input_pattern = rf"^[1-9]+ symptom(s|)"

        if re.match(input_pattern, slot_value):
            number_of_symptoms = [int(s) for s in slot_value.split() if s.isdigit()][0]
            global ordinal_index
            ordinal_index = list(range(1, number_of_symptoms + 1))

            return {"number_of_symptoms": number_of_symptoms}

        dispatcher.utter_message(text="Invalid answer.")
        return {"number_of_symptoms": None}

    async def validate_symptom(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validates `symptom` slot value and sends the patient's answer to Promptly"""

        patient_id = tracker.sender_id
        symptom = tracker.get_slot("symptom")
        response = Symptoms.set_symptoms(patient_id, str(symptom))

        if not response == 200:
            dispatcher.utter_message(text="Invalid answer.")
            return {"symptom": None}

        return {"symptom": slot_value}

    async def validate_intensity(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validates `intensity` slot value and sends the patient's answer to Promptly"""

        patient_id = tracker.sender_id
        intensity = tracker.get_slot("intensity")
        symptom = tracker.get_slot("symptom")
        input_pattern = rf"^[1-9] intensity|10 intensity"

        if re.match(input_pattern, slot_value):
            intensity = [int(s) for s in slot_value.split() if s.isdigit()][0]
            response = Symptoms.edit_symptoms(
                patient_id, {"intensity": intensity, "symptom": symptom}
            )

            if response == 200:
                return {"intensity": slot_value}
        else:
            dispatcher.utter_message(text="Invalid answer for intensity.")

        return {"intensity": None}

    async def validate_duration(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Union[Dict[Text, Any], List[Any]]:
        """Validates `duration` slot value and sends the patient's answer to Promptly"""

        patient_id = tracker.sender_id
        symptom = tracker.get_slot("symptom")
        intensity = tracker.get_slot("intensity")
        duration = tracker.get_slot("duration")
        number_of_symptoms = tracker.get_slot("number_of_symptoms")
        input_pattern_minutes = rf"^[0-9]+ minute(s|)"
        input_pattern_hours = rf"^[0-9]+ hour(s|)"
        input_pattern_days = rf"^[0-9]+ day(s|)"

        if (
            re.match(input_pattern_minutes, slot_value)
            or re.match(input_pattern_hours, slot_value)
            or re.match(input_pattern_days, slot_value)
        ):
            response = Symptoms.edit_symptoms(
                patient_id, {"duration": duration, "symptom": symptom}
            )
            if response == 200 and intensity is not None:
                dispatcher.utter_message(
                    text=f"Your '{symptom}' symptom was registered!\n"
                    + f"Intensity: {intensity.replace('intensity', '')}on a scale from 1-10\n"
                    + f"Duration: {duration}\n"
                )

                informative_texts = {
                    "Increased Thirst": "When you have diabetes, your body can't use sugars "
                    + "from food properly. This causes sugar to collect in your blood. High blood sugar "
                    + "levels force your kidneys to go into overdrive to get rid of the extra sugar. "
                    + "When your kidneys can't keep up, the excess glucose is excreted into your urine, "
                    + "dragging along fluids from your tissues, which makes you dehydrated.",
                    "Blurred Vision": "Diabetes symptoms sometimes "
                    + "involve your vision. High levels of blood glucose pull fluid "
                    + "from your tissues, including the lenses of your eyes. This "
                    + "affects your ability to focus.\n"
                    + "You should get an eye exam.",
                    "Fatigue/Tiredness": "Diabetes can make you feel tired. "
                    + "High blood glucose impairs your body's ability to use glucose "
                    + "for energy needs. Dehydration from increased "
                    + "urination also can leave you feeling fatigued.\n"
                    + "Here's some things you can do to boost your energy:\n\n"
                    + "- Aim for 7 to 9 hours of sleep each night.\n"
                    + "- Exercise regularly.\n"
                    + "- Eliminate processed foods and sugar from your diet.\n"
                    + "- Reduce your alcohol intake, if you drink.\n"
                    + "- Drink caffeine in moderation.\n"
                    + "- Try relaxation techniques like yoga or meditation.\n",
                    "Unexpected Weight Loss": "When you lose glucose through frequent urination, "
                    + "you also lose calories. At the same time, diabetes may keep the glucose from your "
                    + "food from reaching your cells — leading to constant hunger. The combined effect "
                    + "can potentially cause rapid weight loss, especially with type 1 diabetes.",
                    "Increased Hunger": "When you lose glucose through frequent urination, "
                    + "you also lose calories. At the same time, diabetes may keep the glucose from your "
                    + "food from reaching your cells — leading to constant hunger. The combined effect "
                    + "can potentially cause rapid weight loss, especially with type 1 diabetes.",
                    "Increased Urination": "Excessive thirst and increased urination "
                    + "are common diabetes signs and symptoms. When you have diabetes, excess "
                    + "glucose — a type of sugar — builds up in your blood. Your kidneys are forced "
                    + "to work overtime to filter and absorb the excess glucose.\n"
                    + "When your kidneys can't keep up, the excess glucose is excreted into "
                    + "your urine, dragging along fluids from your tissues, which makes you "
                    + "dehydrated. This will usually leave you feeling thirsty. As you drink more "
                    + "fluids to quench your thirst, you'll urinate even more.",
                }

                if symptom is not None:
                    dispatcher.utter_message(text=informative_texts[symptom])

                if number_of_symptoms is not None and int(number_of_symptoms) == 0:
                    return [
                        SlotSet("requested_slot", None),
                        SlotSet("number_of_symptoms", None),
                        SlotSet("symptom", None),
                        SlotSet("intensity", None),
                        SlotSet("duration", None),
                    ]
                return {"symptom": None, "intensity": None, "duration": None}
        else:
            dispatcher.utter_message(text="Invalid answer.")

        return {"duration": None}
