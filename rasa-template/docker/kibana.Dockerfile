FROM docker.elastic.co/kibana/kibana:7.3.0
FROM python:3.6-slim

COPY rasa-template/modules/analytics/import_dashboards.py analytics/import_dashboards.py
COPY rasa-template/modules/analytics/dashboards.json analytics/dashboards.json

USER 1001
RUN python -m pip install --upgrade pip
RUN pip install requests
