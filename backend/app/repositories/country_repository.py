from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.country import Country


class CountryRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all(self) -> list[Country]:
        return list(self.db.scalars(select(Country).order_by(Country.code)).all())

    def find_by_code(self, code: str) -> Country | None:
        return self.db.get(Country, code)

    def all_codes(self) -> set[str]:
        return set(self.db.scalars(select(Country.code)).all())

    def save(self, country: Country) -> Country:
        self.db.add(country)
        self.db.commit()
        self.db.refresh(country)
        return country
