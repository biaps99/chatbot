from dotenv import load_dotenv
from utils.medication import Medication
from datetime import datetime
import requests


load_dotenv()


def test_set_medication(patient_id):
    response = Medication.set_medication(patient_id, "metaformin")
    assert response == 200


def test_edit_medication(patient_id):
    data = {
        "medicine": "metaformin",
        "dose": "5 mg",
        "permanent": True,
        "how_many_times": 1,
        "schedule": datetime.now().strftime(f"%d/%m/%y, %H:%M"),
    }
    response = Medication.edit_medication(patient_id, data)
    assert response == 200


def test_endpoint(patient_medication):
    results = requests.get(patient_medication)
    code = results.status_code
    assert code == 200


def test_get_medication(patient_id):
    medication = Medication.get_medication(patient_id, "metaformin")
    assert medication is not None
    assert "metaformin" == medication.medicine
    assert "5 mg" == medication.dose
    assert True == medication.permanent
    assert 1 == medication.how_many_times
    assert type(medication.schedule) == list


def test_get_all_medicines(patient_id):
    all_medicines = Medication.get_all_medicines(patient_id)
    assert type(all_medicines) == list
    assert len(all_medicines) == 1


def test_delete_medication(patient_id):
    response = Medication.delete_medication(patient_id, "metaformin")
    assert 200 == response


def test_get_all_medicines_two(patient_id):
    all_medicines = Medication.get_all_medicines(patient_id)
    assert type(all_medicines) == list
    assert len(all_medicines) == 0
