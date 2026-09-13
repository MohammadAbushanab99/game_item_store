from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class SalesRow(BaseModel):
    day: date
    location: str
    orders: int
    items_sold: int
    revenue: Decimal


class SalesReport(BaseModel):
    rows: list[SalesRow]
    total_orders: int
    total_revenue: Decimal
