from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown events."""
    # Startup: verify database connection
    from app.database import engine

    async with engine.begin() as conn:
        pass  # Connection pool initialized

    yield

    # Shutdown: dispose engine
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="CampusOrbit — Complete Education Platform Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.users import router as users_router
from app.api.courses import router as courses_router
from app.api.fees import router as fees_router
from app.api.attendance import router as attendance_router
from app.api.leads import router as leads_router
from app.api.campus import router as campus_router
from app.api.inventory import router as inventory_router
from app.api.transport import router as transport_router
from app.api.notifications import router as notifications_router
from app.api.pricing import router as pricing_router
from app.api.marketplace import router as marketplace_router
from app.api.payments import router as payments_router
from app.api.substitutions import router as substitutions_router
from app.api.complaints import router as complaints_router

api_prefix = "/api/v1"
app.include_router(auth_router, prefix=api_prefix)
app.include_router(dashboard_router, prefix=api_prefix)
app.include_router(users_router, prefix=api_prefix)
app.include_router(courses_router, prefix=api_prefix)
app.include_router(fees_router, prefix=api_prefix)
app.include_router(attendance_router, prefix=api_prefix)
app.include_router(leads_router, prefix=api_prefix)
app.include_router(campus_router, prefix=api_prefix)
app.include_router(inventory_router, prefix=api_prefix)
app.include_router(transport_router, prefix=api_prefix)
app.include_router(notifications_router, prefix=api_prefix)
app.include_router(pricing_router, prefix=api_prefix)
app.include_router(marketplace_router, prefix=api_prefix)
app.include_router(payments_router, prefix=api_prefix)
app.include_router(substitutions_router, prefix=api_prefix)
app.include_router(complaints_router, prefix=api_prefix)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME, "version": "1.0.0"}
