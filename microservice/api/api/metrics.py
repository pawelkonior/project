from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import psutil
from fastapi import APIRouter, Request, Response



router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("")
async def get_metrics(
        request: Request,
):
    from core.metrics import MEMORY_USAGE
    memory_info = psutil.Process().memory_info()
    MEMORY_USAGE.set(memory_info.rss)


    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )