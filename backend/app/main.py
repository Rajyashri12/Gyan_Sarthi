from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import (
    Base,
    engine,
)

import app.models


# =====================================
# ROUTES
# =====================================

from app.api.routes.ai import (
    router as ai_router
)

from app.api.routes.auth import (
    router as auth_router
)

from app.api.routes.practice import (
    router as practice_router
)

from app.api.routes.mastery import (
    router as mastery_router
)

from app.api.routes.analytics import (
    router as analytics_router
)

from app.api.routes.ai import router as ai_router

from app.api.routes.revision import (
    router as revision_router
)
from app.api.routes.exam import router as exam_router

from app.api.routes.diagnostic import (
    router as diagnostic_router,
)

# =====================================
# DATABASE
# =====================================

Base.metadata.create_all(
    bind=engine
)


# =====================================
# APP
# =====================================

app = FastAPI(
    title="Gyan Sarthi API",
    version="1.0.0",
)


# =====================================
# CORS
# =====================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =====================================
# ROUTES
# =====================================

app.include_router(
    ai_router
)

app.include_router(
    auth_router
)

app.include_router(
    practice_router
)

app.include_router(
    mastery_router
)

app.include_router(
    analytics_router
)

app.include_router(
    revision_router
)

app.include_router(
    exam_router
)

app.include_router(
    diagnostic_router
)

# =====================================
# ROOT
# =====================================

@app.get("/")
def root():

    return {
        "message": "Gyan Sarthi API is running"
    }


# =====================================
# HEALTH
# =====================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "gyan-sarthi-api",
    }