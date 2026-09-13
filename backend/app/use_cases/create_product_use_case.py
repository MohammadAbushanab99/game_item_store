from app.core.exceptions import AppException
from app.models.product import Product
from app.repositories.country_repository import CountryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreateRequest, ProductResponse
from app.validators.country_validator import CountryValidator


class CreateProductUseCase:
    def __init__(
        self,
        product_repository: ProductRepository,
        country_repository: CountryRepository,
        country_validator: CountryValidator,
    ):
        self.product_repository = product_repository
        self.country_repository = country_repository
        self.country_validator = country_validator

    def execute(self, request: ProductCreateRequest) -> ProductResponse:
        code = request.location.strip().upper()
        self.country_validator.validate_exists(
            self.country_repository.find_by_code(code), code
        )
        if request.id is not None:
            if self.product_repository.find_by_id(request.id) is not None:
                raise AppException(f"A product with id {request.id} already exists.")
            product_id = request.id
        else:
            product_id = self.product_repository.next_id()
        product = self.product_repository.save(
            Product(
                id=product_id,
                title=request.title,
                description=request.description,
                price=request.price,
                location=code,
            )
        )
        return ProductResponse.model_validate(product)
