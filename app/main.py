import logging
from time import perf_counter

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging

# from contextlib import asynccontextmanager
# from app.db.session import engine

# @asynccontextmanager
# async def lifespan(_: FastAPI):
#     # Все нужные модели должны быть импортированы перед запуском
#     from app.models.task import TaskORM
#     from app.models.category import CategoryORM
#     Base.metadata.create_all(bind=engine)
#     yield

configure_logging()

app = FastAPI()
logger = logging.getLogger("app.middleware")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    started_at = perf_counter()
    try:
        response: Response = await call_next(request)
    except Exception:
        duration_ms = (perf_counter() - started_at) * 1000
        logger.exception(
            "Request failed: %s %s completed_in=%.2fms",
            request.method,
            request.url.path,
            duration_ms,
        )
        raise
    duration_ms = (perf_counter() - started_at) * 1000
    logger.info(
        "%s %s -> %s (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


request_counter = 0


@app.middleware("http")
async def add_request_number(request: Request, call_next) -> Response:
    global request_counter
    request_counter += 1
    response: Response = await call_next(request)
    response.headers["X-Request-Number"] = str(request_counter)
    return response


app.include_router(api_router)
