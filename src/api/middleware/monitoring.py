import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.routing import Match

from src.monitoring.service import MetricsService

logger = logging.getLogger(__name__)


class PrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, metrics_service: MetricsService):
        super().__init__(app)
        self.metrics_service = metrics_service

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Do not track /metrics itself
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        
        # Try to find the matched route for the endpoint label
        # This prevents high cardinality from dynamic paths (e.g. /users/123 -> /users/{id})
        endpoint = request.url.path
        for route in request.app.routes:
            match, _ = route.matches(request.scope)
            if match == Match.FULL:
                if hasattr(route, "path"):
                    endpoint = route.path
                break

        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            self.metrics_service.record_pipeline_error("api")
            raise e
        finally:
            end_time = time.perf_counter()
            duration = end_time - start_time
            self.metrics_service.record_http_request(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration_seconds=duration,
            )

        return response
