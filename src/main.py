from os import getenv
from pathlib import Path
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from loguru import logger
from starlette.background import BackgroundTask
from yt_dlp import YoutubeDL, match_filter_func

load_dotenv()

DEFAULT_MAX_DURATION = getenv("MAX_DURATION")
DEFAULT_FORMAT = getenv("FORMAT")
DEFAULT_FORMAT_SORT = getenv("FORMAT_SORT")

ENCODING = "UTF-8"
THUMBNAIL_PARAMS = {"writethumbnail": True, "skip_download": True}

app = FastAPI()


@app.get("/download")
def download(
    video_url: str,
    max_duration: int | None = DEFAULT_MAX_DURATION,
    format: str | None = DEFAULT_FORMAT,
    format_sort: str | None = DEFAULT_FORMAT_SORT,
) -> Response:
    logger.info(f"[{video_url}] Received request")
    filename = str(uuid4())
    params = video_params(max_duration, format, format_sort)
    file = download_file(video_url, filename, params)
    if not file:
        logger.info(f"[{video_url}] Falling back to thumbnail")
        file = download_file(video_url, filename, THUMBNAIL_PARAMS)
    return FileResponse(file, background=BackgroundTask(file.unlink))


def video_params(
    max_duration: int | None,
    format: str | None,
    format_sort: str | None,
) -> dict[str, Any]:
    params = {}
    if format is not None:
        params["format"] = format
    if format_sort is not None:
        params["format_sort"] = [format_sort]
    if max_duration:
        params["match_filter"] = match_filter_func(f"duration<={max_duration}")
    return params


def download_file(video_url: str, filename: str, params: dict[str, Any]) -> Path | None:
    with YoutubeDL({"outtmpl": f"{filename}.%(ext)s"} | params) as ytdl:
        ytdl.download(video_url)
    return find_downloaded_file(filename)


def find_downloaded_file(name: str) -> Path | None:
    return next((f for f in Path().iterdir() if f.is_file() and f.stem == name), None)
