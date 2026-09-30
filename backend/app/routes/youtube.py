import os
import re
import uuid
import threading

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.downloader import (
    get_video_info,
    download_video,
    jobs,
    jobs_lock,
)


router = APIRouter()


# ---------------------------------------------------------
# DOWNLOAD DIRECTORY
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

DOWNLOAD_DIR = BASE_DIR / "downloads"

DOWNLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------
# REQUEST MODELS
# ---------------------------------------------------------

class VideoInfoRequest(BaseModel):

    url: str


class DownloadRequest(BaseModel):

    url: str
    quality: str


# ---------------------------------------------------------
# YOUTUBE URL VALIDATION
# ---------------------------------------------------------

def is_valid_youtube_url(url: str):

    pattern = re.compile(
        r"^(https?://)?"
        r"(www\.)?"
        r"(youtube\.com|youtu\.be)/.+$",
        re.IGNORECASE,
    )

    return bool(
        pattern.match(
            url.strip()
        )
    )


# ---------------------------------------------------------
# VIDEO INFO
# ---------------------------------------------------------

@router.post("/info")
def video_info(
    request: VideoInfoRequest,
):

    url = request.url.strip()

    if not is_valid_youtube_url(url):

        raise HTTPException(
            status_code=400,
            detail="Please enter a valid YouTube URL.",
        )

    try:

        return get_video_info(url)

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


# ---------------------------------------------------------
# START DOWNLOAD
# ---------------------------------------------------------

@router.post("/download")
def start_download(
    request: DownloadRequest,
):

    url = request.url.strip()

    quality = request.quality.strip()


    if not is_valid_youtube_url(url):

        raise HTTPException(
            status_code=400,
            detail="Invalid YouTube URL.",
        )


    allowed_qualities = [
        "360p",
        "480p",
        "720p",
        "1080p",
        "1440p",
        "2160p",
    ]


    if quality not in allowed_qualities:

        raise HTTPException(
            status_code=400,
            detail="Invalid video quality.",
        )


    job_id = str(
        uuid.uuid4()
    )


    with jobs_lock:

        jobs[job_id] = {

            "status": "queued",

            "progress": 0,

            "message": "Download queued.",
        }


    def worker():

        try:

            download_video(
                url=url,
                quality=quality,
                job_id=job_id,
            )

        except Exception:

            pass


    thread = threading.Thread(

        target=worker,

        daemon=True,
    )

    thread.start()


    return {

        "success": True,

        "job_id": job_id,

        "message": "Download started.",
    }


# ---------------------------------------------------------
# DOWNLOAD PROGRESS
# ---------------------------------------------------------

@router.get(
    "/progress/{job_id}"
)
def download_progress(
    job_id: str,
):

    with jobs_lock:

        job = jobs.get(job_id)


    if not job:

        raise HTTPException(

            status_code=404,

            detail="Download job not found.",
        )


    response = {

        "job_id": job_id,

        "status": job.get(
            "status",
            "unknown",
        ),

        "progress": job.get(
            "progress",
            0,
        ),

        "message": job.get(
            "message",
            "",
        ),

        "speed": job.get(
            "speed",
            0,
        ),

        "eta": job.get(
            "eta",
        ),
    }


    if job.get("status") == "completed":

        response["download_url"] = (

            f"/api/youtube/file/"
            f"{job_id}/"
            f"{job.get('filename')}"

        )

        response["filename"] = job.get(
            "filename"
        )


    return response


# ---------------------------------------------------------
# SERVE DOWNLOADED FILE
# ---------------------------------------------------------

@router.get(
    "/file/{job_id}/{filename:path}"
)
def download_file(
    job_id: str,
    filename: str,
):

    safe_job_id = os.path.basename(
        job_id
    )

    safe_filename = os.path.basename(
        filename
    )


    file_path = os.path.join(

        str(DOWNLOAD_DIR),

        safe_job_id,

        safe_filename,
    )


    if not os.path.isfile(
        file_path
    ):

        raise HTTPException(

            status_code=404,

            detail="File not found.",
        )


    return FileResponse(

        path=file_path,

        filename=safe_filename,

        media_type="video/mp4",
    )