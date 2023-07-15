from typing import List
from dotenv import load_dotenv
from .path import Path
import requests

load_dotenv()


class Question(Path):
    def __init__(
        self,
        title: str,
        possible_values: List[str],
        button_choice: bool,
        repeated: bool,
    ):
        self.title = title
        self.possible_values = possible_values
        self.button_choice = button_choice
        self.repeated = repeated

    @classmethod
    def get_next_question(cls, patient_id: str):
        """Retrieves the next question to a patient using Promptly's API"""

        full_path = Path.get_path(
            key_endpoint="promptly_next_question", patient_id=patient_id
        )
        response = requests.get(full_path)
        question = None

        if response.status_code == 200:
            result = response.json()
            question = cls(
                result["title"],
                result["possible_values"],
                result["button_choice"],
                result["repeated"],
            )

        return question
