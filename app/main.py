from typing import Dict

import uvicorn
from fastapi import FastAPI

from app.core.logger import logger
from app.presentation.api.v1.auth_routes import router as auth_router
from app.presentation.api.v1.project_routes import router as project_router

app = FastAPI(title="FastAPI Project Management Mess", version="1.0.0")

app.include_router(auth_router)
app.include_router(project_router)


@app.get("/", summary="Health Check", tags=["Health"], response_model=dict)
async def root() -> Dict[str, str]:
    """Rootmake endpoint to check if the server is running."""
    logger.info("Health check endpoint hit")
    return {"status": "healthy", "message": "server is up"}


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info", reload=True)
