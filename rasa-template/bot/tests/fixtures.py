from dotenv import load_dotenv
import os
import ast
import pytest

load_dotenv()


@pytest.fixture
def api_port():
    return os.environ.get("API_PORT")


@pytest.fixture
def endpoints():
    return ast.literal_eval(os.environ["ENDPOINTS"])


@pytest.fixture
def patient_id():
    return "5548951369"


@pytest.fixture
def patient_answers(api_port, endpoints, patient_id):
    return endpoints["promptly_answers"].format(api_port, patient_id)


@pytest.fixture
def next_question(api_port, endpoints, patient_id):
    return endpoints["promptly_next_question"].format(api_port, patient_id)


@pytest.fixture
def patient_daily_goals(api_port, endpoints, patient_id):
    return endpoints["patients_daily_goals"].format(api_port, patient_id)


@pytest.fixture
def patient_medication(api_port, endpoints, patient_id):
    return endpoints["patient_medication"].format(api_port, patient_id)


@pytest.fixture
def topic_diet():
    return "diet"


@pytest.fixture
def topic_weight():
    return "weight"


@pytest.fixture
def topic_blood_pressure():
    return "blood pressure"


@pytest.fixture
def topic_glucose():
    return "glucose"


@pytest.fixture
def topic_exercise():
    return "physical exercise"
