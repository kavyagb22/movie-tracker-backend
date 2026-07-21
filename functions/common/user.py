from sqlalchemy.orm import Session

from comp.models import User
from comp.schema import UserCreate, UserLogin, UserResponse
from utils.auth import hash_password, verify_password

def create_user(user_data: UserCreate, db: Session) -> UserResponse:
    hashed_pwd = hash_password(user_data.password)
    user = User(
        firstname = user_data.firstname,
        lastname = user_data.lastname,
        email = user_data.email,
        password = hashed_pwd,
        notifications = user_data.notifications
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_id(user_id: int, db: Session) -> UserResponse:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(user_email: str, db: Session) -> UserResponse:
    return db.query(User).filter(User.email == user_email).first()

def login_user(login_data: UserLogin, db: Session) -> UserResponse:
    user = get_user_by_email(login_data.email, db)
    if not user:
        raise ValueError(f"User not created for this email")
    if not verify_password(login_data.password, user.password):
        raise ValueError(f"Password incorrect for given user")
    return user

