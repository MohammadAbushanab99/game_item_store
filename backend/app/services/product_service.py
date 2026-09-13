from app.schemas.common import PageResponse
from app.schemas.product import ProductResponse
from app.use_cases.get_product_use_case import GetProductUseCase
from app.use_cases.list_products_use_case import ListProductsUseCase


class ProductService:
    def __init__(
        self,
        list_products_use_case: ListProductsUseCase,
        get_product_use_case: GetProductUseCase,
    ):
        self.list_products_use_case = list_products_use_case
        self.get_product_use_case = get_product_use_case

    def list_products(
        self,
        page: int,
        size: int,
        location: str | None,
        allowed_locations: set[str] | None = None,
    ) -> PageResponse[ProductResponse]:
        return self.list_products_use_case.execute(
            page, size, location, allowed_locations
        )

    def get_product(
        self, product_id: int, allowed_locations: set[str] | None = None
    ) -> ProductResponse:
        return self.get_product_use_case.execute(product_id, allowed_locations)
