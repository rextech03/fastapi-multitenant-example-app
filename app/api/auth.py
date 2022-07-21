from app.crud import crud_auth
from app.db import engine, get_public_db
from app.models.models import User
from app.models.shared_models import PublicUser, Tenant
from app.schemas.requests import UserRegisterIn
from app.schemas.responses import StandardResponse
from app.schemas.schemas import UserLoginIn, UserLoginOut
from app.service import auth
from app.service.password import Password
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

auth_router = APIRouter()


@auth_router.post("/register", response_model=StandardResponse)
async def auth_register(*, shared_db: Session = Depends(get_public_db), user: UserRegisterIn):

    if auth.is_email_temporary(user.email):
        raise HTTPException(status_code=400, detail="Temporary email not allowed")

    db_user = crud_auth.get_user_by_email(shared_db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")

    is_password_ok = Password(user.password).compare(user.password_confirmation)

    if is_password_ok is False:
        raise HTTPException(status_code=400, detail=is_password_ok)

    if auth.is_timezone_correct is False:
        raise HTTPException(status_code=400, detail="Invalid timezone")

    crud_auth.create_public_user(shared_db, user)

    return {"ok": True}


@auth_router.post("/login")  # , response_model=UserLoginOut
async def auth_login(*, shared_db: Session = Depends(get_public_db), users: UserLoginIn, req: Request):
    ua_string = req.headers["User-Agent"]
    # browser_lang = req.headers["accept-language"]

    try:
        res = UserLoginIn.from_orm(users)

        db_shared_user = shared_db.execute(
            select(PublicUser).where(PublicUser.email == res.email).where(PublicUser.is_active == True)
        ).scalar_one_or_none()

        db_shared_tenant = shared_db.execute(
            select(Tenant).where(Tenant.id == db_shared_user.tenant_id)
        ).scalar_one_or_none()

        if db_shared_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # ----------------
        schema_translate_map = dict(tenant=db_shared_tenant.schema)
        connectable = engine.execution_options(schema_translate_map=schema_translate_map)
        with Session(autocommit=False, autoflush=False, bind=connectable, future=True) as db:
            db_user = db.execute(select(User).where(User.id == 1)).scalar_one_or_none()

    except Exception as err:
        print(err)
        raise HTTPException(status_code=404, detail="User not found")

    return db_user
