from pydantic import BaseModel, Field
from typing import Optional


class SendCodeRequest(BaseModel):
    phone: str = Field(..., min_length=11, max_length=20, examples=["13800138000"])
    email: Optional[str] = Field(None, examples=["user@example.com"])


class LoginRequest(BaseModel):
    phone: str = Field(..., min_length=11, max_length=20)
    code: str = Field(..., min_length=6, max_length=6)
    nickname: Optional[str] = Field(None, min_length=1, max_length=50)


class WxLoginRequest(BaseModel):
    code: str = Field(..., min_length=1, examples=["0a3lGd000xxx"])


class PasswordLoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)


class BindUsernameRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    nickname: Optional[str] = Field(None, min_length=1, max_length=50)
    birthday: Optional[str] = Field(None, examples=["2000-01-15"])


class BindEmailRequest(BaseModel):
    email: str = Field(..., examples=["user@example.com"])


class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = Field(None, min_length=1, max_length=50)
    birthday: Optional[str] = Field(None, examples=["2000-01-15"])
    gender: Optional[str] = Field(None, pattern="^(male|female)$")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    nickname: str


class UserProfile(BaseModel):
    id: str
    phone: Optional[str] = None
    nickname: str
    avatar_url: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    birthday: Optional[str] = None
    gender: Optional[str] = None
    has_couple: bool
    has_password: bool = False
