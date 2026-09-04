import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import repository
from app.config import CORS_ORIGINS
from app.routers.auth import auth_router
from app.routers.loads import loads_router
from app.routers.users import users_router

logging.basicConfig(
    filename=Path(__file__).parent / "depo.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    encoding="utf-8",
)

logging.getLogger("httpx").setLevel("WARNING")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await repository.create_pool()
    yield
    if repository.pool is not None:
        await repository.pool.close()


app = FastAPI(title="Dispo", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGINS],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(loads_router)


@app.get("/health")
async def health():
    response = await repository.check_health()
    return {"status": response}
