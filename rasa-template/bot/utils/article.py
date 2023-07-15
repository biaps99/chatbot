from dotenv import load_dotenv
from .path import Path
import requests

load_dotenv()


class Article(Path):
    def __init__(self, topic: str, url: str):
        self.topic = topic
        self.url = url

    @staticmethod
    def get_health_finder_articles(topic: str):
        full_path = Path.get_path(
            key_endpoint="health_article_finder", article_topic=topic
        )
        response = requests.get(full_path)
        bestResults = []

        if response.status_code == 200:
            if "Result" in response.json() and "Total" in response.json()["Result"]:
                if response.json()["Result"]["Total"] > 0:
                    articles_list = response.json()["Result"]["Resources"]["Resource"]
                else:
                    articles_list = []

                for article in articles_list:
                    if (
                        topic.lower() in article["Title"].lower()
                        and "AcessibleVersion" in article.keys()
                    ):
                        bestResults.append(article["AcessibleVersion"])

        return bestResults

    @staticmethod
    def get_promptly_articles(topic: str):
        full_path = Path.get_path(key_endpoint="promptly_articles", article_topic=topic)
        response = requests.get(full_path)
        promptly_articles = []

        if response.status_code == 200:
            if "articles" in response.json():
                promptly_articles = response.json()["articles"]

        return promptly_articles

    @classmethod
    def get_articles(cls, topic: str):
        """
        Retrieves articles from 'myhealthfinder' and extends that set with default articles from Promptly, according to the given topic.

        topic : str
            string representing the main topic of the article, for instance, "glucose measurement".
        """

        health_finder_articles = Article.get_health_finder_articles(topic)
        promptly_articles = Article.get_promptly_articles(topic)
        total_articles = promptly_articles + health_finder_articles
        article_instances = []

        for article_url in total_articles:
            article_instances.append(cls(topic, article_url))

        return article_instances
