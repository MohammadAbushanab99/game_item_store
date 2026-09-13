from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    price: Decimal
    location: str


class ProductCreateRequest(BaseModel):
    id: int | None = Field(default=None, gt=0)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    location: str = Field(min_length=2, max_length=3, description="Country code")
