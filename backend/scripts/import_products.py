import csv
import sys
from decimal import Decimal
from pydantic import BaseModel, Field, ValidationError, field_validator
from app.core.database import SessionLocal
from app.models.product import Product


class ProductCsvRow(BaseModel):
    id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    location: str = Field(min_length=2, max_length=3)

    @field_validator("title", "description", mode="before")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value

    @field_validator("location", mode="before")
    @classmethod
    def upper_location(cls, value: str) -> str:
        return value.strip().upper() if isinstance(value, str) else value


def import_products(csv_path: str) -> None:
    imported, skipped = (0, 0)
    db = SessionLocal()
    try:
        with open(csv_path, newline="", encoding="utf-8") as file:
            for line_number, raw_row in enumerate(csv.DictReader(file), start=2):
                try:
                    row = ProductCsvRow(**raw_row)
                except ValidationError as error:
                    skipped += 1
                    print(f"Line {line_number} skipped: {error.errors()[0]['msg']}")
                    continue
                db.merge(
                    Product(
                        id=row.id,
                        title=row.title,
                        description=row.description,
                        price=row.price,
                        location=row.location,
                    )
                )
                imported += 1
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    print(f"Done. Imported/updated: {imported}, skipped: {skipped}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.import_products <path-to-csv>")
        sys.exit(1)
    import_products(sys.argv[1])
