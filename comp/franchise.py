from pydantic import BaseModel
from typing import Optional, List, Literal

class Movie(BaseModel):
    id: int
    title: str
    release_date: Optional[str] = None
    poster_path: Optional[str] = None

class Collection(BaseModel):
    collection_id: int
    name: str
    movies: List[Movie]

MediaType = Literal["movie", "tv"]

class FranchiseItem(BaseModel):
    type: MediaType
    id: int
    title: str
    date: Optional[str] = None
    img: Optional[str] = None

class Franchise(BaseModel):
    company: str
    franchise: str
    items: list[FranchiseItem]