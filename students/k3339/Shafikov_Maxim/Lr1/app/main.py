from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api.routers import auth, budgets, categories, goals, tags, transactions, users
from .core.database import engine
from .crud.base import CrudIntegrityError
from .models.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Personal Finance API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(CrudIntegrityError)
async def crud_integrity_error_handler(_: Request, exc: CrudIntegrityError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(tags.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(goals.router)
