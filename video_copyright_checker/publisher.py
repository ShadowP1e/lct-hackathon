import os
from typing import Any

import pika
import json

from dotenv import load_dotenv

from settings import config

load_dotenv()

RABBIT_HOST = config.RABBITMQ_HOST
RABBITMQ_USER = config.RABBITMQ_USER
RABBITMQ_PASSWORD = config.RABBITMQ_PASSWORD

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
parameters = pika.ConnectionParameters(RABBIT_HOST, 5672, '/', credentials)


def send_to_queue(data: Any):
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(
        queue='backend-api'
    )
    data = json.dumps(data)
    channel.basic_publish(
        exchange='',
        routing_key='backend-api',
        body=data.encode(),
    )
    connection.close()
    print(" [x] Data published successfully!")
