from fastapi import FastAPI, Request
import time

from api import routers
from core.config import settings
from core.middleware import add_middleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for CRUD operations on widgets",
    version="1.0.0"
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

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
