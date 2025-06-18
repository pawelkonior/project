import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from core.metrics import ACTIVE_REQUESTS, record_request_metrics


class PrometheusMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        ACTIVE_REQUESTS.inc()

        start_time = time.time()

        path_template = request.url.path
        route = request.scope.get("route")

        if route and route.path:
            path_template = route.path

        try:
            response = await call_next(request)

            duration = time.time() - start_time
            record_request_metrics(
                method=request.method,
                endpoint=path_template,
                status_code=response.status_code,
                duration=duration,
            )

            return response

        except Exception as e:
            duration = time.time() - start_time
            record_request_metrics(
                method=request.method,
                endpoint=path_template,
                status_code=500,
                duration=duration,
            )
            raise e
        finally:
            ACTIVE_REQUESTS.dec()