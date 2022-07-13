from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr


class StandardResponse(BaseModel):  # OK
    ok: bool


class Books(BaseModel):
    __tablename__ = "books"
    id: int | None
    title: str | None
    author: str | None

    class Config:
        orm_mode = True
