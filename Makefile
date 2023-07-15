current_dir := $(shell pwd)
user := $(shell whoami)

ENDPOINTS = endpoints.yml
CREDENTIALS = credentials.yml

# DEPLOYMENT

# Don't forget to run "ngrok http 5005" to create the tunnel.
# http://localhost:4040/status to view Ngrok's monitoring dashboard.
# http://localhost:15672 to view RabbitMQ's UI.
# http://localhost:5601 to view Kibana's UI.


build-analytics:
	docker-compose up -d elasticsearch
	docker-compose up -d rabbitmq
	docker-compose up -d rabbitmq-consumer
	docker-compose up -d kibana

# Run on shell just one time
# docker-compose run --rm -v $PWD/rasa-template/modules/analytics:/analytics bot python /analytics/setup_elastic.py
# docker-compose run --rm -v $PWD/rasa-template/modules/analytics:/analytics bot python /analytics/import_dashboards.py

run:
	docker-compose up -d rabbitmq
	docker-compose up -d rabbitmq-consumer
	docker-compose up -d elasticsearch
	docker-compose up -d kibana
	docker-compose up -d fakeapi

fakeapi:
	docker-compose up -d fakeapi

telegram:
	docker-compose run \
		-d \
		--rm \
		--service-ports \
		bot \
		make telegram ENDPOINTS=$(ENDPOINTS) CREDENTIALS=$(CREDENTIALS)