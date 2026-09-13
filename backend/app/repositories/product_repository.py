from collections.abc import Iterable
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.product import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, product_id: int) -> Product | None:
        return self.db.get(Product, product_id)

    def existing_ids(self, ids: Iterable[int]) -> set[int]:
        ids = list(ids)
        if not ids:
            return set()
        return set(self.db.scalars(select(Product.id).where(Product.id.in_(ids))).all())

    def next_id(self) -> int:
        return (self.db.scalar(select(func.max(Product.id))) or 0) + 1

    def save(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def bulk_save(self, products: list[Product]) -> int:
        self.db.add_all(products)
        self.db.commit()
        return len(products)

    def find_page(
        self,
        page: int,
        size: int,
        location: str | None = None,
        allowed_locations: set[str] | None = None,
    ) -> tuple[list[Product], int]:
        query = select(Product)
        count_query = select(func.count()).select_from(Product)
        if allowed_locations is not None:
            query = query.where(Product.location.in_(allowed_locations))
            count_query = count_query.where(Product.location.in_(allowed_locations))
        if location:
            query = query.where(Product.location == location)
            count_query = count_query.where(Product.location == location)
        total = self.db.scalar(count_query) or 0
        items = self.db.scalars(
            query.order_by(Product.id).offset((page - 1) * size).limit(size)
        ).all()
        return (list(items), total)
