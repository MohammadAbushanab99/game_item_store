from app.core.exceptions import NotFoundException
from app.models.product import Product


class ProductValidator:
    def validate_exists(self, product: Product | None, product_id: int) -> Product:
        if product is None:
            raise NotFoundException(f"Product {product_id} not found")
        return product

    def validate_access(
        self, product: Product, product_id: int, allowed_locations: set[str] | None
    ) -> Product:
        if allowed_locations is not None and product.location not in allowed_locations:
            raise NotFoundException(f"Product {product_id} not found")
        return product
