from app.models.country import Country
from app.repositories.country_repository import CountryRepository
from app.schemas.country import CountryCreateRequest, CountryResponse
from app.validators.country_validator import CountryValidator


class CreateCountryUseCase:
    def __init__(
        self, country_repository: CountryRepository, validator: CountryValidator
    ):
        self.country_repository = country_repository
        self.validator = validator

    def execute(self, request: CountryCreateRequest) -> CountryResponse:
        code = request.code.strip().upper()
        self.validator.validate_is_new(self.country_repository.find_by_code(code), code)
        country = self.country_repository.save(Country(code=code, name=request.name))
        return CountryResponse.model_validate(country)
