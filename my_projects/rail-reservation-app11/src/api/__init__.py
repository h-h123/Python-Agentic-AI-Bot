from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import trains, bookings, payments
from src.config.settings import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="Railway Reservation System API",
    version="1.0.0",
    contact={
        "name": "Support Team",
        "email": settings.support_email,
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trains.router, prefix="/api/trains", tags=["trains"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Railway Reservation System API")
    logger.info(f"Application: {settings.app_name}")
    logger.info(f"Environment: {settings.environment}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Railway Reservation System API")

@app.get("/api/health", tags=["health"])
async def health_check():
    return {"status": "healthy", "app_name": settings.app_name}

@app.get("/api/info", tags=["info"])
async def system_info():
    return {
        "app_name": settings.app_name,
        "version": "1.0.0",
        "max_seats_per_train": settings.max_seats_per_train,
        "default_seat_classes": settings.default_seat_classes,
        "currency": settings.currency,
        "support_email": settings.support_email
    }