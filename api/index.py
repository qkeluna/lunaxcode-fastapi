"""Vercel serverless handler"""

from mangum import Mangum
from api.main import app

# Export Mangum handler directly - Vercel expects ASGI callable
# Using lifespan="off" to prevent issues with serverless cold starts
handler = Mangum(app, lifespan="off", api_gateway_base_path="/api")