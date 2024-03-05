"""HTTP custom middlewares."""
import time

import structlog
from asgi_correlation_id.context import correlation_id
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from uvicorn.protocols.utils import get_path_with_query_string


class LoggingMiddleware(BaseHTTPMiddleware):
    """LoggingMiddleware class."""

    def __init__(self, app: FastAPI, *, logger: structlog.BoundLogger) -> None:
        self._logger = logger
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Get request and response information before and after processing the request.

        Parameters
        ----------
        request: Request
            Request instance
        call_next: RequestResponseEndpoint
            an awaitable Response object

        Returns
        -------
        Response
            Http Response object
        """
        structlog.contextvars.clear_contextvars()
        start_time = time.perf_counter()

        request_id = correlation_id.get()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        try:
            req_body = await request.json()
        except Exception:  # noqa: BLE001
            req_body = None

        try:
            response = await call_next(request)
        except Exception:  # pragma: no cover
            structlog.stdlib.get_logger("api.error").exception("Uncaught exception")
            raise
        else:
            status_code = response.status_code
            url = get_path_with_query_string(request.scope)  # type: ignore[arg-type]
            client_host = request.client.host if request.client else None
            client_port = request.client.port if request.client else None
            http_method = request.method
            http_version = request.scope["http_version"]
            process_time = time.perf_counter() - start_time
            # Recreate the Uvicorn access log format, but add all parameters as structured information
            self._logger.info(
                """%s:%s - "%s %s HTTP/%s" %s""",
                client_host,
                client_port,
                http_method,
                url,
                http_version,
                status_code,
                http={
                    "url": str(request.url),
                    "path": request.url.path,
                    "status_code": status_code,
                    "method": http_method,
                    "request_id": request_id,
                    "version": http_version,
                    "referrer": request.headers.get("referrer"),
                    "ua": request.headers.get("user-agent"),
                },
                params=dict(request.query_params.items()),
                body=req_body,
                network={"client": {"ip": client_host, "port": client_port}},
                duration=process_time,
            )
            response.headers["X-Process-Time"] = str(process_time)
            return response
