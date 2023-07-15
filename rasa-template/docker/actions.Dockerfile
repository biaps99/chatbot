FROM rasa/rasa-sdk:3.0.4
FROM python:3.8.12

WORKDIR /bot
COPY rasa-template/bot /bot

RUN pip install python-dotenv
RUN pip install git+https://github.com/RasaHQ/rasa-sdk@3.0.4
RUN pip install inflect

ENTRYPOINT []
CMD "python -m rasa_sdk -p 5055"
