from contextlib import asynccontextmanager

from fastapi import FastAPI

from apps.database import create_tables
from apps.routes import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(router=user_router)
