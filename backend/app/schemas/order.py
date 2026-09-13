from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class PurchaseItemRequest(BaseModel):
    product_id: int = Field(gt=0, examples=[1])
    quantity: int = Field(default=1, ge=1, le=99, examples=[1])


class PurchaseRequest(BaseModel):
    items: list[PurchaseItemRequest] = Field(min_length=1)


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    product_title: str
    location: str
    unit_price: Decimal
    quantity: int
    line_total: Decimal


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_number: str
    total_amount: Decimal
    status: str
    created_at: datetime
    items: list[OrderItemResponse]
