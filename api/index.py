"""Vercel serverless handler"""

from mangum import Mangum
from api.main import app

# Create the Mangum handler instance
_handler = Mangum(app, lifespan="off")

# Vercel expects a callable named 'handler'
def handler(event, context):
    """Wrapper function for Vercel serverless"""
    return _handler(event, context)