from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
import asyncio
from datetime import datetime

app = FastAPI()
start_time = datetime.now()

@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "uptime": str(datetime.now() - start_time),
            "timestamp": datetime.now().isoformat()
        }
    )
