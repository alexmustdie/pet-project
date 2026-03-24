# from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.models.base import Base
from app.db.session import engine

# @asynccontextmanager
# async def lifespan(_: FastAPI):
#     # Все нужные модели должны быть импортированы перед запуском
#     from app.models.task import TaskORM
#     from app.models.category import CategoryORM
#     Base.metadata.create_all(bind=engine)
#     yield

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=['*'],
    allow_headers=['*'],
    allow_credentials=True,
)

app.include_router(api_router)
