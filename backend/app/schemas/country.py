from pydantic import BaseModel, ConfigDict, Field, field_validator


class CountryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: str
    name: str


class CountryCreateRequest(BaseModel):
    code: str = Field(
        min_length=2, max_length=3, pattern="^[A-Za-z]{2,3}$", examples=["UAE"]
    )
    name: str = Field(min_length=1, max_length=100, examples=["United Arab Emirates"])

    @field_validator("code", mode="before")
    @classmethod
    def upper_code(cls, value: str) -> str:
        return value.strip().upper() if isinstance(value, str) else value

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value


class ImportResult(BaseModel):
    inserted: int
    message: str
