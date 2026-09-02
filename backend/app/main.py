from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import repository
from app.routers.auth import auth_router
from app.routers.loads import loads_router
from app.routers.users import users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await repository.create_pool()
    yield
    await repository.pool.close()


app = FastAPI(title="Dispo", lifespan=lifespan)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(loads_router)


@app.get("/health")
async def health():
    response = await repository.check_health()
    return {"status": response}
