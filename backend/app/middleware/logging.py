import time
import logging
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("reminderbot.api")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid4())[:8]
        start_time = time.time()

        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
            except Exception:
                pass

        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - Request received"
        )

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"Unhandled exception after {process_time:.3f}s",
                exc_info=True,
            )
            raise

        process_time = time.time() - start_time

        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time_ms": round(process_time * 1000, 2),
            "ip": request.client.host if request.client else "unknown",
        }

        if response.status_code >= 500:
            logger.error(f"[{request_id}] Server error: {log_data}")
        elif response.status_code >= 400:
            logger.warning(f"[{request_id}] Client error: {log_data}")
        else:
            logger.info(f"[{request_id}] Success: {log_data}")

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = str(log_data["process_time_ms"])

        return response
