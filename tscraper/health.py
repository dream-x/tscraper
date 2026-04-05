from fastapi import FastAPI, status
from fastapi.responses import JSONResponse, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime

app = FastAPI()
start_time = datetime.now()

# Shared state — set by the scraper at runtime
_scraper_status: dict = {"connected": False, "last_error": None}


def set_scraper_status(*, connected: bool, last_error: str | None = None):
    _scraper_status["connected"] = connected
    _scraper_status["last_error"] = last_error


@app.get("/health")
async def health_check():
    connected = _scraper_status["connected"]
    payload = {
        "status": "healthy" if connected else "degraded",
        "scraper_connected": connected,
        "uptime": str(datetime.now() - start_time),
        "timestamp": datetime.now().isoformat(),
    }
    if _scraper_status["last_error"]:
        payload["last_error"] = _scraper_status["last_error"]

    code = status.HTTP_200_OK if connected else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=code, content=payload)


@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
