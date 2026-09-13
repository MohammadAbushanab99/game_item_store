from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
from app.models.enums import OrderStatus
from app.models.order import Order
from app.models.order_item import OrderItem
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.order import OrderResponse, PurchaseRequest
from app.validators.order_validator import OrderValidator


class CreateOrderUseCase:
    def __init__(
        self,
        product_repository: ProductRepository,
        order_repository: OrderRepository,
        validator: OrderValidator,
    ):
        self.product_repository = product_repository
        self.order_repository = order_repository
        self.validator = validator

    def execute(
        self,
        user_id: int,
        request: PurchaseRequest,
        allowed_locations: set[str] | None = None,
    ) -> OrderResponse:
        merged: dict[int, int] = {}
        for item in request.items:
            merged[item.product_id] = merged.get(item.product_id, 0) + item.quantity
        order_items: list[OrderItem] = []
        total = Decimal("0")
        for product_id, quantity in merged.items():
            product = self.product_repository.find_by_id(product_id)
            product = self.validator.validate_can_purchase(
                product, product_id, allowed_locations
            )
            line_total = product.price * quantity
            total += line_total
            order_items.append(
                OrderItem(
                    product_id=product.id,
                    product_title=product.title,
                    location=product.location,
                    unit_price=product.price,
                    quantity=quantity,
                    line_total=line_total,
                )
            )
        order = Order(
            order_number=self._generate_order_number(),
            user_id=user_id,
            total_amount=total,
            status=OrderStatus.COMPLETED.value,
            items=order_items,
        )
        saved = self.order_repository.save(order)
        return OrderResponse.model_validate(saved)

    @staticmethod
    def _generate_order_number() -> str:
        return f"ORD-{datetime.now(timezone.utc):%Y%m%d}-{uuid4().hex[:8].upper()}"
