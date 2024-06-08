import json
from typing import Any
from uuid import uuid4
from time import sleep

import pika
from dotenv import load_dotenv

from config import config
import publisher
from utils import download_file, cut_clip
from s3_client import MinioClient
from markup_ml import video_copyright_check

load_dotenv()

RABBIT_HOST = config.RABBITMQ_HOST
RABBITMQ_USER = config.RABBITMQ_USER
RABBITMQ_PASSWORD = config.RABBITMQ_PASSWORD

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
parameters = pika.ConnectionParameters(RABBIT_HOST, 5672, '/', credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue='video_copyright_checker')


def add_copyright_video_handler(data: Any):
    file_content = download_file(data['s3_url'])

    sleep(20)  # make some ml changes

    result = {
        'video_id': data['id'],
        'type': data['type']
    }

    publisher.send_to_queue(result)


def check_copyright_video_handler(data: Any):
    file_content = download_file(data['s3_url'])

    intervals = video_copyright_check(file_content)  # change to normal function

    copyright_parts = []
    for (start, end) in intervals:
        clip = cut_clip(file_content, start, end)

        filename = str(uuid4()) + '.' + data['filetype']
        url = MinioClient().upload_file('copyright-parts', clip, filename)

        copyright_parts.append(
            {
                's3_url': url,
                'start': start,
                'end': end,
            }
        )

    sleep(20)

    result = {
        'video_id': data['id'],
        'data': copyright_parts,
        'type': data['type']
    }
    publisher.send_to_queue(result)


def callback(ch, method, properties, body):
    data = json.loads(body)
    print(" [x] Received dictionary:", data)

    if data['type'] == 'add_copyright_video':
        add_copyright_video_handler(data)

    elif data['type'] == 'check_copyright_video':
        check_copyright_video_handler(data)

    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(queue='video_copyright_checker', on_message_callback=callback, auto_ack=False)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
