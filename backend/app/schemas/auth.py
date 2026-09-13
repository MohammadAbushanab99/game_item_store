from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50, examples=["demo"])
    password: str = Field(min_length=6, max_length=72, examples=["Demo@12345"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    is_admin: bool = False
