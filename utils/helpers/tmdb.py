from dotenv import load_dotenv
import os
import httpx
from typing import Optional
from fastapi import HTTPException

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

async def tmdb_api(endpoint: str, extra_params: Optional[dict] = None) -> dict:
    url = f"{TMDB_BASE_URL}{endpoint}"
    params = {"api_key": TMDB_API_KEY}
    if extra_params:
        params.update(extra_params)
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

def raise_tmdb_error(exc: httpx.HTTPStatusError) -> None:
    raise HTTPException(
        status_code=exc.response.status_code,
        detail=f"TMDB request failed: {exc.response.text}",
    )