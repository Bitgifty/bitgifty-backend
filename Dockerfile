FROM python:3.8.12-alpine3.15

ADD ./requirements.txt /app/requirements.txt


RUN apk upgrade -U \
    && rm -rf /var/cache/*

ADD . /app
WORKDIR /app

RUN pip install -r /app/requirements.txt

RUN python /app/manage.py makemigrations

RUN python /app/manage.py migrate

ENV PATH /env/bin:$PATH

EXPOSE 8000


CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "BinanceGift.wsgi:application"]

