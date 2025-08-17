from contextlib import asynccontextmanager
from typing import Dict

import uvicorn
from fastapi import FastAPI

from app.presentation.api.v1.auth_routes import router as auth_router
from app.core.logger import logger
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event to create database and tables."""
    logger.info("Creating database and tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database and tables created successfully.")
    yield


app = FastAPI(
    title="FastAPI Project Management Mess", version="1.0.0", lifespan=lifespan
)

app.include_router(auth_router)


@app.get("/", summary="Health Check", tags=["Health"], response_model=dict)
async def root() -> Dict[str, str]:
    """Root endpoint to check if the server is running."""
    logger.info("Health check endpoint hit")
    return {"status": "healthy", "message": "server is up"}


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info", reload=True)
