from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.db.session import init_db
from backend.rag.vector_store import init_vector_store
from backend.core.config import get_settings
from backend.core.logging import logger
from backend.api.v1.routes import chat_routes, trip_routes

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting Travel Agent Backend...")
        await init_db()
        init_vector_store()
        logger.info("Startup complete.")
    except Exception as e:
        logger.critical(f"Startup failed: {e}")
    yield

app = FastAPI(title=settings.APP_NAME, version="1.0.0", lifespan=lifespan, debug=settings.DEBUG)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Uncaught exception on {request.url}: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

app.add_middleware(CORSMiddleware, allow_origins=settings.ALLOWED_ORIGINS, allow_credentials=True, allow_methods=["GET", "POST"], allow_headers=["*"])

app.include_router(chat_routes.router, prefix="/api/v1")
app.include_router(trip_routes.router, prefix="/api/v1")

@app.get("/health")
async def health_check(): return {"status": "healthy"}