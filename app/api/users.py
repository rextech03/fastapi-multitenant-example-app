from app.main import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

user_router = APIRouter()


@user_router.get("/")
async def user_get_all(*, db: Session = Depends(get_db)):

    return {"ok": True}
