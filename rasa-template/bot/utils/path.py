from typing import Union
from dotenv import load_dotenv
import os
import ast

load_dotenv()


class Path:

    api_port = os.environ.get("API_PORT")
    api_host = os.environ.get("API_HOST")
    endpoints = ast.literal_eval(os.environ["ENDPOINTS"])

    @classmethod
    def get_path(
        cls,
        key_endpoint: str,
        patient_id: Union[str, None] = None,
        article_topic: Union[str, None] = None,
    ):
        if article_topic is not None and key_endpoint == "health_article_finder":
            return Path.endpoints[key_endpoint].format(article_topic)
        elif article_topic is not None and key_endpoint == "promptly_articles":
            return Path.endpoints[key_endpoint].format(
                Path.api_host, Path.api_port, article_topic
            )

        return Path.endpoints[key_endpoint].format(
            Path.api_host, Path.api_port, patient_id
        )
