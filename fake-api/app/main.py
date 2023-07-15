from typing import Dict, Union
from fastapi import FastAPI, Body
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import json
import os


app = FastAPI()
load_dotenv()
api_root = os.environ.get("API_ROOT")

# Global variables. This is just for POC purposes.
with open(f"{api_root}/static/articles.json", "r") as fp:
    articles = json.load(fp)
patients_answers = {"5548951369": {}}
patients_medication = {}
patients_symptom = {}
next_question_id = 1
repeated = False
health_questionnaire = {
    "questions": {
        1: {
            "title": "Is your stress level high, medium or low?",
            "possible_values": ["low", "medium", "high"],
            "button_choice": True,
        },
        2: {
            "title": "How many hours did you sleep last night?",
            "possible_values": [
                "less than 6 hours",
                "more than 6 hours",
            ],
            "button_choice": True,
        },
        3: {
            "title": "Felt very fatigued?",
            "possible_values": ["yes", "no"],
            "button_choice": True,
        },
        4: {
            "title": "Felt very thirsty?",
            "possible_values": ["yes", "no"],
            "button_choice": True,
        },
        5: {
            "title": "Felt very hungry?",
            "possible_values": ["yes", "no"],
            "button_choice": True,
        },
        6: {
            "title": "Urinated (pee) a lot?",
            "possible_values": ["yes", "no"],
            "button_choice": True,
        },
        7: {
            "title": "Had any episode of low blood sugar?",
            "possible_values": ["yes", "no"],
            "button_choice": True,
        },
        8: {
            "title": "Had unexpected weight loss?",
            "possible_values": ["yes", "no"],
            "button_choice": True,
        },
        9: {
            "title": "Had blurry vision?",
            "possible_values": ["yes", "no"],
            "button_choice": True,
        },
        10: {
            "title": "Felt nausea, vomiting or stomach pain?",
            "possible_values": ["yes", "no"],
            "button_choice": True,
        },
        11: {
            "title": None,
            "possible_values": None,
            "button_choice": None,
        },
    }
}
patients_daily_goals = {
    "5548951369": {
        "Weigh in": {"status": "True", "value": 56.5, "number measurements": 1},
        "Read educational articles": {"status": "False", "number": "None"},
        "Check blood pressure": {
            "status": "True",
            "systolic": {
                "value": 120,
            },
            "diastolic": {
                "value": 70,
            },
            "number measurements": 1,
        },
        "Practise physical exercise": {"status": "False"},
        "Comply with nutrition plan": {"status": "True"},
        "Measure glucose level": {
            "status": "True",
            "value": 48,
            "number measurements": 1,
        },
    }
}


class Answer(BaseModel):
    question_title: str = Field(title="Title of the question", max_length=100)
    patient_answer: str = Field(title="Patient answer", max_length=100)


class Measurement(BaseModel):
    metric: str = Field(title="Name of the metric", max_length=100)
    value: int = Field(title="Value of the metric", gt=0)
    type: Union[str, None] = Field(
        default=None, title="Type of the metric", max_length=100
    )


class Symptoms(BaseModel):
    symptom: str = Field(title="Name of the symptom", max_length=100)
    intensity: int = Field(title="Intensity of the symptom", gt=0)
    duration: int = Field(title="Duration of the symptom", gt=0)


class Medication(BaseModel):
    medicine: str = Field(title="Name of the medicine", max_length=100)
    dose: Union[str, None] = Field(default=None, title="Dosing", max_length=100)
    permanent: Union[bool, None] = Field(
        default=None, title="If the medication is permanent"
    )
    how_many_times: Union[int, None] = Field(
        default=None, title="How many times a day the medication is taken", gt=0
    )
    schedule: Union[str, None] = Field(default=None, title="Schedule time")
    how_many_days: Union[int, None] = Field(
        default=None, title="How many days the medication is scheduled for", gt=0
    )


def set_alarming_metrics(patient_answers: Dict[str, str]):
    """Analyses the patient's answers and sets alarming metrics in those answers"""

    response = []
    questions_left = {
        "Felt very fatigued?": "fatigue",
        "Had unexpected weight loss?": "sudden weight loss",
        "Urinated (pee) a lot?": "increased urination",
        "Felt very thirsty?": "increased thirst",
        "Felt very hungry?": "increased hunger",
        "Had blurry vision?": "blurry vision",
        "Felt nausea, vomiting or stomach pain?": "nausea",
        "Had any episode of low blood sugar?": "low blood sugar",
    }

    for question_title in list(patient_answers.keys()):
        answer = {}
        answer["question_title"] = question_title
        answer["patient_answer"] = patient_answers[question_title]

        if question_title == "Is your stress level high, medium or low?":
            answer["question_topic"] = "high stress"
            answer["alarming"] = False
            if "high" in answer["patient_answer"]:
                answer["alarming"] = True
        elif question_title == "How many hours did you sleep last night?":
            answer["question_topic"] = "lack of sleep"
            answer["alarming"] = False
            if answer["patient_answer"] == "less than 6 hours":
                answer["alarming"] = True
        else:
            answer["question_topic"] = questions_left[f"{question_title}"]
            answer["alarming"] = False
            if answer["patient_answer"] == "yes":
                answer["alarming"] = True
        response.append(answer)

    return response


