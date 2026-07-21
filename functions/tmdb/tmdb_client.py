import os

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

from comp.franchise import Collection, Movie, MediaType
from utils.helpers.tmdb import tmdb_api
from utils.constants import KNOWN_COMPANIES, FRANCHISE_DATA

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

if not TMDB_API_KEY:
    raise RuntimeError("TMDB_API_KEY not found")


async def search_collection(name: str) -> Optional[int]:
    data = await tmdb_api("/search/collection", {"query": name})
    results = data.get("results", [])
    return results[0]["id"] if results else None


async def get_collection(collection_id: int) -> Collection:
    data = await tmdb_api(f"/collection/{collection_id}")

    sorted_parts = sorted(
        data.get("parts", []),
        key=lambda movie: movie.get("release_date") or "N/A",
    )

    movies = [
        Movie(
            id=m["id"],
            title=m["title"],
            release_date=m.get("release_date"),
            poster_path=m.get("poster_path"),
        )
        for m in sorted_parts
    ]

    return Collection(collection_id=data["id"], name=data["name"], movies=movies)


async def get_franchise_by_name(name: str) -> Collection:
    collection_id = await search_collection(name)
    if collection_id is None:
        raise ValueError(f"No TMDB collection found for franchise '{name}'")
    return await get_collection(collection_id)


async def search_company(name: str) -> Optional[int]:
    key = name.strip().lower()
    if key in KNOWN_COMPANIES:
        return KNOWN_COMPANIES[key]
    data = await tmdb_api("/search/company", {"query": name})
 
    results = data.get("results", [])

    
    return results[0]["id"] if results else None


async def discover_by_company(company_id: int, media_type: MediaType, keyword_id: Optional[int] = None) -> list[dict]:
    
    if media_type== 'movie':
        date_field = 'release_date'
    elif media_type == 'tv':
        date_field = 'first_air_date'
    else:
        raise ValueError(f"Media type is not supported")
    params = {
        "with_companies": company_id,
        "sort_by": f"{date_field}.asc",
        "page": 1,
    }
    if keyword_id:
        params["with_keywords"] = keyword_id

    all_results = []
    while True:
        data = await tmdb_api(f"/discover/{media_type}", params)
        all_results.extend(data.get("results", []))

        total_pages = data.get("total_pages", 1)
        if params["page"] >= total_pages:
            break
        params["page"] += 1

    return all_results
async def get_franchise(company_name: str, is_movie: bool, is_tv: bool) -> dict:
    company_id = await search_company(company_name)
    if company_id is None:
        raise ValueError(f"No company found for '{company_name}'")
    
    movies = await discover_by_company(company_id, 'movie') if is_movie else []
    tv_shows = await discover_by_company(company_id, 'tv') if is_tv else []

    items = [
        {"type": "movie",
         "id": m["id"], 
         "title": m["title"], 
         "date": m.get("release_date"),
         "img": m.get('poster_path')}
        for m in movies
    ] + [
        {"type": "tv", 
        "id": t["id"], 
        "title": t["name"], 
        "date": t.get("first_air_date"),
        "img": t.get('poster_path')}
        for t in tv_shows
    ]

    items.sort(key=lambda x: x["date"] or "N/A")
    return {"company": company_name, "items": items, 'franchise': company_name}


async def get_curated_franchise(franchise_name: str, include_movies: bool = True, include_tv: bool = True, include_extra: bool = False) -> dict:
    key = franchise_name.strip().lower()
    if key not in FRANCHISE_DATA:
        raise ValueError(f"'{franchise_name}' is not a curated franchise yet")
    
    data = FRANCHISE_DATA[key]
    if include_movies:
        movie_ids = list(data['movies'].keys())
    else:
        movie_ids = []
    if include_tv:
        tv_ids = list(data['tv'].keys())
    else:
        tv_ids = []
    if include_extra:
        movie_ids += [i for i,t in data['extras'].items() if t['type'] == 'movie']
        tv_ids += [i for i,t in data['extras'].items() if t['type'] == 'tv']

    movies = [await tmdb_api(f"/movie/{mid}") for mid in movie_ids]
    tv_shows = [await tmdb_api(f"/tv/{tid}") for tid in tv_ids]

    items = [{
        "type": "movie",
        "id" : m["id"],
        "title": m['title'],
        "date": m.get('release_date'),
        "img": m.get('poster_path')
    } for m in movies] + \
    [{
        "type": "tv",
        "id" : t["id"],
        "title": t['name'],
        "date": t.get('first_air_date'),
        "img": t.get('poster_path')
    } for t in tv_shows]

    items.sort(key=lambda x: x['date'] or 'N/A')
    return {"franchise":franchise_name, "items": items, "company":FRANCHISE_DATA[key]['company']}


    


    