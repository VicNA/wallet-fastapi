from fastapi import FastAPI

from app.api.router import api_router
from app.api.v1.handlers.exception_handler import register_exception_handlers
from app.core.config import get_config

config = get_config()

app = FastAPI(
    title=config.title,
    description=config.description,
    version=config.version,
    docs_url=config.docs_url,
    redoc_url=config.redoc_url,
)

register_exception_handlers(app)

app.include_router(api_router)
