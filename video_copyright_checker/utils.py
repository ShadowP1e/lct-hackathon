import os
import tempfile
import io

import requests
from moviepy.editor import VideoFileClip
from urllib.parse import urljoin, urlparse


def download_file(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        return None


def cut_clip(video_bytes, start_time, end_time):
    # Write the video bytes to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(video_bytes)
        temp_file_path = temp_file.name

    # Load the video from the temporary file
    video = VideoFileClip(temp_file_path)

    # Cut the clip
    clipped_video = video.subclip(start_time, end_time)

    # Write the clipped video to a temporary file
    clipped_temp_file_path = temp_file_path.replace(".mp4", "_clipped.mp4")
    clipped_video.write_videofile(clipped_temp_file_path, codec="libx264", fps=video.fps)

    # Close the video file
    video.close()

    # Read the bytes of the resulting video
    with open(clipped_temp_file_path, "rb") as clipped_temp_file:
        result_bytes = clipped_temp_file.read()

    # Clean up temporary files
    os.remove(temp_file_path)
    os.remove(clipped_temp_file_path)

    return io.BytesIO(result_bytes)


def remove_query_params(url: str) -> str:
    return urljoin(url, urlparse(url).path)
