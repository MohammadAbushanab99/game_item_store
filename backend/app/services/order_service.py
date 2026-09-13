from app.schemas.order import OrderResponse, PurchaseRequest
from app.use_cases.create_order_use_case import CreateOrderUseCase
from app.use_cases.get_order_use_case import GetOrderUseCase


class OrderService:
    def __init__(
        self,
        create_order_use_case: CreateOrderUseCase,
        get_order_use_case: GetOrderUseCase,
    ):
        self.create_order_use_case = create_order_use_case
        self.get_order_use_case = get_order_use_case

    def purchase(
        self,
        user_id: int,
        request: PurchaseRequest,
        allowed_locations: set[str] | None = None,
    ) -> OrderResponse:
        return self.create_order_use_case.execute(user_id, request, allowed_locations)

    def get_order(self, user_id: int, order_id: int) -> OrderResponse:
        return self.get_order_use_case.execute(user_id, order_id)
