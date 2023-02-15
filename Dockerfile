FROM python:3.10-slim-bullseye

ADD ./requirements.txt /app/requirements.txt

ADD . /app
WORKDIR /app

RUN pip install -r /app/requirements.txt

RUN python /app/manage.py collectstatic --no-input

EXPOSE 8000

# Render wan kill me