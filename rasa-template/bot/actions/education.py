from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import FollowupAction, SlotSet, ReminderScheduled
from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime, timedelta
from utils.article import Article
from dotenv import load_dotenv
import os
import random

load_dotenv()


class ActionScheduleArticleForAlarmingMetrics(Action):
    """
    Schedules reminders to show articles according to the patient's alarming metrics.
    For instance, if the patient has answered in the questionnaire that he felt very fatigued, the Bot shows
    an article about that symptom.
    """

    def name(self) -> Text:
        return "action_show_article_for_alarming_metrics"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        alarming_metrics = tracker.get_slot("alarming_metrics")
        reminders = []
        time_gap = int(os.environ["TIME_GAP"])

        if alarming_metrics and len(alarming_metrics) > 0:
            seconds_interval = 0
            for index, metric in enumerate(alarming_metrics):
                date = datetime.now() + timedelta(seconds=time_gap + seconds_interval)
                reminder = ReminderScheduled(
                    "choose_article_topic",
                    trigger_date_time=date,
                    entities={"topic": metric},
                    name=f"my_reminder{index}",
                    kill_on_user_message=False,
                )
                reminders.append(reminder)
                seconds_interval += 10

        return reminders


class ActionProvideArticle(Action):
    """Randomly provides the link of an article according to the choice of the user"""

    def name(self) -> Text:
        return "action_provide_article"

    def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        topic = tracker.get_slot("topic")
        alarming_metrics = tracker.get_slot("alarming_metrics")

        if topic:
            articles_list = Article.get_articles(topic)
            if len(articles_list) > 0:
                pick_article_index = random.randint(0, len(articles_list) - 1)
                article = articles_list[pick_article_index].url
                if alarming_metrics and topic in alarming_metrics:
                    dispatcher.utter_message(f"I noticed that you had {topic}.")

                dispatcher.utter_message(
                    f"There you go an article about {topic} ({article})."
                )

                return [SlotSet("article_url", article)]
            dispatcher.utter_message(f"I did not find an article about {topic}.")

        return []


class ActionAnswerToLearnMore(Action):
    """If the user wants to learn more about a given topic, the chatbot provides an article"""

    def name(self) -> Text:
        return "action_answer_to_learn_more"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        intent = tracker.latest_message["intent"].get("name")

        if intent == "refuse_help":
            dispatcher.utter_message(response="utter_accept_refusal")
        else:
            return [FollowupAction("action_provide_article")]

        return []


class ActionAnswerAbout(Action):
    """Provide health information about a given topic"""

    def name(self) -> Text:
        return "action_answer_about"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        intent = tracker.latest_message["intent"].get("name")

        if intent in [
            "ask_about_glucose",
            "ask_about_weight",
            "ask_about_nutrition",
            "ask_about_exercise",
            "ask_about_blood_pressure",
        ]:
            string = intent.replace("ask", "answer")
            dispatcher.utter_message(response="utter_" + string)

        return []


class ActionShowDifferentArticle(Action):
    """If the user has already viewed a given article, the chatbot shows another one"""

    def name(self) -> Text:
        return "action_show_different_article"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        last_url = tracker.get_slot("article_url")
        topic = tracker.get_slot("topic")

        if topic:
            article_urls = Article.get_articles(topic)
            num_articles = len(article_urls)
            pick_article_index = 0
            new_url = article_urls[pick_article_index].url

            if last_url:
                while new_url == last_url:
                    pick_article_index = random.randint(0, num_articles - 1)
                    new_url = article_urls[pick_article_index].url

            dispatcher.utter_message(
                f"There you go a new article about {topic} ({new_url})"
            )

            return [SlotSet("article_url", new_url)]

        return []
