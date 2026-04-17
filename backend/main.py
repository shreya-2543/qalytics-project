"""
main.py � FastAPI application entry point
Organizes routes from backend.routes modules
"""
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend import models
from backend.auth import hash_password
from backend.config import (
    BOOTSTRAP_ADMIN_EMAIL,
    BOOTSTRAP_ADMIN_ENABLED,
    BOOTSTRAP_ADMIN_PASSWORD,
    BOOTSTRAP_ADMIN_ROLE,
    BOOTSTRAP_ADMIN_USERNAME,
    CORS_ALLOWED_ORIGINS,
)
from backend.database import Base, engine, get_db
from backend.logging_utils import LoggingMiddleware
from backend.routes import auth, suites, cases, runs, analytics, reports, websocket, chat


# -- Lifespan: create tables + seed admin --------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _seed_admin()
    yield


def _seed_admin():
    from backend.database import SessionLocal
    if not BOOTSTRAP_ADMIN_ENABLED or not BOOTSTRAP_ADMIN_USERNAME or not BOOTSTRAP_ADMIN_PASSWORD:
        return
    db = SessionLocal()
    try:
        if not db.query(models.User).filter_by(username=BOOTSTRAP_ADMIN_USERNAME).first():
            db.add(models.User(
                username=BOOTSTRAP_ADMIN_USERNAME,
                email=BOOTSTRAP_ADMIN_EMAIL,
                hashed_password=hash_password(BOOTSTRAP_ADMIN_PASSWORD),
                role=BOOTSTRAP_ADMIN_ROLE,
            ))
            db.commit()
    finally:
        db.close()


# -- App -----------------------------------------------------------------------
app = FastAPI(
    title="QAlytics API",
    version="1.0.0",
    description="QA Test Management Platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add structured logging middleware (logs all requests as JSON)
app.add_middleware(LoggingMiddleware)

# Serve Allure reports
_reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
os.makedirs(_reports_dir, exist_ok=True)
app.mount("/reports", StaticFiles(directory=_reports_dir, html=True), name="reports")


# -- Exception handlers --------------------------------------------------------
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": "Resource not found"})


@app.exception_handler(401)
async def unauth_handler(request, exc):
    return JSONResponse(status_code=401, content={"detail": "Unauthorized"})


# -- Health --------------------------------------------------------------------
@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok", "version": "1.0.0", "timestamp": datetime.utcnow().isoformat()}


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs", status_code=307)


# -- Include route modules -----------------------------------------------------
app.include_router(auth.router)
app.include_router(suites.router)
app.include_router(cases.router)
app.include_router(runs.router)
app.include_router(analytics.router)
app.include_router(reports.router)
app.include_router(websocket.router)
app.include_router(chat.router)
