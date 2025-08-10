from typing import Dict

from fastapi import FastAPI
import uvicorn
import os
from dotenv import load_dotenv

from app.core.logger import logger

load_dotenv()

# set the log level from environment variable or default to "info"
UVICORN_PORT = os.getenv("UVICORN_PORT", "8000")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

app = FastAPI(title="FastAPI Project Management Mess", version="1.0.0")


@app.get("/", summary="Health Check", tags=["Health"], response_model=dict)
async def root() -> Dict[str, str]:
    """Root endpoint to check if the server is running. """
    logger.info("Health check endpoint hit")
    return {"status": "healthy", "message": "server is up"}


if __name__ == "__main__":
    uvicorn.run("main:app", port=int(UVICORN_PORT), log_level=LOG_LEVEL, reload=True)
