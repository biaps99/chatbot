FROM python:3.8.12

WORKDIR /fake-api

COPY fake-api/requirements.txt /fake-api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /fake-api/requirements.txt 

COPY fake-api/app /fake-api/app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]