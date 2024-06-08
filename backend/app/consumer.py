import asyncio
import json
from typing import Any

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from core.config import config
from schemas.video import AddCopyrightVideoPartSchema
from services.video import VideoService
from utils.unitofwork import UnitOfWork

RABBIT_HOST = config.RABBITMQ_HOST
RABBITMQ_USER = config.RABBITMQ_USER
RABBITMQ_PASSWORD = config.RABBITMQ_PASSWORD


async def check_copyright_video_handler(data: Any):
    uow = UnitOfWork()
    async with uow:
        video = await uow.video.get(id=data['video_id'])
        video.finished = True

        uow.session.add(video)

        data = data['data']
        for item in data:
            schema = AddCopyrightVideoPartSchema(
                video_id=video.id,
                url=item['s3_url'],
                start=int(item['start']),
                end=int(item['end']),
            )
            await VideoService.add_copyright_video_part(uow, schema)

        await uow.commit()


async def add_copyright_video_handler(data: Any):
    uow = UnitOfWork()
    async with uow:
        video = await uow.copyright_video.get(id=data['video_id'])
        video.finished = True

        uow.session.add(video)

        await uow.commit()


async def receive_message():
    connection = await aio_pika.connect_robust(f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBIT_HOST}/")
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue('backend-api')

        async def on_message(message: AbstractIncomingMessage) -> None:
            data = message.body.decode()
            data = json.loads(data)
            print(" [x] Received dictionary :", data)

            if data['type'] == 'add_copyright_video':
                await add_copyright_video_handler(data)

            elif data['type'] == 'check_copyright_video':
                await check_copyright_video_handler(data)

            await message.ack()

        await queue.consume(on_message)
        await asyncio.Future()


def start_consumer():
    print(" [x] Start receiving")
    asyncio.run(receive_message())
