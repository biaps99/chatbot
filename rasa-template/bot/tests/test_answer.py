from dotenv import load_dotenv
from utils.answer import Answer
import requests

load_dotenv()


def test_status_code(patient_answers):
    results = requests.get(patient_answers)
    code = results.status_code
    assert code == 200


def test_answers_in_keys(patient_answers):
    results = requests.get(patient_answers).json()
    assert "answers" in results


def test_results_type(patient_answers):
    results = requests.get(patient_answers).json()["answers"]
    assert type(results) == list


def test_get_patient_answers(patient_id):
    answers = Answer.get_patient_answers(patient_id)
    assert type(answers) == list
