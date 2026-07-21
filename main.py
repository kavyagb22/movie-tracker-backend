from fastapi import FastAPI, HTTPException, status, Depends
import httpx
from typing import Optional
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from functions.tmdb.tmdb_client import get_collection, search_collection, get_franchise_by_name, get_franchise, get_curated_franchise
from comp.franchise import Collection, Franchise
from utils.helpers.tmdb import raise_tmdb_error
from comp.schema import UserResponse, UserCreate, UserLogin
from functions.common.user import get_user_by_email, create_user, login_user

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Movie Fandom Tracker API")
 
 
@app.get("/test")
def test():
    
    return {"status": "Test ok!"}

@app.post("/auth/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(user_data.email, db):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email is already registered')
    return create_user(user_data, db)

@app.post("/auth/signin", response_model=UserResponse)
def signin(login_data: UserLogin, db: Session = Depends(get_db)):
    user = login_user(login_data, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')
    return user

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
    