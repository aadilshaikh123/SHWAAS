"""
Vercel entrypoint. Vercel looks for a FastAPI instance named `app`; the real
application lives in backend/main.py so local `uvicorn backend.main:app` and the
deployed function run identical code.

vercel.json rewrites the API paths to this function's exact path (/api/index).
Vercel preserves the caller's original path in the request, so FastAPI still sees
/predict and /health and routes them normally - verified against a deployed probe.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app  # noqa: E402

__all__ = ["app"]
