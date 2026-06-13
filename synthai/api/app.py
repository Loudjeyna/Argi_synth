"""API Layer — FastAPI application factory."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from synthai.services.startup_service import StartupService
from synthai.api.routes import auth, users, models, datasets, predictions, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    StartupService.initialize()
    yield


app = FastAPI(
    title="SynthAI API",
    version="1.0.0",
    description="Agricultural Synthetic Data Platform — REST API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(models.router, prefix="/api/model", tags=["Models"])
app.include_router(datasets.router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
