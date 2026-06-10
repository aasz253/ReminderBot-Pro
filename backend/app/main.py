import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.middleware.cors import setup_cors
from app.middleware.logging import LoggingMiddleware
from app.scheduler import init_scheduler, shutdown_scheduler

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("reminderbot")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME}")
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment="production" if not settings.DEBUG else "development",
            )
            logger.info("Sentry initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Sentry: {e}")

    init_scheduler()
    logger.info("Scheduler initialized")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")

    yield

    shutdown_scheduler()
    await engine.dispose()
    logger.info("Application shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

setup_cors(app)
app.add_middleware(LoggingMiddleware)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error. Please try again later."},
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


from app.api.v1.auth import router as auth_router
from app.api.v1.reminders import router as reminders_router
from app.api.v1.subscriptions import router as subscriptions_router
from app.api.v1.payments import router as payments_router
from app.api.v1.teams import router as teams_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.admin import router as admin_router
from app.api.v1.categories import router as categories_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(reminders_router, prefix="/api/v1")
app.include_router(subscriptions_router, prefix="/api/v1")
app.include_router(payments_router, prefix="/api/v1")
app.include_router(teams_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")

from app.api.webhooks.stripe import router as stripe_webhook_router
from app.api.webhooks.mpesa import router as mpesa_webhook_router
from app.api.webhooks.telegram import router as telegram_webhook_router
from app.api.webhooks.whatsapp import router as whatsapp_webhook_router
from app.api.webhooks.sendgrid import router as sendgrid_webhook_router

app.include_router(stripe_webhook_router, prefix="/api/webhooks")
app.include_router(mpesa_webhook_router, prefix="/api/webhooks")
app.include_router(telegram_webhook_router, prefix="/api/webhooks")
app.include_router(whatsapp_webhook_router, prefix="/api/webhooks")
app.include_router(sendgrid_webhook_router, prefix="/api/webhooks")

try:
    import os
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
except Exception:
    pass


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.0.0",
    }


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/docs",
        "health": "/health",
    }
