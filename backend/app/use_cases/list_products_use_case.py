import math
from app.repositories.product_repository import ProductRepository
from app.schemas.common import PageResponse
from app.schemas.product import ProductResponse


class ListProductsUseCase:
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository

    def execute(
        self,
        page: int,
        size: int,
        location: str | None,
        allowed_locations: set[str] | None = None,
    ) -> PageResponse[ProductResponse]:
        loc = location.strip().upper() if location else None
        products, total = self.product_repository.find_page(
            page, size, loc, allowed_locations
        )
        return PageResponse[ProductResponse](
            items=[ProductResponse.model_validate(p) for p in products],
            page=page,
            size=size,
            total_items=total,
            total_pages=math.ceil(total / size) if total else 0,
        )
