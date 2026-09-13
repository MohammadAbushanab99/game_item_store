from app.core.database import SessionLocal
from app.models.country import Country

DEFAULT_COUNTRIES = {"JO": "Jordan", "SA": "Saudi Arabia"}


def seed_countries() -> None:
    db = SessionLocal()
    try:
        added = 0
        for code, name in DEFAULT_COUNTRIES.items():
            if db.get(Country, code) is None:
                db.add(Country(code=code, name=name))
                added += 1
        db.commit()
        print(f"Countries ensured. Added: {added}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_countries()
