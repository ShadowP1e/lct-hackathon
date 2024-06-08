FROM python:3.11-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y curl

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
