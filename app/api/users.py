from datetime import datetime

from app.db import get_db
from app.models.models import User
from app.schemas.schemas import (
    BookBase,
    StandardResponse,
    UserBase,
    UserLoginIn,
    UserLoginOut,
)
from faker import Faker
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

user_router = APIRouter()


@user_router.get("/")
async def user_get_all(*, db: Session = Depends(get_db)):
    DEFAULT_DATABASE_USER = db.execute(select(User)).scalars().all()
    if DEFAULT_DATABASE_USER is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return DEFAULT_DATABASE_USER


@user_router.post("/")  # , response_model=User
def read_user(*, db: Session = Depends(get_db)):

    faker = Faker()

    new_user = User(
        email=faker.email(),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        user_role_id=1,
        created_at=datetime.utcnow(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@user_router.post("/roles")  # , response_model=User
def read_user(*, db: Session = Depends(get_db)):

    faker = Faker()

    new_user = User(
        email=faker.email(),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        user_role_id=1,
        created_at=datetime.utcnow(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
