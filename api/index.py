"""Vercel serverless handler - ASGI adapter for FastAPI"""

from mangum import Mangum
from api.main import app

# Vercel requires a handler that is an ASGI callable
# Mangum wraps FastAPI (ASGI) to work with Vercel's serverless runtime
handler = Mangum(app, lifespan="off")