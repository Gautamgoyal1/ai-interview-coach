"""Small ASGI response policy for the bearer-authenticated API."""
from starlette.datastructures import MutableHeaders


class ResponseHeadersMiddleware:
    def __init__(self, app, *, production: bool = False):
        self.app, self.production = app, production

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        async def protected_send(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Content-Type-Options"] = "nosniff"
                headers["X-Frame-Options"] = "DENY"
                headers["Referrer-Policy"] = "no-referrer"
                headers["Cache-Control"] = "private, no-store"
                if self.production:
                    headers["Strict-Transport-Security"] = "max-age=31536000"
                    headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
            await send(message)

        await self.app(scope, receive, protected_send)
