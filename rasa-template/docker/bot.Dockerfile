FROM python:3.8.12
FROM khalosa/rasa-aarch64:3.0.8

WORKDIR /bot
COPY rasa-template/bot /bot
COPY rasa-template/modules /modules

USER root
RUN apt-get update && apt-get install -y gcc make

RUN python -m pip install --upgrade pip

COPY rasa-template/requirements.txt /tmp

RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN python -c "import nltk; nltk.download('stopwords');"
RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
USER 1001

RUN export PYTHONPATH=/bot/components/:$PYTHONPATH

ENTRYPOINT []
CMD []
