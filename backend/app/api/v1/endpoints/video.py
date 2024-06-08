import io
from uuid import UUID

from fastapi import APIRouter, UploadFile, File

from core.exceptions import BadRequestError
from services.video import VideoService
from schemas.video import VideoCreateSchema, VideoSchema, ListVideoResponse
from core.dependencies import current_user_ip, UOW
from utils.video_types import allowed_video_types

router = APIRouter(
    prefix="/videos",
    tags=["videos"],
)


@router.post('/upload', response_model=VideoSchema)
async def upload_file(uow: UOW, user_ip: current_user_ip, file: UploadFile = File(...)):
    if file.content_type not in allowed_video_types:
        raise BadRequestError("Invalid file type. Only video files are allowed.")

    schema = VideoCreateSchema(
        filename=file.filename,
        user_ip=user_ip
    )
    contents = io.BytesIO(await file.read())

    response_schema = await VideoService().create(uow, schema, contents)

    return response_schema


@router.get('/{video_id}', response_model=VideoSchema)
async def get_video(uow: UOW, video_id: UUID):
    response_schema = await VideoService.get(uow, id=video_id)
    return response_schema


@router.get('', response_model=ListVideoResponse)
async def get_list_video(uow: UOW, limit: int = 10, offset: int = 0):
    response_schema = await VideoService.get_list(uow, limit, offset)
    return response_schema
