from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderResponse
from app.validators.order_validator import OrderValidator


class GetOrderUseCase:
    def __init__(self, order_repository: OrderRepository, validator: OrderValidator):
        self.order_repository = order_repository
        self.validator = validator

    def execute(self, user_id: int, order_id: int) -> OrderResponse:
        order = self.order_repository.find_by_id(order_id)
        order = self.validator.validate_owner(order, order_id, user_id)
        return OrderResponse.model_validate(order)