@app.get("/patients_daily_goals/{patient_id}")
def get_patient_daily_goals(patient_id: str):

    return patients_daily_goals["5548951369"]


@app.put("/patients_daily_goals/{patient_id}")
def edit_patient_daily_goals(*, measurement: Measurement = Body(), patient_id: str):
    global patients_daily_goals

    if measurement.metric == "Check blood pressure":
        patients_daily_goals["5548951369"]["Check blood pressure"][measurement.type][
            "value"
        ] = measurement.value
    else:
        patients_daily_goals["5548951369"][measurement.metric][
            "value"
        ] = measurement.value
    patients_daily_goals["5548951369"][measurement.metric]["status"] = "True"
    patients_daily_goals["5548951369"][measurement.metric]["number measurements"] += 1

    return patients_daily_goals["5548951369"]


@app.get("/articles/{topic}")
def get_articles(topic: str):
    if topic in list(articles.keys()):
        default_set_articles = articles[topic]
    else:
        default_set_articles = []
        if "weight" in topic:
            default_set_articles = articles["weight"]
        elif "exercise" in topic or "physical activity" in topic:
            default_set_articles = articles["physical exercise"]
        elif "glucose" in topic or "blood sugar" in topic or "glycaemia" in topic:
            default_set_articles = articles["glucose levels"]
        elif "nutrition" in topic or "diet" in topic:
            default_set_articles = articles["nutrition"]
        elif "blood pressure" in topic:
            default_set_articles = articles["blood pressure"]

    return {"articles": default_set_articles}


@app.get("/next_question")
def get_next_question(patient_id: str):
    global next_question_id
    global patients_answers
    data = health_questionnaire["questions"][next_question_id]
    data["repeated"] = repeated
    num_questions = len(list(health_questionnaire["questions"].keys()))

    if next_question_id == 1:
        patients_answers[patient_id] = {}
    if next_question_id == num_questions:
        next_question_id = 1

    return data


@app.get("/answers/{patient_id}")
def get_patient_answers(patient_id: str):
    response = set_alarming_metrics(patients_answers[patient_id])

    return {"answers": response}


@app.post("/answer")
def set_answer(*, answer: Answer = Body(), patient_id: str):
    questions = health_questionnaire["questions"]
    global next_question_id
    global repeated
    global patients_answers

    for index in questions:
        if questions[index]["title"] == answer.question_title:
            if (answer.patient_answer).lower() in questions[index]["possible_values"]:
                if patient_id not in list(patients_answers.keys()):
                    patients_answers[patient_id] = {}
                next_question_id = index + 1
                repeated = False
                patients_answers[patient_id][
                    answer.question_title
                ] = answer.patient_answer
                return next_question_id
            repeated = True


@app.post("/medication")
def set_medication(*, medication: Medication = Body(), patient_id: str):
    global patients_medication

    if patient_id not in patients_medication:
        patients_medication[patient_id] = {}

    medicine_taken = medication.dict()["medicine"]
    patients_medication[patient_id][medicine_taken] = {}

    return medication.dict


@app.put("/medication")
def edit_medication(*, medication: Medication = Body(), patient_id: str):
    global patients_medication
    medicine_taken = medication.dict()["medicine"]

    for parameter in medication.dict().keys():
        if medication.dict()[parameter] != None and parameter != "schedule":
            patients_medication[patient_id][medicine_taken][
                parameter
            ] = medication.dict()[parameter]
        elif medication.dict()[parameter] != None and parameter == "schedule":
            if "schedule" not in patients_medication[patient_id][medicine_taken].keys():
                patients_medication[patient_id][medicine_taken]["schedule"] = []

            patients_medication[patient_id][medicine_taken]["schedule"].append(
                medication.dict()["schedule"]
            )

    return patients_medication[patient_id][medicine_taken]


@app.get("/medication")
def get_medication(patient_id: str):

    return patients_medication[patient_id]


@app.delete("/medication")
def delete_medication(*, medication: Medication = Body(), patient_id: str):
    global patients_medication
    medicine_to_delete = medication.dict()["medicine"]
    del patients_medication[patient_id][medicine_to_delete]

    return medication.dict


@app.post("/symptoms")
def set_symptoms(*, result: dict, patient_id: str):
    global patients_symptom

    symptom = result["symptom"]
    if patient_id not in patients_symptom:
        patients_symptom[patient_id] = {}

    patients_symptom[patient_id][symptom] = {}
    return symptom


@app.put("/symptoms")
def edit_symptoms(*, data: dict, patient_id: str):
    global patients_symptom
    symptom_felt = data["symptom"]
    for parameter in data.keys():
        patients_symptom[patient_id][symptom_felt][parameter] = data[parameter]

    return patients_symptom[patient_id][symptom_felt]
