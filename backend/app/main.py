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
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
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
        "message": "YT Downloader API is running locally.",
    }