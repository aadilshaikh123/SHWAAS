"""
Vercel entrypoint. Vercel looks for a FastAPI instance named `app`; the real
application lives in backend/main.py so local `uvicorn backend.main:app` and the
deployed function run identical code.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app  # noqa: E402

# Vercel invokes this file for a request, and the app then sees the function's own
# path ("/api/index/predict") rather than the one the browser asked for
# ("/predict"), so every route 404s. vercel.json appends the real path to the
# destination and this strips the function prefix back off. Written to be a no-op
# if the original path arrives unchanged, so it is correct either way.
_FUNCTION_PREFIXES = ("/api/index", "/api")


class _StripFunctionPrefix:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            path = scope.get("path", "")
            for prefix in _FUNCTION_PREFIXES:
                if path == prefix or path.startswith(prefix + "/"):
                    stripped = path[len(prefix):] or "/"
                    scope = dict(scope, path=stripped, raw_path=stripped.encode())
                    break
        await self.app(scope, receive, send)


app.add_middleware(_StripFunctionPrefix)

__all__ = ["app"]
