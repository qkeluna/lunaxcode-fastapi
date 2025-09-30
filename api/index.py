"""Vercel serverless handler"""

from mangum import Mangum
from api.main import app

# Mangum handler for Vercel
handler = Mangum(app, lifespan="off")