from dotenv import load_dotenv
from utils.goals import Goals
import requests

load_dotenv()


def test_patient_goals_status_code(patient_daily_goals):
    results = requests.get(patient_daily_goals)
    code = results.status_code
    assert code == 200


def test_patient_goals_result_keys(patient_daily_goals):
    results = requests.get(patient_daily_goals).json()
    assert "Weigh in" in results
    assert "Read educational articles" in results
    assert "Check blood pressure" in results
    assert "Practise physical exercise" in results
    assert "Comply with nutrition plan" in results
    assert "Measure glucose level" in results


def test_retrieve_patient_daily_goals(patient_id):
    results = Goals.retrieve_status_of_patient_daily_goals(patient_id)
    assert "Weigh in" in results
    assert "Read educational articles" in results
    assert "Check blood pressure" in results
    assert "Practise physical exercise" in results
    assert "Comply with nutrition plan" in results
    assert "Measure glucose level" in results
