import requests
from create_api_access_token import create_access_token
from typing import Text, Dict


def trigger_conversation(intent_name: Text, user_id: Text, entities: Dict[Text, Text]):
    """
    An external API or service can trigger a conversation between the bot and a given Telegram user
    :: intent_name: the name of the intent you want to execute
    :: user_id: the chat id of the user you want to contact in Telegram
    :: entities: possible entities to pass in the intent
    """

    # User with the role 'admin' has access to all endpoints.
    token_payload = {"user": {"username": "user123", "role": "admin"}}

    encoded_token = create_access_token(token_payload)

    payload = {"name": intent_name, "entities": entities}

    # In a real-life scenario, you would get the users' conversation IDs from an API or a database.
    # This parameter can be seen in the Elasticsearch database.

    url = f"http://localhost:5005/conversations/{user_id}/trigger_intent?output_channel=telegram"
    response = requests.post(url=url, json=payload)
    # headers={'Authorization': 'Bearer {}'.format(encoded_token)})

    return response.status_code


def main():

    trigger_conversation("show_wellness_check", "5548951369", {})


if __name__ == "__main__":
    main()
