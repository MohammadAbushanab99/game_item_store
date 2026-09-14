from app.core.exceptions import BusinessRuleException, NotFoundException
from app.models.order import Order
from app.models.product import Product


# Purchase rules; an out-of-region item returns 404 (not 403) so we never reveal it exists.
class OrderValidator:
    def validate_can_purchase(
        self,
        product: Product | None,
        product_id: int,
        allowed_locations: set[str] | None = None,
    ) -> Product:
        if product is None:
            raise NotFoundException(f"Product {product_id} not found")
        if allowed_locations is not None and product.location not in allowed_locations:
            raise NotFoundException(f"Product {product_id} not found")
        if product.price <= 0:
            raise BusinessRuleException("This product is not available for purchase")
        return product

    def validate_owner(self, order: Order | None, order_id: int, user_id: int) -> Order:
        if order is None or order.user_id != user_id:
            raise NotFoundException(f"Order {order_id} not found")
        return order
