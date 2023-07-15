.PHONY: all clean actions
PIP_FLAGS = --use-deprecated=legacy-resolver
LOG_LEVEL = -v
RASA_ENDPOINTS = --endpoints 
ENDPOINTS = endpoints.yml
RASA_CREDENTIALS = --credentials
CREDENTIALS = credentials.yml
API_SECRET_KEY = <generated_api_secret_key>

install:
	pip install --upgrade pip 						&& \
	pip install -r requirements.txt

telegram:
	rasa run \
		-m models/ \
		$(LOG_LEVEL) \
		$(RASA_ENDPOINTS) $(ENDPOINTS) \
		$(RASA_CREDENTIALS)	$(CREDENTIALS) \
		--port 5005 \
		--enable-api \