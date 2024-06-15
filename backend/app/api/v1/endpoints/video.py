import io
import os
import shutil
import tempfile
import zipfile
from uuid import UUID

from fastapi import APIRouter, UploadFile, File
import magic

from core.exceptions import BadRequestError
from services.video import VideoService
from schemas.video import VideoCreateSchema, VideoSchema, ListVideoResponse
from core.dependencies import current_user_ip, UOW
from utils.file_types import allowed_video_types, allowed_zip_types

router = APIRouter(
    prefix="/videos",
    tags=["videos"],
)


@router.post('/upload')
async def upload_file(uow: UOW, user_ip: current_user_ip,
                      file: UploadFile = File(...)) -> VideoSchema | list[VideoSchema]:
    print(file.content_type)

    if file.content_type in allowed_zip_types:
        with tempfile.TemporaryDirectory() as temp_dir:

            temp_zip_path = os.path.join(temp_dir, file.filename)

            with open(temp_zip_path, "wb") as temp_file:
                shutil.copyfileobj(file.file, temp_file)

            extraction_path = os.path.join(temp_dir, 'extracted')
            os.makedirs(extraction_path, exist_ok=True)

            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(extraction_path)

            extracted_files = os.listdir(extraction_path)

            mime = magic.Magic(mime=True)

            response = []

            for file_name in extracted_files:
                file_path = os.path.join(extraction_path, file_name)

                try:
                    file_mime_type = mime.from_file(file_path)
                except IsADirectoryError:
                    raise BadRequestError("Allowed zip with video files")

                if file_mime_type in allowed_video_types:
                    file = open(file_path, 'rb')
                    file_data = file.read()

                    schema = VideoCreateSchema(
                        filename=file_name,
                        user_ip=user_ip
                    )

                    response_schema = await VideoService().create(uow,
                                                                  schema,
                                                                  file_data,
                                                                  file_mime_type
                                                                  )
                    response.append(response_schema)

            return response

    elif file.content_type in allowed_video_types:

        schema = VideoCreateSchema(
            filename=file.filename,
            user_ip=user_ip
        )

        response_schema = await VideoService().create(uow, schema, (await file.read()), file.content_type)

        return response_schema

    else:
        raise BadRequestError("Invalid file type. Only video files (or zip) are allowed.")


@router.get('/{video_id}', response_model=VideoSchema)
async def get_video(uow: UOW, video_id: UUID):
    response_schema = await VideoService.get(uow, id=video_id)
    return response_schema


@router.get('', response_model=ListVideoResponse)
async def get_list_video(uow: UOW, limit: int = 10, offset: int = 0):
    response_schema = await VideoService.get_list(uow, limit, offset)
    return response_schema
