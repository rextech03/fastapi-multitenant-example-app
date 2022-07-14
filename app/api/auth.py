from app.db import SQLALCHEMY_DATABASE_URL, engine, get_public_db
from app.models.models import User
from app.models.shared_models import SharedUser, Tenant
from app.schemas.schemas import StandardResponse, UserLoginIn, UserLoginOut
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

auth_router = APIRouter()


@auth_router.post("/login")  # , response_model=UserLoginOut
async def auth_login(*, shared_db: Session = Depends(get_public_db), users: UserLoginIn, req: Request):
    ua_string = req.headers["User-Agent"]
    # browser_lang = req.headers["accept-language"]

    try:
        res = UserLoginIn.from_orm(users)

        db_shared_user = shared_db.execute(
            select(SharedUser).where(SharedUser.email == res.email).where(SharedUser.is_active == True)
        ).scalar_one_or_none()

        db_shared_tenant = shared_db.execute(
            select(Tenant).where(Tenant.id == db_shared_user.tenant_id)
        ).scalar_one_or_none()

        if db_shared_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # ----------------
        schema_translate_map = dict(tenant=db_shared_tenant.schema)
        connectable = engine.execution_options(schema_translate_map=schema_translate_map)
        with Session(autocommit=False, autoflush=False, bind=connectable) as db:
            db_user = db.execute(select(User).where(User.id == 1)).scalar_one_or_none()

    except Exception as err:
        print(err)
        raise HTTPException(status_code=404, detail="User not found")

    return db_user
