import json
import os
import threading
from typing import Any
from uuid import uuid4
from time import sleep

import pika
from dotenv import load_dotenv

from scripts.storage import setup_db
from scripts.fingerprint import register_video, register_directory
from scripts.recognise import recognise_video, recognise_directory

from settings import config
import publisher
from utils import download_file, cut_clip
from s3_client import MinioClient

load_dotenv()

RABBIT_HOST = config.RABBITMQ_HOST
RABBITMQ_USER = config.RABBITMQ_USER
RABBITMQ_PASSWORD = config.RABBITMQ_PASSWORD

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
parameters = pika.ConnectionParameters(RABBIT_HOST, 5672, '/', credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue='video_copyright_checker')
channel.basic_qos(prefetch_count=1)


def add_copyright_video_handler(data: Any):
    file_content = MinioClient().get_object(data['s3_bucket_name'], data['s3_filename'])

    with open(f"dummy_index/{data['user_filename']}", 'wb') as file:
        file.write(file_content)

    register_video(f'dummy_index/{data["user_filename"]}')

    os.remove(f"dummy_index/{data['user_filename']}")

    result = {
        'video_id': data['id'],
        'type': data['type']
    }

    publisher.send_to_queue(result)


def check_copyright_video_handler(data: Any):
    file_content = MinioClient().get_object(data['s3_bucket_name'], data['s3_filename'])

    with open(f"dummy_val/{data['user_filename']}", 'wb') as file:
        file.write(file_content)

    pred = recognise_video(f"dummy_val/{data['user_filename']}")
    if pred != (None, None):
        from_filename = pred[0][:-4]
        start = pred[1][0]
        end = pred[1][1]
        intervals = [[start, end]]
    else:
        intervals = []

    copyright_parts = []
    for (start, end) in intervals:
        clip = cut_clip(file_content, start, end)

        filename = str(uuid4()) + '.' + data['filetype']
        bucket_name = 'copyright-parts'
        url = MinioClient().upload_file(bucket_name, clip, filename)

        copyright_parts.append(
            {
                's3_filename': filename,
                's3_bucket_name': bucket_name,
                'from_filename': from_filename,
                'start': start,
                'end': end,
            }
        )

    os.remove(f"dummy_val/{data['user_filename']}")

    result = {
        'video_id': data['id'],
        'data': copyright_parts,
        'type': data['type']
    }
    publisher.send_to_queue(result)


def callback(ch, method, properties, body):
    global threads
    data = json.loads(body)
    print(" [x] Received dictionary:", data)

    ch.basic_ack(delivery_tag=method.delivery_tag)
    if data['type'] == 'add_copyright_video':
        t = threading.Thread(target=add_copyright_video_handler, args=(data, ))
        t.start()
        threads.append(t)

    elif data['type'] == 'check_copyright_video':
        t = threading.Thread(target=check_copyright_video_handler, args=(data, ))
        t.start()
        threads.append(t)


threads = []
setup_db()

channel.basic_consume(queue='video_copyright_checker', on_message_callback=callback, auto_ack=False)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

for thread in threads:
    thread.join()
