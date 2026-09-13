from decimal import Decimal, InvalidOperation
from app.core.exceptions import ImportValidationException
from app.models.product import Product

REQUIRED_COLUMNS = ["id", "title", "description", "price"]
COUNTRY_COLUMN_ALIASES = ("country", "location")


def _row_error(row_number: int, message: str) -> dict:
    return {"field": f"row {row_number}", "message": message}


def _to_int(value) -> int:
    if isinstance(value, bool):
        raise ValueError
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        raise ValueError
    return int(str(value).strip())


def _to_decimal(value) -> Decimal:
    if isinstance(value, bool):
        raise ValueError
    try:
        amount = Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise ValueError from exc
    if amount < 0:
        raise ValueError
    if -amount.as_tuple().exponent > 2:
        raise ValueError
    return amount


class ImportValidator:
    def validate(
        self,
        headers: list[str],
        rows: list[tuple[int, dict]],
        existing_ids: set[int],
        valid_country_codes: set[str],
    ) -> list[Product]:
        country_column = next((c for c in COUNTRY_COLUMN_ALIASES if c in headers), None)
        missing_columns = [c for c in REQUIRED_COLUMNS if c not in headers]
        if country_column is None:
            missing_columns.append("country")
        if missing_columns:
            raise ImportValidationException(
                f"The file must contain the columns: id, title, description, price, country. Missing: {', '.join(missing_columns)}."
            )
        if not rows:
            raise ImportValidationException("The file has no data rows.")
        errors: list[dict] = []
        seen_ids: dict[int, int] = {}
        products: list[Product] = []
        for row_number, row in rows:
            values = {
                "id": row.get("id"),
                "title": row.get("title"),
                "description": row.get("description"),
                "price": row.get("price"),
                "country": row.get(country_column),
            }
            missing = [
                name
                for name, value in values.items()
                if value is None or str(value).strip() == ""
            ]
            if missing:
                errors.append(
                    _row_error(
                        row_number, f"missing required value(s): {', '.join(missing)}"
                    )
                )
                continue
            try:
                product_id = _to_int(values["id"])
            except (ValueError, TypeError):
                errors.append(
                    _row_error(
                        row_number, f"id '{values['id']}' must be a positive integer"
                    )
                )
                continue
            if product_id <= 0:
                errors.append(
                    _row_error(
                        row_number, f"id '{values['id']}' must be a positive integer"
                    )
                )
                continue
            try:
                price = _to_decimal(values["price"])
            except (ValueError, TypeError):
                errors.append(
                    _row_error(
                        row_number,
                        f"price '{values['price']}' must be a valid number (>= 0, up to 2 decimals)",
                    )
                )
                continue
            code = str(values["country"]).strip().upper()
            if code not in valid_country_codes:
                errors.append(
                    _row_error(
                        row_number,
                        f"unknown country '{code}'. Add it first, then re-import.",
                    )
                )
                continue
            if product_id in seen_ids:
                errors.append(
                    _row_error(
                        row_number,
                        f"duplicate id {product_id} (already used in row {seen_ids[product_id]})",
                    )
                )
                continue
            if product_id in existing_ids:
                errors.append(
                    _row_error(
                        row_number, f"id {product_id} already exists in the catalogue"
                    )
                )
                continue
            seen_ids[product_id] = row_number
            products.append(
                Product(
                    id=product_id,
                    title=str(values["title"]).strip(),
                    description=str(values["description"]).strip(),
                    price=price,
                    location=code,
                )
            )
        if errors:
            raise ImportValidationException(
                "Import cancelled: fix the problems listed below. No rows were imported.",
                details=errors,
            )
        return products
