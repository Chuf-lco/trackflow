from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes import shipments, auth
from .database import engine, Base
from .logging_config import setup_logging
import logging
from datetime import datetime
from .routes import shipments, mpesa

# Setup logging
logger = setup_logging(settings.LOG_LEVEL)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TrackFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #Allows ALL origins (safe for dev/demo, restrict later)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#Register routes
app.include_router(auth.router)
app.include_router(shipments.router)
app.include_router(mpesa.router)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with Kenya timezone"""
    start_time = datetime.utcnow()
    
    response = await call_next(request)
    
    logger.info(
        f"{request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
            "client_ip": request.client.host if request.client else "unknown"
        }
    )
    
    return response

@app.get("/health")
def health():
    logger.info("Health check requested")
    return {"status": "ok", "env": settings.LOG_LEVEL}