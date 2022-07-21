from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from unidecode import unidecode

from app.crud import crud_auth
from app.db import get_public_db
from app.schemas.requests import UserFirstRunIn, UserRegisterIn
from app.schemas.responses import StandardResponse
from app.service import auth
from app.service.api_rejestr_io import get_company_details
from app.service.password import Password
from app.service.tenants import alembic_upgrade_head, tenant_create

auth_router = APIRouter()


@auth_router.post("/register", response_model=StandardResponse)
async def auth_register(
    *, shared_db: Session = Depends(get_public_db), user: UserRegisterIn
):

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


@auth_router.post("/first_run")
async def auth_first_run(
    *, shared_db: Session = Depends(get_public_db), user: UserFirstRunIn
):
    """Activate user based on service token"""

    if auth.is_nip_correct(user.nip):  # 123-456-32-18
        raise HTTPException(status_code=400, detail="Invalid NIP number")

    db_user = crud_auth.get_user_by_service_token(shared_db, user.token)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_company = crud_auth.get_company_by_nip(shared_db, user.nip)
    user_role_id = 2  # SUPER_ADMIN[1] / USER[2] / VIEWER[3]
    is_verified = False

    if not db_company:
        company_data = get_company_details(user.nip)
        print("#####")
        db_company = crud_auth.create_public_company(shared_db, company_data)
        tenanat_id = unidecode(db_company.short_name).lower()

        tenant_create(tenanat_id, tenanat_id, tenanat_id)
        alembic_upgrade_head(tenanat_id)
        user_role_id = 1  # SUPER_ADMIN[1] / USER[2] / VIEWER[3]
        is_verified = True

    update_package = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": True,
        "is_verified": is_verified,
        "user_role_id": user_role_id,
        "service_token": None,
        "service_token_valid_to": None,
        "updated_at": datetime.utcnow(),
    }

    for key, value in update_package.items():
        setattr(db_user, key, value)
    shared_db.add(db_user)
    shared_db.commit()
    shared_db.refresh(db_user)

    # return {
    #     "ok": True,
    #     "first_name": db_user.first_name,
    #     "last_name": db_user.last_name,
    #     "lang": db_user.lang,
    #     "tz": db_user.tz,
    #     "uuid": db_user.uuid,
    #     "token": token,
    # }
    return data


# @auth_router.post("/login")  # , response_model=UserLoginOut
# async def auth_login(*, shared_db: Session = Depends(get_public_db), users: UserLoginIn, req: Request):
#     ua_string = req.headers["User-Agent"]
#     # browser_lang = req.headers["accept-language"]

#     try:
#         res = UserLoginIn.from_orm(users)

#         db_shared_user = shared_db.execute(
#             select(PublicUser).where(PublicUser.email == res.email).where(PublicUser.is_active == True)
#         ).scalar_one_or_none()

#         db_shared_tenant = shared_db.execute(
#             select(Tenant).where(Tenant.id == db_shared_user.tenant_id)
#         ).scalar_one_or_none()

#         if db_shared_user is None:
#             raise HTTPException(status_code=404, detail="User not found")

#         # ----------------
#         schema_translate_map = dict(tenant=db_shared_tenant.schema)
#         connectable = engine.execution_options(schema_translate_map=schema_translate_map)
#         with Session(autocommit=False, autoflush=False, bind=connectable, future=True) as db:
#             db_user = db.execute(select(User).where(User.id == 1)).scalar_one_or_none()

#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=404, detail="User not found")

#     return db_user
