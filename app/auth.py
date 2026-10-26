import secrets
from fastapi import Header, HTTPException
from . import config


def verify_api_key(x_api_key: str | None = Header(default=None)):
    """FastAPI maps the x_api_key parameter to the X-API-Key header automatically."""
    if not x_api_key or not config.SERVICE_API_KEY:
        raise HTTPException(status_code=401, detail="Missing or invalid API key")
    if not secrets.compare_digest(
        x_api_key.encode(), config.SERVICE_API_KEY.encode()
    ):
        raise HTTPException(status_code=401, detail="Missing or invalid API key")