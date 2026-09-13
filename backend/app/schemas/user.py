from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool
    has_all_countries: bool
    countries: list[str]


class UserAccessUpdate(BaseModel):
    has_all_countries: bool = False
    countries: list[str] = Field(default_factory=list)
