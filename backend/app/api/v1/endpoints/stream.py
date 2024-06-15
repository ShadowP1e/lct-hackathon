from fastapi import APIRouter, Request, Header
from fastapi.responses import Response, StreamingResponse

from services.s3 import MinioClient
from core.exceptions import NotFoundError

router = APIRouter(
    prefix="/stream",
    tags=["stream"],
)


CHUNK_SIZE = 1024*1024  # 1 MB


@router.get("/{bucket}/{object_name}")
async def stream_video(bucket: str, object_name: str, request: Request, range: str = Header(None)):
    object_stat = MinioClient().stat_object(bucket, object_name)
    file_size = object_stat.size
    content_type = object_stat.content_type

    if range:
        range = range.strip().lower()
        range_start, range_end = range.replace("bytes=", "").split("-")
        range_start = int(range_start)
        range_end = int(range_end) if range_end else range_start + CHUNK_SIZE
        chunk_size = range_end - range_start

        response = MinioClient().get_object(bucket, object_name, offset=range_start, length=chunk_size)

        if not response:
            raise NotFoundError("Not found object")

        headers = {
            "Content-Range": f"bytes {range_start}-{min(range_end, file_size - 1)}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(len(response)),
            "Content-Type": content_type,
        }
        return Response(response, status_code=206, headers=headers, media_type=content_type)

    else:
        response = MinioClient().get_object(bucket, object_name)

        if not response:
            raise NotFoundError("Not found object")

        headers = {
            "Content-Length": str(file_size),
            "Content-Type": content_type,
        }
        return Response(response, status_code=200, headers=headers, media_type=content_type)
