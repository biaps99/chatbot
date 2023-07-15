from dotenv import load_dotenv
from utils.question import Question
import requests

load_dotenv()


def test_next_question_status_code(next_question):
    results = requests.get(next_question)
    code = results.status_code
    assert code == 200


def test_next_question_result_keys(next_question):
    results = requests.get(next_question).json()
    assert "title" in results
    assert "possible_values" in results
    assert "repeated" in results


def test_get_next_question(patient_id):
    next_question = Question.get_next_question(patient_id)
    assert next_question is not None
    assert type(next_question.title) == str
    assert type(next_question.possible_values) == list
    assert type(next_question.repeated) == bool
