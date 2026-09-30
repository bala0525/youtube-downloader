import os
import threading

from pathlib import Path

import yt_dlp


# ---------------------------------------------------------
# BASE DIRECTORY
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------
# DOWNLOAD DIRECTORY
# ---------------------------------------------------------

DOWNLOAD_DIR = BASE_DIR / "downloads"

DOWNLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------
# JOB STORAGE
# ---------------------------------------------------------

jobs = {}

jobs_lock = threading.Lock()


def update_job(
    job_id,
    **data,
):

    with jobs_lock:

        if job_id not in jobs:

            jobs[job_id] = {}

        jobs[job_id].update(data)


def get_job(
    job_id,
):

    with jobs_lock:

        return jobs.get(
            job_id,
            {},
        ).copy()


# ---------------------------------------------------------
# GET VIDEO INFORMATION
# ---------------------------------------------------------

def get_video_info(
    url: str,
):

    options = {

        "quiet": True,

        "no_warnings": True,

        "skip_download": True,

        "noplaylist": True,

        # Select best available formats.
        "format": "bestvideo+bestaudio/best",
    }


    with yt_dlp.YoutubeDL(
        options
    ) as ydl:

        info = ydl.extract_info(
            url,
            download=False,
        )


    # -----------------------------------------------------
    # COLLECT AVAILABLE QUALITIES
    # -----------------------------------------------------

    available_heights = set()


    for fmt in info.get(
        "formats",
        [],
    ):

        height = fmt.get(
            "height"
        )


        if not height:

            continue


        if height in [
            360,
            480,
            720,
            1080,
            1440,
            2160,
        ]:

            available_heights.add(
                height
            )


    quality_order = [

        (360, "360p"),

        (480, "480p"),

        (720, "720p"),

        (1080, "1080p"),

        (1440, "1440p"),

        (2160, "2160p"),
    ]


    formats = []


    for height, label in quality_order:

        if height in available_heights:

            formats.append({

                "quality": label,

                "height": height,

                "extension": "mp4",
            })


    return {

        "title": info.get(
            "title"
        ),

        "thumbnail": info.get(
            "thumbnail"
        ),

        "duration": info.get(
            "duration"
        ),

        "uploader": info.get(
            "uploader"
        ),

        "formats": formats,
    }


# ---------------------------------------------------------
# PROGRESS HOOK
# ---------------------------------------------------------

def create_progress_hook(
    job_id,
):

    def progress_hook(
        data,
    ):

        status = data.get(
            "status"
        )


        if status == "downloading":

            downloaded = (
                data.get(
                    "downloaded_bytes"
                )
                or 0
            )


            total = (
                data.get(
                    "total_bytes"
                )
                or data.get(
                    "total_bytes_estimate"
                )
                or 0
            )


            percentage = 0


            if total > 0:

                percentage = (
                    downloaded / total
                ) * 100


            speed = (
                data.get(
                    "speed"
                )
                or 0
            )


            eta = data.get(
                "eta"
            )


            update_job(

                job_id,

                status="downloading",

                progress=round(
                    percentage,
                    1,
                ),

                downloaded_bytes=downloaded,

                total_bytes=total,

                speed=speed,

                eta=eta,
            )


        elif status == "finished":

            update_job(

                job_id,

                status="processing",

                progress=100,

                message=(
                    "Merging video and audio..."
                ),
            )


    return progress_hook


# ---------------------------------------------------------
# DOWNLOAD VIDEO
# ---------------------------------------------------------

def download_video(
    url: str,
    quality: str,
    job_id: str,
):

    quality_heights = {

        "360p": 360,

        "480p": 480,

        "720p": 720,

        "1080p": 1080,

        "1440p": 1440,

        "2160p": 2160,
    }


    if quality not in quality_heights:

        raise ValueError(
            "Unsupported quality."
        )


    height = quality_heights[
        quality
    ]


    # -----------------------------------------------------
    # JOB DIRECTORY
    # -----------------------------------------------------

    job_directory = (
        DOWNLOAD_DIR / job_id
    )


    job_directory.mkdir(
        parents=True,
        exist_ok=True,
    )


    output_template = str(
        job_directory /
        "%(title)s [%(id)s].%(ext)s"
    )


    update_job(

        job_id,

        status="starting",

        progress=0,

        message="Starting download...",
    )


    # -----------------------------------------------------
    # YT-DLP OPTIONS
    # -----------------------------------------------------

    options = {

        # Try requested quality first.
        # Then fall back to the best available
        # combined format.
        "format": (
            f"bestvideo[height<={height}]"
            f"+bestaudio/"
            f"best[height<={height}]/"
            f"best"
        ),

        "outtmpl": output_template,

        "merge_output_format": "mp4",

        "noplaylist": True,

        "quiet": True,

        "no_warnings": True,

        "progress_hooks": [
            create_progress_hook(
                job_id
            )
        ],

        "overwrites": True,
    }


    # -----------------------------------------------------
    # DOWNLOAD
    # -----------------------------------------------------

    try:

        with yt_dlp.YoutubeDL(
            options
        ) as ydl:

            ydl.download([
                url
            ])


        # -------------------------------------------------
        # FIND FILE
        # -------------------------------------------------

        files = list(
            job_directory.iterdir()
        )


        media_files = [

            file

            for file in files

            if file.is_file()

            and not file.name.endswith(
                ".part"
            )

            and not file.name.endswith(
                ".ytdl"
            )

        ]


        if not media_files:

            raise FileNotFoundError(
                "Downloaded file was not found."
            )


        # Prefer MP4.
        mp4_files = [

            file

            for file in media_files

            if file.suffix.lower()
            == ".mp4"

        ]


        if mp4_files:

            final_file = mp4_files[0]

        else:

            final_file = media_files[0]


        # -------------------------------------------------
        # COMPLETED
        # -------------------------------------------------

        update_job(

            job_id,

            status="completed",

            progress=100,

            filename=final_file.name,

            file_path=str(
                final_file
            ),

            message="Download completed.",
        )


        return str(
            final_file
        )


    except Exception as error:

        update_job(

            job_id,

            status="error",

            progress=0,

            message=str(error),
        )

        raise