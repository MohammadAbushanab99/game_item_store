from app.schemas.country import CountryCreateRequest, CountryResponse
from app.use_cases.create_country_use_case import CreateCountryUseCase
from app.use_cases.list_countries_use_case import ListCountriesUseCase


class CountryService:
    def __init__(
        self,
        list_countries_use_case: ListCountriesUseCase,
        create_country_use_case: CreateCountryUseCase,
    ):
        self.list_countries_use_case = list_countries_use_case
        self.create_country_use_case = create_country_use_case

    def list_countries(
        self, allowed_codes: set[str] | None = None
    ) -> list[CountryResponse]:
        return self.list_countries_use_case.execute(allowed_codes)

    def create_country(self, request: CountryCreateRequest) -> CountryResponse:
        return self.create_country_use_case.execute(request)
