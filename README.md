# Chatbot

If you want to learn about our **Chatbot**, you can read this.

# Setup

After downloading the project, go to the **"/bot"** directory and perform the following steps.

## Create a virtual environment

-> **conda env create -v --name rasatest -f env.yml** to create a new virtual environment called "rasatest" based on the dependencies from the "env.yml" file.

-> **conda activate rasatest** to activate the virtual environment.

## Install required packages

If you are on Mac, you’ll need to install the Rasa dependencies manually from git.  
The versions shown below have been tested beforehand and seem to work!

-> **pip install git+https://github.com/RasaHQ/rasa-sdk@3.0.4 --no-deps**
-> **pip install git+https://github.com/RasaHQ/rasa.git@3.0.8 --no-deps**

Once that is finished you should be able to run Rasa!

-> **python -m rasa --version**

If you are on Windows, you can simply use:

-> **pip install -r requirements.txt** to install **rasa 3.0.8** on the virtual environment.

## Useful commands

Here some useful commands you should need.

-> **rasa data validate** to check for any inconsistencies in the stories and rules.

-> **rasa train** to train the model.

-> **rasa shell** to interact via terminal with the chatbot.

-> **rasa interactive** to interact with the chatbot and perform step-by-step debbuging.

-> **rasa run actions** to start a local server for the custom actions.

## Interact with the ChatBot via Telegram

You can interact with the chatbot via Telegram. For that, you need to expose your Rasa server to the public, so that other people can communicate with your bot. To achieve that, perform the following steps:

### Download [Ngrok](https://ngrok.com/) and create an account.

Once ngrok is installed, connect it to your ngrok Account. If you haven't already, [sign up (or log in)](https://dashboard.ngrok.com/) to the ngrok Dashboard and get your [Authtoken](https://dashboard.ngrok.com/get-started/your-authtoken). Ngrok uses the authtoken to log into your account when you start a tunnel. Copy the value and run this command to add the authtoken in your terminal.

-> **ngrok config add-authtoken AUTHTOKEN**

### Start Ngrok.

-> **ngrok http 5005**

> 5001 is the port in which the Rasa server will be running.

After running the command, you should see something similar to:

-> **Forwarding https://84c5df439d74.ngrok.io -> http://localhost:5005**

### Create a bot on Telegram

To create a bot on Telegram, simply follow the steps in https://core.telegram.org/bots#6-botfather. From there, you should extract two parameters: an **access_token** and a **verify**, which correspond to a token and the username of the bot, respectively. These parameters are given by the Botfather.

### Configure the [credentials.yml](credentials.yml) file.

Add the following parameters to the [credentials.yml](credentials.yml) file.

telegram:

access_token: ${your_token}

verify: ${bot_username}

webhook_url: ${tunnel_url_generated_by_ngrok/webhooks/telegram/webhook}

### Run the Rasa server, the actions server, the fake API and interact with the bot in your Telegram account!

-> **rasa run --port 5005** to run Rasa server on port 5005.

-> **rasa run actions** to run Rasa custom actions server.

-> **uvicorn main:app --reload** to run fake API.

## Deploy with Docker

In order to deploy the chatbot with Docker, **7 containers** are configured:

- The **Rasa chatbot**;
- The **Rasa custom actions server** used to connect with external APIs;
- The **fake API** to simulate interaction with Promptly's services;
- The custom broker to store Rasa tracker data - **RabbitMq**;
- The custom broker consumer responsible to store data in ElasticSearch - **RabbitMq-consumer**;
- The database to store the conversations data - **Elasticsearch**;
- The tool to analise the data and build dashboards - **Kibana**.

If it is the first time deploying the project, **on the root folder**, perform the following commands:

1. Don't forget to **start Ngrok** and **configure the credentials.yml file**.

2. **make build-analytics** to build and run the analytics containers.

Then, run on shell just one time:

3. **docker-compose run --rm -v $PWD/rasa-template/modules/analytics:/analytics bot python /analytics/setup_elastic.py** to setup the Elasticsearch database.

4. **docker-compose run --rm -v $PWD/rasa-template/modules/analytics:/analytics bot python /analytics/import_dashboards.py** to build the data dashboards.

5. **make fakeapi** to build and run the fake API container.

6. **make telegram** to build and run the actions server and the chatbot containers.

Once you built the project for the first time, then, every time you want to start the project, you will only need to:

1. **start Ngrok** and **configure the credentials.yml file**.
1. Run **make run** to build and run the analytics and the fake API containers.
1. Run **make telegram** to build and run the actions server and the chatbot containers.
