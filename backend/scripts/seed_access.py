from app.core.database import SessionLocal
from app.repositories.user_repository import UserRepository


# Give the demo user all-country access so it can browse everything out of the box.
def seed_access() -> None:
    db = SessionLocal()
    try:
        repo = UserRepository(db)
        demo = repo.find_by_username("demo")
        if demo and (not demo.has_all_countries):
            demo.has_all_countries = True
            db.commit()
            print("Granted demo access to all countries")
        else:
            print("demo access already configured")
    finally:
        db.close()


if __name__ == "__main__":
    seed_access()
