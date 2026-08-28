from fastapi import FastAPI
from contextlib import asynccontextmanager
import app.repository as repository

from app.routers.auth import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await repository.create_pool()
    yield
    await repository.pool.close()


app = FastAPI(title="Dispo", lifespan=lifespan)


app.include_router(auth_router)


@app.get("/health")
async def health():
    response = await repository.check_health()
    return {"status": response}
