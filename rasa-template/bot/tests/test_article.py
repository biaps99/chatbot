from dotenv import load_dotenv
from utils.article import Article
import requests

load_dotenv()


def test_status_code_topic_diet_health_finder(endpoints, topic_diet):
    response = requests.get(endpoints["health_article_finder"].format(topic_diet))
    code = response.status_code
    assert code == 200


def test_status_code_topic_weight_health_finder(endpoints, topic_weight):
    response = requests.get(endpoints["health_article_finder"].format(topic_weight))
    code = response.status_code
    assert code == 200


def test_status_code_topic_blood_pressure_health_finder(
    endpoints, topic_blood_pressure
):
    response = requests.get(
        endpoints["health_article_finder"].format(topic_blood_pressure)
    )
    code = response.status_code
    assert code == 200


def test_status_code_topic_glucose_health_finder(endpoints, topic_glucose):
    response = requests.get(endpoints["health_article_finder"].format(topic_glucose))
    code = response.status_code
    assert code == 200


def test_status_code_topic_exercise_health_finder(endpoints, topic_exercise):
    response = requests.get(endpoints["health_article_finder"].format(topic_exercise))
    code = response.status_code
    assert code == 200


def test_status_code_topic_diet_promptly(endpoints, topic_diet, api_port):
    response = requests.get(endpoints["promptly_articles"].format(api_port, topic_diet))
    code = response.status_code
    assert code == 200


def test_status_code_topic_weight_promptly(endpoints, topic_weight, api_port):
    response = requests.get(
        endpoints["promptly_articles"].format(api_port, topic_weight)
    )
    code = response.status_code
    assert code == 200


def test_status_code_topic_blood_pressure_promptly(
    endpoints, topic_blood_pressure, api_port
):
    response = requests.get(
        endpoints["promptly_articles"].format(api_port, topic_blood_pressure)
    )
    code = response.status_code
    assert code == 200


def test_status_code_topic_glucose_promptly(endpoints, topic_glucose, api_port):
    response = requests.get(
        endpoints["promptly_articles"].format(api_port, topic_glucose)
    )
    code = response.status_code
    assert code == 200


def test_status_code_topic_exercise_promptly(endpoints, topic_exercise, api_port):
    response = requests.get(
        endpoints["promptly_articles"].format(api_port, topic_exercise)
    )
    code = response.status_code
    assert code == 200


def test_articles_in_response(endpoints, topic_exercise, api_port):
    response = requests.get(
        endpoints["promptly_articles"].format(api_port, topic_exercise)
    ).json()
    assert "articles" in response


def test_response_type(endpoints, topic_exercise, api_port):
    response = requests.get(
        endpoints["promptly_articles"].format(api_port, topic_exercise)
    ).json()["articles"]
    assert type(response) == list


def test_valid_url(endpoints, topic_exercise, api_port):
    response = requests.get(
        endpoints["promptly_articles"].format(api_port, topic_exercise)
    ).json()["articles"]
    example_article_url = response[0]
    assert example_article_url.startswith("http")


def test_get_articles_result_type(topic_exercise):
    articles_list = Article.get_articles(topic_exercise)
    assert type(articles_list) == list


def test_get_articles_result_len(topic_exercise):
    articles_list = Article.get_articles(topic_exercise)
    assert len(articles_list) > 0


def test_get_articles_url_topic(topic_exercise):
    articles_list = Article.get_articles(topic_exercise)
    example_article = articles_list[0]
    assert example_article.url.startswith("http")
    assert example_article.topic == "physical exercise"
