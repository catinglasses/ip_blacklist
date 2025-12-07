import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI

from src.api.router import api_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, Any]:
    logger.info("Starting up...")
    yield
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan)

app.include_router(api_router)

@app.get('/')
async def root() -> dict[str, Any]:
    return {'message': 'IP Blacklist Service'}
