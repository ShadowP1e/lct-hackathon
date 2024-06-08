import io
from uuid import UUID, uuid4

from core.exceptions import NotFoundError
from schemas.video import VideoCreateSchema, VideoSchema, AddCopyrightVideoPartSchema, ListVideoResponse
from utils.unitofwork import IUnitOfWork
from services.s3 import MinioClient
import publisher


class VideoService:
    @staticmethod
    async def create(uow: IUnitOfWork, schema: VideoCreateSchema, file: io.BytesIO) -> VideoSchema:
        async with uow:
            s3_uuid = str(uuid4())
            filename = s3_uuid + '.' + schema.filename.split('.')[-1]
            url = MinioClient().upload_file('upload-videos', file, filename)
            schema.url = url

            video = await uow.video.create(schema.model_dump())

            await uow.session.refresh(video)

            data = {
                'id': str(video.id),
                'type': 'check_copyright_video',
                'filetype': schema.filename.split('.')[-1],
                's3_uuid': s3_uuid,
                's3_url': url,
            }
            await publisher.send_to_queue('video_copyright_checker', data)

            await uow.commit()

            return VideoSchema.model_validate(video, from_attributes=True)

    @staticmethod
    async def get(uow: IUnitOfWork, **filters) -> VideoSchema:
        async with uow:
            video = await uow.video.get(**filters)

            if not video:
                raise NotFoundError('Video with this id not found')

            await uow.commit()

            return VideoSchema.model_validate(video, from_attributes=True)

    @staticmethod
    async def delete(uow: IUnitOfWork, _id: UUID) -> None:
        video = await uow.video.get(id=_id)

        if video is not None:
            await uow.video.delete(_id)
            await uow.commit()

    @staticmethod
    async def get_list(uow: IUnitOfWork, limit: int = None, offset: int = None, order_by: str = None,
                       reverse: bool = False, **filter_by):
        async with uow:
            videos = await uow.video.get_list(limit, offset, order_by, reverse, **filter_by)

            await uow.commit()

            return ListVideoResponse.model_validate(videos, from_attributes=True)

    @staticmethod
    async def add_copyright_video_part(uow: IUnitOfWork, schema: AddCopyrightVideoPartSchema) -> None:
        await uow.copyright_video_part.create(schema.model_dump())
        await uow.commit()

    @staticmethod
    async def remove_copyright_video_part(uow: IUnitOfWork, _id: UUID) -> None:
        video = await uow.copyright_video_part.get(id=_id)

        if video is not None:
            await uow.copyright_video_part.delete(_id)
            await uow.commit()
