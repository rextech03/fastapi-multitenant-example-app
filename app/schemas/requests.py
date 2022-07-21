from pydantic import BaseModel, EmailStr


class BaseRequest(BaseModel):
    # may define additional fields or config shared across requests
    pass


class UserRegisterIn(BaseRequest):  # OK
    email: EmailStr
    password: str
    password_confirmation: str
    tos: bool
    tz: str | None = "Europe/Warsaw"
    lang: str | None = "pl"
