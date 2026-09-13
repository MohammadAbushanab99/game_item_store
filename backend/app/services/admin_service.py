from app.schemas.country import ImportResult
from app.schemas.product import ProductCreateRequest, ProductResponse
from app.use_cases.create_product_use_case import CreateProductUseCase
from app.use_cases.import_products_use_case import ImportProductsUseCase


class AdminService:
    def __init__(
        self,
        create_product_use_case: CreateProductUseCase,
        import_products_use_case: ImportProductsUseCase,
    ):
        self.create_product_use_case = create_product_use_case
        self.import_products_use_case = import_products_use_case

    def create_product(self, request: ProductCreateRequest) -> ProductResponse:
        return self.create_product_use_case.execute(request)

    def import_products(self, filename: str, content: bytes) -> ImportResult:
        return self.import_products_use_case.execute(filename, content)
