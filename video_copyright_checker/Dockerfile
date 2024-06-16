FROM python:3.11-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y ffmpeg libavcodec-extra curl python3-dev libportaudio2 libportaudiocpp0 portaudio19-dev build-essential

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
