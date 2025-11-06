# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import asyncio
from sqlalchemy import text
import logging
import logging
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.core.config import settings
from api.api.v1.router import api_router
from api.db.session import engine
from api.db.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # start a background keep-alive task to avoid idle connections being closed by MySQL
    keepalive_task = None
    try:
        async def _keepalive():
            logger = logging.getLogger("app.keepalive")
            while True:
                try:
                    async with engine.connect() as conn:
                        await conn.execute(text("SELECT 1"))
                    logger.info("Keepalive query succeeded")
                except Exception as e:
                    logger.warning("Keepalive query failed: %s", e)
                await asyncio.sleep(30)

        keepalive_task = asyncio.create_task(_keepalive())
        yield
    finally:
        # Shutdown: cancel keepalive and dispose engine
        if keepalive_task:
            keepalive_task.cancel()
            try:
                await keepalive_task
            except asyncio.CancelledError:
                pass
        await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)



# Temporary middleware to log request bodies and responses for debugging 422s
logger = logging.getLogger("app.request_logger")


class DebugRequestBodyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # read body so we can log it; store it so downstream can also read
        try:
            body = await request.body()
        except Exception:
            body = b""
        # create a new receive function that will replay the same body
        async def receive() -> dict:
            return {"type": "http.request", "body": body, "more_body": False}

        # create a fresh Request with the same scope and our receive so downstream
        # consumers (FastAPI/Starlette) can read the body normally
        req = Request(request.scope, receive)

        response = await call_next(req)

        # If client got 4xx/5xx on the income variable endpoint, log details
        try:
            path = request.url.path
            if path.startswith("/api/income/variable/"):
                status = response.status_code
                if status >= 400:
                    # log request body and status (avoid consuming response body here)
                    logger.warning("Request to %s returned %s. Request body=%s", path, status, body.decode(errors='replace'))
        except Exception:
            logger.exception("Error while logging request/response")

        return response


# register debug middleware (safe to remove after debugging)
app.add_middleware(DebugRequestBodyMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    try:
        body = await request.body()
    except Exception:
        body = b""
    logger.warning("Validation error for %s. Request body=%s; Errors=%s", request.url.path, body.decode(errors='replace'), exc.errors())
    # return the default JSON structure with details so client behavior remains unchanged
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Sistema de Gestão Financeira API"}


if __name__ == "__main__":
    # Force the default asyncio event loop implementation instead of uvloop
    # to avoid known interoperability issues between uvloop + aiomysql.
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, loop="asyncio")

