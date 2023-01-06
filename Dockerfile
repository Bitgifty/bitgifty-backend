FROM python:3.10.8-alpine3.15

ADD ./requirements.txt /app/requirements.txt

ADD . /app
WORKDIR /app

RUN pip install -r /app/requirements.txt

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "BinanceGift.wsgi:application"]

# Render wan kill me