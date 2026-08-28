from fastapi import FastAPI
from contextlib import asynccontextmanager

import app.repository as repository


@asynccontextmanager
async def lifespan(app: FastAPI):
    await repository.create_pool()
    yield
    await repository.pool.close()


app = FastAPI(title="Dispo", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}
