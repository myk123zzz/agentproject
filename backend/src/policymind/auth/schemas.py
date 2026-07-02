"""Pydantic schemas for authentication API requests and responses."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    tenant_slug: str = Field(min_length=2, max_length=64)
    username: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=8, max_length=256)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserInfo(BaseModel):
    id: int
    tenant_id: int
    username: str
    role: str
    access_level: int
