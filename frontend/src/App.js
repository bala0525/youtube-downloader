import React, { useEffect, useRef, useState } from "react";
import "./App.css";


// --------------------------------------------------
// LOCAL BACKEND API
// --------------------------------------------------

const API_URL = "http://localhost:8000";


function App() {

  const [url, setUrl] = useState("");

  const [video, setVideo] = useState(null);

  const [quality, setQuality] = useState("");

  const [loadingInfo, setLoadingInfo] = useState(false);

  const [startingDownload, setStartingDownload] =
    useState(false);

  const [downloadJob, setDownloadJob] = useState(null);

  const [error, setError] = useState("");


  const pollingRef = useRef(null);


  // --------------------------------------------------
  // CLEANUP
  // --------------------------------------------------

  useEffect(() => {

    return () => {

      if (pollingRef.current) {

        clearInterval(
          pollingRef.current
        );

      }

    };

  }, []);


  // --------------------------------------------------
  // GET VIDEO INFO
  // --------------------------------------------------

  const fetchVideoInfo = async () => {

    if (!url.trim()) {

      setError(
        "Please paste a YouTube URL."
      );

      return;
    }


    setLoadingInfo(true);

    setError("");

    setVideo(null);

    setDownloadJob(null);


    try {

      const response = await fetch(
        `${API_URL}/api/youtube/info`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            url: url.trim(),
          }),
        }
      );


      const data =
        await response.json();


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Unable to get video information."
        );

      }


      setVideo(data);


      // Select highest available quality
      if (
        data.formats &&
        data.formats.length > 0
      ) {

        const highest =
          data.formats[
            data.formats.length - 1
          ];

        setQuality(
          highest.quality
        );

      }

    } catch (error) {

      setError(
        error.message
      );

    } finally {

      setLoadingInfo(false);

    }

  };


  // --------------------------------------------------
  // START DOWNLOAD
  // --------------------------------------------------

  const startDownload = async () => {

    if (!video || !quality) {

      setError(
        "Please select a quality."
      );

      return;
    }


    setStartingDownload(true);

    setError("");

    setDownloadJob({
      status: "starting",
      progress: 0,
      message: "Starting download...",
    });


    try {

      const response = await fetch(
        `${API_URL}/api/youtube/download`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            url: url.trim(),
            quality: quality,
          }),
        }
      );


      const data =
        await response.json();


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Could not start download."
        );

      }


      setStartingDownload(false);

      startPolling(
        data.job_id
      );

    } catch (error) {

      setStartingDownload(false);

      setError(
        error.message
      );

      setDownloadJob(null);

    }

  };


  // --------------------------------------------------
  // POLL DOWNLOAD STATUS
  // --------------------------------------------------

  const startPolling = (jobId) => {

    if (pollingRef.current) {

      clearInterval(
        pollingRef.current
      );

    }


    const checkProgress =
      async () => {

        try {

          const response =
            await fetch(
              `${API_URL}/api/youtube/progress/${jobId}`
            );


          const data =
            await response.json();


          if (!response.ok) {

            throw new Error(
              data.detail ||
              "Unable to check download."
            );

          }


          setDownloadJob(data);


          if (
            data.status ===
            "completed"
          ) {

            clearInterval(
              pollingRef.current
            );

            pollingRef.current =
              null;

          }


          if (
            data.status ===
            "error"
          ) {

            clearInterval(
              pollingRef.current
            );

            pollingRef.current =
              null;

          }

        } catch (error) {

          clearInterval(
            pollingRef.current
          );

          pollingRef.current =
            null;

          setError(
            error.message
          );

        }

      };


    checkProgress();


    pollingRef.current =
      setInterval(
        checkProgress,
        1000
      );

  };


  // --------------------------------------------------
  // DOWNLOAD FILE
  // --------------------------------------------------

  const saveFile = () => {

    if (
      !downloadJob ||
      !downloadJob.download_url
    ) {

      return;

    }


    const link =
      document.createElement("a");


    link.href =
      `${API_URL}${downloadJob.download_url}`;


    link.download =
      downloadJob.filename ||
      "video.mp4";


    document.body.appendChild(
      link
    );


    link.click();


    document.body.removeChild(
      link
    );

  };


  // --------------------------------------------------
  // FORMAT FILE SIZE
  // --------------------------------------------------

  const formatBytes = (bytes) => {

    if (!bytes || bytes <= 0) {

      return "0 B";

    }


    const units = [
      "B",
      "KB",
      "MB",
      "GB",
      "TB",
    ];


    const index =
      Math.floor(
        Math.log(bytes) /
        Math.log(1024)
      );


    return (
      (
        bytes /
        Math.pow(
          1024,
          index
        )
      ).toFixed(1) +
      " " +
      units[index]
    );

  };


  // --------------------------------------------------
  // FORMAT SPEED
  // --------------------------------------------------

  const formatSpeed = (bytes) => {

    if (!bytes) {

      return "--";

    }


    return (
      formatBytes(bytes) +
      "/s"
    );

  };


  // --------------------------------------------------
  // FORMAT ETA
  // --------------------------------------------------

  const formatEta = (seconds) => {

    if (
      seconds === null ||
      seconds === undefined
    ) {

      return "--";

    }


    const minutes =
      Math.floor(
        seconds / 60
      );


    const secs =
      seconds % 60;


    return (
      `${minutes}:` +
      String(secs).padStart(
        2,
        "0"
      )
    );

  };


  // --------------------------------------------------
  // RESET
  // --------------------------------------------------

  const reset = () => {

    setUrl("");

    setVideo(null);

    setQuality("");

    setDownloadJob(null);

    setError("");


    if (pollingRef.current) {

      clearInterval(
        pollingRef.current
      );

      pollingRef.current =
        null;

    }

  };


  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  return (

    <div className="app">

      <header className="navbar">

        <div className="logo">

          <div className="logo-icon">
            ▶
          </div>

          <span>
            YT Downloader
          </span>

        </div>

        <div className="nav-badge">
          4K READY
        </div>

      </header>


      <main className="main">

        <section className="hero">

          <div className="hero-badge">
            FAST • SIMPLE • HIGH QUALITY
          </div>


          <h1>

            Download your

            <span>
              {" "}favorite videos
            </span>

          </h1>


          <p>

            Paste a YouTube URL and
            choose the highest available
            video quality.

          </p>


          <div className="url-box">

            <div className="url-input-wrapper">

              <span className="link-icon">
                🔗
              </span>


              <input

                type="text"

                value={url}

                onChange={(event) =>
                  setUrl(
                    event.target.value
                  )
                }

                onKeyDown={(event) => {

                  if (
                    event.key ===
                    "Enter"
                  ) {

                    fetchVideoInfo();

                  }

                }}

                placeholder="Paste YouTube URL here..."

              />


              {url && (

                <button

                  className="clear-button"

                  onClick={() =>
                    setUrl("")
                  }

                >

                  ×

                </button>

              )}

            </div>


            <button

              className="analyze-button"

              onClick={fetchVideoInfo}

              disabled={loadingInfo}

            >

              {loadingInfo
                ? "Analyzing..."
                : "Analyze"}

            </button>

          </div>


          {error && (

            <div className="error-box">

              ⚠ {error}

            </div>

          )}

        </section>


        {video && (

          <section className="video-section">

            <div className="video-card">

              <div className="thumbnail-container">

                <img

                  src={video.thumbnail}

                  alt={video.title}

                  className="thumbnail"

                />


                <div className="thumbnail-overlay">

                  {video.duration
                    ? `${Math.floor(
                        video.duration / 60
                      )}:${String(
                        video.duration % 60
                      ).padStart(2, "0")}`
                    : ""}

                </div>

              </div>


              <div className="video-info">

                <div className="channel">

                  {video.uploader ||
                    "YouTube"}

                </div>


                <h2>
                  {video.title}
                </h2>


                <div className="video-meta">

                  {video.duration && (

                    <span>

                      ⏱{" "}

                      {Math.floor(
                        video.duration /
                        60
                      )} min

                    </span>

                  )}


                  <span>

                    ✓ Video found

                  </span>

                </div>


                <button

                  className="change-button"

                  onClick={reset}

                >

                  Analyze another

                </button>

              </div>

            </div>


            <div className="download-panel">

              <div className="panel-title">

                Choose quality

              </div>


              <div className="quality-grid">

                {video.formats.map(
                  (format) => (

                    <button

                      key={
                        format.quality
                      }

                      className={
                        `quality-card ${
                          quality ===
                          format.quality
                            ? "selected"
                            : ""
                        }`
                      }

                      onClick={() =>
                        setQuality(
                          format.quality
                        )
                      }

                    >

                      <span className="quality-name">

                        {format.quality}

                      </span>


                      {format.quality ===
                        "2160p" && (

                        <span className="quality-badge">

                          4K

                        </span>

                      )}


                      {quality ===
                        format.quality && (

                        <span className="check">

                          ✓

                        </span>

                      )}

                    </button>

                  )
                )}

              </div>


              <button

                className="download-button"

                onClick={startDownload}

                disabled={
                  startingDownload ||
                  downloadJob?.status ===
                    "downloading" ||
                  downloadJob?.status ===
                    "processing"
                }

              >

                {startingDownload

                  ? "Starting..."

                  : downloadJob?.status ===
                    "downloading"

                  ? "Downloading..."

                  : downloadJob?.status ===
                    "processing"

                  ? "Processing..."

                  : `Download ${quality}`}

              </button>


              {downloadJob && (

                <div className="progress-container">

                  <div className="progress-header">

                    <span>

                      {downloadJob.message}

                    </span>


                    <strong>

                      {downloadJob.progress ||
                        0}%

                    </strong>

                  </div>


                  <div className="progress-bar">

                    <div

                      className="progress-fill"

                      style={{

                        width:
                          `${downloadJob.progress || 0}%`

                      }}

                    />

                  </div>


                  <div className="download-stats">

                    <span>

                      Speed:{" "}

                      {formatSpeed(
                        downloadJob.speed
                      )}

                    </span>


                    <span>

                      ETA:{" "}

                      {formatEta(
                        downloadJob.eta
                      )}

                    </span>

                  </div>


                  {downloadJob.status ===
                    "completed" && (

                    <button

                      className="save-button"

                      onClick={saveFile}

                    >

                      ⬇ Download video

                    </button>

                  )}


                  {downloadJob.status ===
                    "error" && (

                    <div className="error-box">

                      {downloadJob.message}

                    </div>

                  )}

                </div>

              )}

            </div>

          </section>

        )}


        {!video && (

          <section className="features">

            <div className="feature">

              <div className="feature-icon">

                ⚡

              </div>

              <h3>

                Fast

              </h3>

              <p>

                Direct download using
                yt-dlp.

              </p>

            </div>


            <div className="feature">

              <div className="feature-icon">

                4K

              </div>

              <h3>

                High Quality

              </h3>

              <p>

                2160p when the source
                provides it.

              </p>

            </div>


            <div className="feature">

              <div className="feature-icon">

                🔊

              </div>

              <h3>

                Audio Included

              </h3>

              <p>

                Video and audio are
                merged automatically.

              </p>

            </div>

          </section>

        )}

      </main>


      <footer>

        <span>

          YT Downloader

        </span>

        <span>

          Developed by Balaraman

        </span>

      </footer>

    </div>

  );

}


export default App;

