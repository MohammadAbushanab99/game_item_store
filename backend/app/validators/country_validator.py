from app.core.exceptions import AppException
from app.models.country import Country


class CountryValidator:
    def validate_is_new(self, existing: Country | None, code: str) -> None:
        if existing is not None:
            raise AppException(f"Country '{code}' already exists.")

    def validate_exists(self, country: Country | None, code: str) -> Country:
        if country is None:
            raise AppException(
                f"Unknown country '{code}'. Add it first, then try again."
            )
        return country
