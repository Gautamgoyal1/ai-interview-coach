"""Reject oversized bodies before multipart parsing or temporary-file creation."""

import asyncio
from threading import Lock

from starlette.responses import JSONResponse


MAX_REQUEST_BYTES = 11 * 1024 * 1024  # 10 MiB PDF plus bounded form overhead.


class RequestBodyLimitMiddleware:
    def __init__(self, app, max_bytes=MAX_REQUEST_BYTES, max_active=8, timeout=60, max_active_per_client=2):
        self.app = app
        self.max_bytes = max_bytes
        self.max_active = max_active
        self.timeout = timeout
        self.max_active_per_client = max_active_per_client
        self._active = 0
        self._clients = {}
        self._lock = Lock()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] not in {"POST", "PUT", "PATCH"}:
            return await self.app(scope, receive, send)
        lengths = [v for k, v in scope.get("headers", []) if k.lower() == b"content-length"]
        if lengths:
            if len(lengths) != 1 or len(lengths[0]) > 20 or not lengths[0].isdigit():
                return await JSONResponse({"detail": "Invalid Content-Length."}, status_code=400)(scope, receive, send)
            if int(lengths[0]) > self.max_bytes:
                return await self._error(scope, receive, send, 413, "Request body is too large.")
        client = (scope.get("client") or ("unknown",))[0]
        with self._lock:
            admitted = self._active < self.max_active and self._clients.get(client, 0) < self.max_active_per_client
            if admitted:
                self._active += 1
                self._clients[client] = self._clients.get(client, 0) + 1
        if not admitted:
            return await self._error(scope, receive, send, 503, "Server is busy. Please retry.")
        reading = True
        try:
            body = bytearray()
            try:
                async with asyncio.timeout(self.timeout):
                    while True:
                        message = await receive()
                        if message["type"] == "http.disconnect":
                            return
                        chunk = message.get("body", b"")
                        if len(body) + len(chunk) > self.max_bytes:
                            return await self._error(scope, receive, send, 413, "Request body is too large.")
                        body.extend(chunk)
                        if not message.get("more_body", False):
                            break
            except TimeoutError:
                return await self._error(scope, receive, send, 408, "Request body timed out.")
            # Body-reader slots must not remain occupied during a slow AI response.
            self._release(client)
            reading = False
            delivered = False

            async def bounded_receive():
                nonlocal delivered
                if not delivered:
                    delivered = True
                    payload = bytes(body)
                    body.clear()
                    return {"type": "http.request", "body": payload, "more_body": False}
                return await receive()

            await self.app(scope, bounded_receive, send)
        finally:
            if reading:
                self._release(client)

    def _release(self, client):
        with self._lock:
            self._active -= 1
            count = self._clients[client] - 1
            if count:
                self._clients[client] = count
            else:
                self._clients.pop(client)

    @staticmethod
    async def _error(scope, receive, send, status, detail):
        response = JSONResponse({"detail": detail}, status_code=status, headers={"Cache-Control": "no-store"})
        await response(scope, receive, send)
