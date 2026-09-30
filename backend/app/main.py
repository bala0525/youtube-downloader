from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.youtube import router as youtube_router


app = FastAPI(
    title="YT Downloader API",
    description="Local YouTube Downloader API",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
<<<<<<< HEAD
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://youtube-downloader-engk08h6j-bxlxrxmxn.vercel.app",
    "https://youtube-downloader-6surf53n7-bxlxrxmxn.vercel.app",
],
=======
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],

>>>>>>> c0ec93b (Changed to run on the local host)
    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ---------------------------------------------------------
# YOUTUBE ROUTES
# ---------------------------------------------------------

app.include_router(
    youtube_router,
    prefix="/api/youtube",
    tags=["YouTube"],
)


# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------

@app.get("/")
def root():

    return {
        "success": True,
<<<<<<< HEAD
        "message": "YT Downloader API is running.",
    }
=======
        "message": "YT Downloader API is running locally.",
    }
>>>>>>> c0ec93b (Changed to run on the local host)
