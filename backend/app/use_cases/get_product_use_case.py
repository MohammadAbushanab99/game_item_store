from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductResponse
from app.validators.product_validator import ProductValidator


class GetProductUseCase:
    def __init__(
        self, product_repository: ProductRepository, validator: ProductValidator
    ):
        self.product_repository = product_repository
        self.validator = validator

    def execute(
        self, product_id: int, allowed_locations: set[str] | None = None
    ) -> ProductResponse:
        product = self.product_repository.find_by_id(product_id)
        product = self.validator.validate_exists(product, product_id)
        product = self.validator.validate_access(product, product_id, allowed_locations)
        return ProductResponse.model_validate(product)
