from typing import List, Union
from dotenv import load_dotenv
from .path import Path
import requests

load_dotenv()


class Symptoms(Path):
    def __init__(
        self,
        symptom: str,
        intensity: int,
        duration: int,
    ):
        self.symptom = symptom
        self.intensity = intensity
        self.duration = duration

    @staticmethod
    def set_symptoms(patient_id: str, symptom: str):
        """Create a new symptom entry for a given patient"""

        full_path = Path.get_path(
            key_endpoint="patient_symptoms", patient_id=patient_id
        )
        data = {"symptom": symptom}
        response = requests.post(url=full_path, json=data)

        return response.status_code

    @staticmethod
    def edit_symptoms(patient_id: str, data: dict):
        """Edit the created entry with the information from the patient medication"""

        full_path = Path.get_path(
            key_endpoint="patient_symptoms", patient_id=patient_id
        )
        response = requests.put(url=full_path, json=data)

        return response.status_code
