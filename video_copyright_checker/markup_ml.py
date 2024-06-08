from moviepy.editor import VideoFileClip
from io import BytesIO
import tempfile
import os
import random


def get_video_duration(video_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(video_bytes)
        temp_file_path = temp_file.name

    video = VideoFileClip(temp_file_path)

    duration = video.duration

    video.close()

    os.remove(temp_file_path)

    return duration


def video_copyright_check(video_bytes):
    duration = get_video_duration(video_bytes)
    print(duration)
    n = random.randint(1, 3)
    print(n)
    intervals = []
    for i in range(n):
        start = random.randint(0, int(duration) - 1)
        end = random.randint(start + 1, int(duration))
        intervals.append([start, end])

    print(intervals)
    return intervals
