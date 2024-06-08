import io
from uuid import UUID

from fastapi import APIRouter, UploadFile, File

from core.exceptions import BadRequestError
from services.copyright_video import CopyrightVideoService
from schemas.video import VideoCreateSchema, VideoSchema, ListVideoResponse, CopyrightVideoSchema
from core.dependencies import current_user_or_error, UOW, current_user_ip
from utils.video_types import allowed_video_types

router = APIRouter(
    prefix="/copyright-videos",
    tags=["copyright-videos"],
)


@router.post('/upload', response_model=CopyrightVideoSchema)
async def upload_file(uow: UOW, current_user: current_user_or_error,
                      user_ip: current_user_ip, file: UploadFile = File(...)):
    if file.content_type not in allowed_video_types:
        raise BadRequestError("Invalid file type. Only video files are allowed.")

    schema = VideoCreateSchema(
        filename=file.filename,
        user_ip=user_ip
    )
    contents = io.BytesIO(await file.read())

    response_schema = await CopyrightVideoService().create(uow, schema, contents)

    return response_schema


@router.get('/{video_id}', response_model=CopyrightVideoSchema)
async def get_video(uow: UOW, video_id: UUID, current_user: current_user_or_error):
    response_schema = await CopyrightVideoService.get(uow, id=video_id)
    return response_schema
