from fastapi import FastAPI, HTTPException
import httpx

from lib.tmdb.tmdb_client import get_collection, search_collection, get_franchise_by_name, get_franchise, get_curated_franchise
from comp.franchise import Collection, Franchise
from typing import Optional
from utils.helpers.tmdb import raise_tmdb_error

app = FastAPI(title="Movie Fandom Tracker API")
 
 
@app.get("/test")
def test():
    
    return {"status": "Test ok!"}


@app.get("/franchises/{name}/movies", response_model=Collection)
async def get_franchise_movies_by_name(name: str):
    try:
        return await get_franchise_by_name(name)
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except httpx.HTTPStatusError as err:
        raise_tmdb_error(err)
 
 
@app.get("/franchises/{collection_id}/movies", response_model=Collection)
async def get_franchise_movies(collection_id: int):
    try:
        return await get_collection(collection_id)
    except httpx.HTTPStatusError as err:
        raise_tmdb_error(err)

@app.get("/franchises/search/{company_name}", response_model=Franchise)
async def get_franchise_route(company_name: str, is_movie: bool = True, is_tv: bool = True):
    try:
        return await get_franchise(company_name, is_movie, is_tv)
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except httpx.HTTPStatusError as err:
        raise_tmdb_error(err)

@app.get('/franchises/curated/{franchise_name}', response_model=Franchise)
async def get_franchise_info(franchise_name: str, include_movies: bool = True, include_tv: bool = True, include_extra: bool = False):
    try:
        return await get_curated_franchise(franchise_name, include_movies, include_tv, include_extra)
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except httpx.HTTPStatusError as err:
        raise_tmdb_error(err)
    