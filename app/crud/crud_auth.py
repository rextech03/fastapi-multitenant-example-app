import secrets
from datetime import datetime, timedelta
from uuid import uuid4

from app.models.shared_models import PublicUser
from app.schemas.schemas import UserRegisterIn
from langcodes import standardize_tag
from passlib.hash import argon2
from sqlalchemy import select
from sqlalchemy.orm import Session


def get_user_by_email(db: Session, email: str):
    return db.execute(select(PublicUser.email).where(PublicUser.email == email)).scalar_one_or_none()


def create_public_user(db: Session, user: UserRegisterIn):
    new_user = PublicUser(
        uuid=str(uuid4()),
        email=user.email.strip(),
        password=argon2.hash(user.password),
        service_token=secrets.token_hex(32),
        service_token_valid_to=datetime.utcnow() + timedelta(days=1),
        is_active=False,
        is_verified=False,
        tos=user.tos,
        tz=user.tz,
        lang=standardize_tag(user.lang),
        created_at=datetime.utcnow(),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
