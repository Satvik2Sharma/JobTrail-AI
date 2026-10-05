import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from app.core.config import settings
from app.db.session import engine, Base, SessionLocal
from app.api import auth, profile, resume, jobs, recommendations, search, skill_gap, applications, recruiter

# For local development with SQLite, create tables if they don't exist.
# In production (PostgreSQL), schema migrations are managed via Alembic.
if settings.is_sqlite:
    Base.metadata.create_all(bind=engine)

# Ensure upload directory exists for local storage fallback
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    port = int(os.environ.get("PORT", settings.PORT))
    print(f"[{settings.PROJECT_NAME}] Starting service v{settings.VERSION} on port {port} (env: {settings.ENVIRONMENT})...")
    yield
    print(f"[{settings.PROJECT_NAME}] Shutting down backend service...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered job and internship recommendation platform with explainable career matching and skill-gap analysis.",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration: Never use wildcard '*' with credentials in production
cors_origins = settings.CORS_ORIGINS
if isinstance(cors_origins, list):
    # Filter out wildcard if present to maintain security with credentials
    cors_origins = [o for o in cors_origins if o != "*"]
    if not cors_origins:
        cors_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoints: Distinguishes basic service health from database readiness
@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health_check():
    db_status = "unknown"
    db_engine = "postgresql" if not settings.is_sqlite else "sqlite"
    is_db_ready = False

    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        db_status = "connected"
        is_db_ready = True
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    storage_provider = "supabase" if settings.is_supabase_storage_enabled else "local"

    overall_status = "healthy" if is_db_ready else "degraded"

    return {
        "status": overall_status,
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": {
            "status": db_status,
            "engine": db_engine,
            "ready": is_db_ready
        },
        "storage": {
            "provider": storage_provider,
            "bucket": settings.SUPABASE_STORAGE_BUCKET if settings.is_supabase_storage_enabled else settings.UPLOAD_DIR
        }
    }

# Include API routers
app.include_router(auth.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(resume.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(skill_gap.router, prefix="/api")
app.include_router(applications.router, prefix="/api")
app.include_router(recruiter.router, prefix="/api")

# Static files for local uploads if directory exists
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", settings.PORT))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=(settings.ENVIRONMENT == "development"))
