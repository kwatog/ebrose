from contextlib import asynccontextmanager
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.routing import Match

from . import models
from .auth import now_utc
from .config import get_settings
from .database import Base, SessionLocal, engine

settings = get_settings()

from .routers import (
    allocations,
    alerts,
    assets,
    audit_logs,
    auth as auth_router,
    budget_items,
    business_case_line_items,
    business_cases,
    dashboard,
    goods_receipts,
    purchase_orders,
    record_access,
    resources,
    user_groups,
    users,
    wbs,
)

# Configure logging - logs to stdout for K8s log collection
LOG_LEVEL = settings.log_level
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def run_migrations():
    """Run Alembic migrations on startup."""
    try:
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations applied successfully")
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Run migrations first
    logger.info("Starting Ebrose application...")
    
    if settings.run_migrations_on_startup:
        run_migrations()

    if settings.auto_create_tables and not settings.is_production:
        Base.metadata.create_all(bind=engine)
    elif settings.auto_create_tables and settings.is_production:
        logger.warning("AUTO_CREATE_TABLES is enabled but ignored in production")

    
    # Initialize admin user from environment variables if no users exist
    if os.getenv("CREATE_ADMIN_USER", "").lower() in ["true", "1", "yes"]:
        db = SessionLocal()
        try:
            user_count = db.query(models.User).count()
            if user_count == 0:
                from .auth import get_password_hash
                
                # Get admin credentials from environment
                admin_username = os.getenv("ADMIN_USERNAME", "admin")
                admin_password = os.getenv("ADMIN_PASSWORD")
                admin_email = os.getenv("ADMIN_EMAIL", "admin@ebrose.local")
                admin_full_name = os.getenv("ADMIN_FULL_NAME", "System Administrator")
                
                if not admin_password:
                    logger.error("ADMIN_PASSWORD environment variable required for admin creation")
                elif len(admin_password) < 8:
                    logger.error("ADMIN_PASSWORD must be at least 8 characters long")
                else:
                    admin_user = models.User(
                        username=admin_username,
                        email=admin_email,
                        hashed_password=get_password_hash(admin_password),
                        full_name=admin_full_name,
                        role="Admin",
                        created_at=now_utc()
                    )
                    db.add(admin_user)
                    db.commit()
                    logger.info(f"Admin user '{admin_username}' created successfully")
        except Exception as e:
            logger.error(f"Error creating admin user: {e}")
        finally:
            db.close()
    
    logger.info("Ebrose application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Ebrose application...")
    pass

docs_url = "/docs" if settings.docs_enabled else None
redoc_url = "/redoc" if settings.docs_enabled else None
openapi_url = "/openapi.json" if settings.docs_enabled else None

app = FastAPI(
    title="Ebrose API",
    debug=settings.debug,
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url,
    lifespan=lifespan,
    redirect_slashes=False,
)

# Enable CORS for frontend
allowed_origins = settings.cors_allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "frame-ancestors 'none'"

        return response


app.add_middleware(SecurityHeadersMiddleware)


class TrailingSlashMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path != '/' and path.endswith('/'):
            return RedirectResponse(request.url.path.rstrip('/'), status_code=301)
        return await call_next(request)


app.add_middleware(TrailingSlashMiddleware)


from sqlalchemy import text

@app.get("/health")
def health_check():
    """Health check endpoint for K8s liveness/readiness probes."""
    try:
        # Check database connectivity
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "service": "ebrose", "database": "unhealthy", "error": str(e)}
    
    return {
        "status": "healthy", 
        "service": "ebrose", 
        "database": db_status,
        "environment": settings.environment
    }

app.include_router(auth_router.router)
app.include_router(users.router)
app.include_router(user_groups.router)
app.include_router(record_access.router)
app.include_router(audit_logs.router)
app.include_router(dashboard.router)
app.include_router(budget_items.router)
app.include_router(purchase_orders.router)
app.include_router(business_cases.router)
app.include_router(business_case_line_items.router)
app.include_router(wbs.router)
app.include_router(assets.router)
app.include_router(goods_receipts.router)
app.include_router(resources.router)
app.include_router(allocations.router)
app.include_router(alerts.router)
