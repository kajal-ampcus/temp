from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.connection.db_connection import init_pool
from backend.connection.db_schema import create_tables
from backend.routes import auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_pool()
    create_tables()
    yield

app = FastAPI(
    title="KitchenLedger API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,prefix="/api/auth",tags=["Auth"])
