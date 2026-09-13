from app.repositories.country_repository import CountryRepository
from app.schemas.country import CountryResponse


class ListCountriesUseCase:
    def __init__(self, country_repository: CountryRepository):
        self.country_repository = country_repository

    def execute(self, allowed_codes: set[str] | None = None) -> list[CountryResponse]:
        countries = self.country_repository.find_all()
        if allowed_codes is not None:
            countries = [c for c in countries if c.code in allowed_codes]
        return [CountryResponse.model_validate(c) for c in countries]
