FROM python:3.8.12-alpine3.15

ADD ./requirements.txt /app/requirements.txt


RUN apk update && apk upgrade

RUN apk add --no-cache --virtual .build-deps postgresql-dev build-base gcc && rm -rf /var/cache/apk/*

ADD . /app
WORKDIR /app

RUN pip install -r /app/requirements.txt

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "BinanceGift.wsgi:application"]

