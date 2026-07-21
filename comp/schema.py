from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    firstname: str
    lastname: Optional[str] = None
    email: EmailStr
    password: str
    notifications: Optional[bool] = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    firstname: str
    lastname: Optional[str] = None
    email: EmailStr
    notifications: Optional[bool] = False
    created_at : datetime

    # instead of dictionary, read attributes directly (can use dot notation to access values)
    class Config:
        from_attributes = True
