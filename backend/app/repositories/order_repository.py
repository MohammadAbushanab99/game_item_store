from datetime import date, timedelta
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.order_item import OrderItem


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, order_id: int) -> Order | None:
        return self.db.get(Order, order_id)

    def save(self, order: Order) -> Order:
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def sales_by_day_and_country(
        self, date_from: date | None, date_to: date | None
    ) -> list[dict]:
        day = func.date(Order.created_at).label("day")
        query = (
            select(
                day,
                OrderItem.location.label("location"),
                func.count(func.distinct(Order.id)).label("orders"),
                func.sum(OrderItem.quantity).label("items_sold"),
                func.sum(OrderItem.line_total).label("revenue"),
            )
            .join(OrderItem, OrderItem.order_id == Order.id)
            .group_by(day, OrderItem.location)
            .order_by(day.desc(), OrderItem.location)
        )
        if date_from is not None:
            query = query.where(Order.created_at >= date_from)
        if date_to is not None:
            query = query.where(Order.created_at < date_to + timedelta(days=1))
        return [dict(row._mapping) for row in self.db.execute(query).all()]
