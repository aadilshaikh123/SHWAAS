"""
Vercel entrypoint. Vercel looks for a FastAPI instance named `app`; the real
application lives in backend/main.py so local `uvicorn backend.main:app` and the
deployed function run exactly the same code.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app  # noqa: E402

__all__ = ["app"]
