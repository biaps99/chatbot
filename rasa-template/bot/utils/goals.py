from dotenv import load_dotenv
from .path import Path
import requests

load_dotenv()


class Goals(Path):
    @staticmethod
    def retrieve_status_of_patient_daily_goals(patient_id: str):
        """Retrieves the status of the patient's daily goals using Promptly's API"""

        full_path = Path.get_path(
            key_endpoint="patients_daily_goals", patient_id=patient_id
        )
        response = requests.get(full_path)
        result = {}

        if response.status_code == 200:
            result = response.json()

        return result

    @staticmethod
    def edit_status_of_patient_daily_goals(patient_id: str, data: dict):
        """Edit the status of the patient's daily goals using Promptly's API"""

        full_path = Path.get_path(
            key_endpoint="patients_daily_goals", patient_id=patient_id
        )
        response = requests.put(full_path, json=data)

        return response.status_code
