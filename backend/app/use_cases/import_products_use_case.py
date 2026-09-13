from app.core.file_parsing import parse_import_file
from app.repositories.country_repository import CountryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.country import ImportResult
from app.validators.import_validator import ImportValidator, _to_int


class ImportProductsUseCase:
    def __init__(
        self,
        product_repository: ProductRepository,
        country_repository: CountryRepository,
        validator: ImportValidator,
    ):
        self.product_repository = product_repository
        self.country_repository = country_repository
        self.validator = validator

    def execute(self, filename: str, content: bytes) -> ImportResult:
        headers, rows = parse_import_file(filename, content)
        candidate_ids: set[int] = set()
        for _, row in rows:
            try:
                candidate_ids.add(_to_int(row.get("id")))
            except (ValueError, TypeError):
                pass
        existing_ids = self.product_repository.existing_ids(candidate_ids)
        valid_codes = self.country_repository.all_codes()
        products = self.validator.validate(headers, rows, existing_ids, valid_codes)
        count = self.product_repository.bulk_save(products)
        return ImportResult(inserted=count, message=f"Imported {count} product(s).")
