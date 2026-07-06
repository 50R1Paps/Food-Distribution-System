from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routes import router as health_router
from app.auth import router as auth_router
from app.families import router as families_router
from app.distributions import router as distributions_router
from app.search import router as search_router
from app.data_transfer import router as data_transfer_router
from app.stats import router as stats_router
from app.reports import router as reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Food Distribution System API",
    description="API for managing food distribution to families",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(families_router)
app.include_router(distributions_router)
app.include_router(search_router)
app.include_router(data_transfer_router)
app.include_router(stats_router)
app.include_router(reports_router)
