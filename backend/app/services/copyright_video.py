import io
from uuid import UUID, uuid4

from core.exceptions import NotFoundError
from schemas.video import VideoCreateSchema, CopyrightVideoSchema
from utils.unitofwork import IUnitOfWork
from services.s3 import MinioClient
import publisher


class CopyrightVideoService:
    @staticmethod
    async def create(uow: IUnitOfWork, schema: VideoCreateSchema, file: io.BytesIO) -> CopyrightVideoSchema:
        async with uow:
            s3_uuid = str(uuid4())
            filename = s3_uuid + '.' + schema.filename.split('.')[-1]
            url = MinioClient().upload_file('copyright-videos', file, filename)
            schema.url = url

            video = await uow.copyright_video.create(schema.model_dump())

            await uow.session.refresh(video)

            data = {
                'id': str(video.id),
                'type': 'add_copyright_video',
                'filetype': schema.filename.split('.')[-1],
                's3_uuid': s3_uuid,
                's3_url': url,
            }
            await publisher.send_to_queue('video_copyright_checker', data)

            await uow.commit()

            return CopyrightVideoSchema.model_validate(video, from_attributes=True)

    @staticmethod
    async def get(uow: IUnitOfWork, **filters) -> CopyrightVideoSchema:
        async with uow:
            video = await uow.copyright_video.get(**filters)

            if not video:
                raise NotFoundError('Video with this id not found')

            await uow.commit()

            return CopyrightVideoSchema.model_validate(video, from_attributes=True)

    @staticmethod
    async def delete(uow: IUnitOfWork, _id: UUID) -> None:
        video = await uow.copyright_video.get(id=_id)

        if video is not None:
            await uow.copyright_video.delete(_id)
            await uow.commit()
