FROM python:3.10-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


ADD ./requirements.txt /app/requirements.txt

ADD . /app
WORKDIR /app

RUN pip install -r /app/requirements.txt

EXPOSE 8000

# RUN python /app/manage.py collectstatic --no-input

# define the default command to run when starting the container
# CMD ["gunicorn", "--chdir", "demo", "--bind", ":8000", "BinanceGift.wsgi:application"]