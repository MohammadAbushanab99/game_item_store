from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from app.models.user_country import UserCountry


class UserCountryRepository:
    def __init__(self, db: Session):
        self.db = db

    def codes_for_user(self, user_id: int) -> set[str]:
        rows = self.db.scalars(
            select(UserCountry.country_code).where(UserCountry.user_id == user_id)
        ).all()
        return set(rows)

    def codes_by_user(self) -> dict[int, list[str]]:
        result: dict[int, list[str]] = {}
        for user_id, code in self.db.execute(
            select(UserCountry.user_id, UserCountry.country_code)
        ).all():
            result.setdefault(user_id, []).append(code)
        return result

    def set_for_user(self, user_id: int, codes: list[str]) -> None:
        self.db.execute(delete(UserCountry).where(UserCountry.user_id == user_id))
        for code in dict.fromkeys(codes):
            self.db.add(UserCountry(user_id=user_id, country_code=code))
        self.db.commit()
