from contextlib import asynccontextmanager

from fastapi import FastAPI

from api import routers
from core.config import settings
from core.events import startup_handler, shutdown_handler
from core.middleware import add_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_handler(app)
    yield
    await shutdown_handler(app)


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for CRUD operations on widgets",
    version="1.0.0",
    lifespan=lifespan,
)

add_middleware(app)

for router in routers:
    app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=443,
        reload=True,
        ssl_keyfile=settings.SSL_KEYFILE,
        ssl_certfile=settings.SSL_CERTFILE,
    )
