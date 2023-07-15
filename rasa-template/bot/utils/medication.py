from typing import List, Union
from dotenv import load_dotenv
from .path import Path
import requests

load_dotenv()


class Medication(Path):
    def __init__(
        self,
        medicine: str,
        dose: str,
        permanent: bool,
        how_many_times: int,
        schedule: List[str],
        how_many_days: Union[int, None] = None,
    ):
        self.medicine = medicine
        self.dose = dose
        self.permanent = permanent
        self.how_many_times = how_many_times
        self.schedule = schedule
        self.how_many_days = how_many_days

    @classmethod
    def get_medication(cls, patient_id: str, medicine: str):
        """Retrieves the information about a given patient medication."""

        full_path = Path.get_path(
            key_endpoint="patient_medication", patient_id=patient_id
        )
        response = requests.get(full_path)
        medication = None

        if response.status_code == 200 and medicine in response.json():
            result = response.json()[medicine]
            how_many_days = None

            if result["permanent"] == False:
                how_many_days = result["how_many_days"]

            medication = cls(
                medicine,
                result["dose"],
                result["permanent"],
                result["how_many_times"],
                result["schedule"],
                how_many_days,
            )

        return medication

    @classmethod
    def get_all_medicines(cls, patient_id: str):
        """Retrieves the information about all of the patient's medicines."""

        full_path = Path.get_path(
            key_endpoint="patient_medication", patient_id=patient_id
        )
        response = requests.get(full_path)
        medicines = []

        if response.status_code == 200:
            result = response.json()

            for medicine in result:
                how_many_days = None
                medication = result[medicine]

                if medication["permanent"] == False:
                    how_many_days = medication["how_many_days"]

                medicine_object = cls(
                    medicine,
                    medication["dose"],
                    medication["permanent"],
                    medication["how_many_times"],
                    medication["schedule"],
                    how_many_days,
                )
                medicines.append(medicine_object)

        return medicines

    @staticmethod
    def set_medication(patient_id: str, medicine: str):
        """Create a new medicine entry for a given patient"""

        full_path = Path.get_path(
            key_endpoint="patient_medication", patient_id=patient_id
        )
        data = {"medicine": medicine}
        response = requests.post(url=full_path, json=data)

        return response.status_code

    @staticmethod
    def edit_medication(patient_id: str, data: dict):
        """Edit the created entry with the information from the patient medication"""

        full_path = Path.get_path(
            key_endpoint="patient_medication", patient_id=patient_id
        )
        response = requests.put(url=full_path, json=data)

        return response.status_code

    @staticmethod
    def delete_medication(patient_id: str, medicine: str):
        """Delete a medicine entry for a given patient"""

        full_path = Path.get_path(
            key_endpoint="patient_medication", patient_id=patient_id
        )
        data = {"medicine": medicine}
        response = requests.delete(url=full_path, json=data)

        return response.status_code
