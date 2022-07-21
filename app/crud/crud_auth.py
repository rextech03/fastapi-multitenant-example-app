import random
import secrets
from datetime import datetime, timedelta
from uuid import uuid4

from app.models.shared_models import PublicCompany, PublicUser
from app.schemas.requests import UserRegisterIn
from app.schemas.schemas import PubliCompanyAdd
from langcodes import standardize_tag
from passlib.hash import argon2
from sqlalchemy import select
from sqlalchemy.orm import Session


def get_user_by_email(db: Session, email: str):
    return db.execute(select(PublicUser.email).where(PublicUser.email == email)).scalar_one_or_none()


def get_user_by_service_token(db: Session, token: str):
    return db.execute(
        select(PublicUser)
        .where(PublicUser.service_token == token)
        .where(PublicUser.is_active == False)
        .where(PublicUser.service_token_valid_to > datetime.utcnow())
    ).scalar_one_or_none()


def get_company_by_nip(db: Session, nip: str):
    return db.execute(select(PublicCompany).where(PublicCompany.nip == nip)).scalar_one_or_none()


def generate_qr_id(db: Session, nip: str):
    allowed_chars = "abcdefghijkmnopqrstuvwxyz23456789"  # ABCDEFGHJKLMNPRSTUVWXYZ23456789
    company_ids = db.execute(select(PublicCompany.qr_id)).scalars().all()
    proposed_id = "".join(random.choice(allowed_chars) for x in range(3))
    while proposed_id in company_ids:
        proposed_id = "".join(random.choice(allowed_chars) for x in range(3))
    return proposed_id


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


def create_public_company(db: Session, company: PubliCompanyAdd):
    new_company = PublicCompany(
        uuid=str(uuid4()),
        name=company.name,
        short_name=company.short_name,
        nip=company.nip,
        country=company.country,
        city=company.city,
        qr_id=generate_qr_id(company.nip),
    )

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return new_company
