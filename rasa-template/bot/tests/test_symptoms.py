from dotenv import load_dotenv
from utils.symptoms import Symptoms
from datetime import datetime
import requests

load_dotenv()


def test_set_medication(patient_id):
    response = Symptoms.set_symptoms(patient_id, "Increased Thirst")
    assert response == 200


def test_edit_symptoms(patient_id):
    data = {
        "symptom": "Increased Thirst",
        "intensity": "7 intensity",
        "duration": "5 days",
    }
    response = Symptoms.edit_symptoms(patient_id, data)
    assert response == 200
