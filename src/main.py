from os import getenv
from pathlib import Path
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from yt_dlp import YoutubeDL, match_filter_func

load_dotenv()
DURATION_MAX = getenv("DURATION_MAX")
FORMAT = getenv("FORMAT")
FORMAT_SORT = getenv("FORMAT_SORT")
ENCODING = "UTF-8"

app = FastAPI()


@app.get("/download")
def download(
    video_url: str,
    duration_max: int | None = DURATION_MAX,
    format: str | None = FORMAT,
    format_sort: str | None = FORMAT_SORT,
) -> Response:
    filename = str(uuid4())
    file = download_video(video_url, filename, duration_max, format, format_sort)
    file = file or download_thumbnail(video_url, filename)
    return FileResponse(file, background=BackgroundTask(file.unlink))


def download_video(
    video_url: str,
    filename: str,
    duration_max: int | None,
    format: str | None,
    format_sort: str | None,
) -> Path | None:
    params = prepare_target_params(filename)
    if format is not None:
        params["format"] = format
    if format_sort is not None:
        params["format_sort"] = [format_sort]
    if duration_max is not None:
        params["match_filter"] = match_filter_func(f"duration<={duration_max}")
    return download_file(params, video_url, filename)


def download_thumbnail(video_url: str, filename: str) -> Path | None:
    params = prepare_target_params(filename) | {
        "writethumbnail": True,
        "skip_download": True,
    }
    return download_file(params, video_url, filename)


def prepare_target_params(filename: str) -> dict[str, str]:
    return {"outtmpl": f"{filename}.%(ext)s"}


def download_file(params: dict[str, Any], video_url: str, filename: str) -> Path | None:
    with YoutubeDL(params) as ytdl:
        ytdl.download(video_url)
    return find_downloaded_file(filename)


def find_downloaded_file(name: str) -> Path | None:
    return next((f for f in Path().iterdir() if f.is_file() and f.stem == name), None)
