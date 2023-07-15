from dotenv import load_dotenv
from .path import Path
import requests

load_dotenv()


class Answer(Path):
    def __init__(
        self,
        question_title: str,
        question_topic: str,
        patient_answer: str,
        alarming: bool,
    ):
        self.question_title = question_title
        self.question_topic = question_topic
        self.patient_answer = patient_answer
        self.alarming = alarming

    @classmethod
    def get_patient_answers(cls, patient_id: str):
        """Retrieves all patient answers to a given Promptly questionnaire"""

        full_path = Path.get_path(
            key_endpoint="promptly_answers", patient_id=patient_id
        )
        response = requests.get(full_path)

        if response.status_code == 200:
            results = response.json()

            if "answers" in results:
                answers = []

                for result in results["answers"]:
                    answer = cls(
                        result["question_title"],
                        result["question_topic"],
                        result["patient_answer"],
                        result["alarming"],
                    )
                    answers.append(answer)

                return answers

        return []

    @classmethod
    def set_patient_answer(cls, patient_id: str, data: dict):
        """Send patient answer to Promptly"""

        full_path = Path.get_path(key_endpoint="patient_answer", patient_id=patient_id)
        response = requests.post(url=full_path, json=data)

        return response.status_code
