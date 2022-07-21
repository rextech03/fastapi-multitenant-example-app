from pydantic import BaseModel


class BaseResponse(BaseModel):
    # may define additional fields or config shared across responses
    class Config:
        orm_mode = True


class StandardResponse(BaseResponse):
    ok: bool
