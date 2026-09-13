import os

os.environ["DATABASE_URL"] = "sqlite://"
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models import Country, Product, User, UserCountry

engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def client():
    Base.metadata.create_all(engine)
    db = TestingSession()
    db.add_all(
        [Country(code="JO", name="Jordan"), Country(code="SA", name="Saudi Arabia")]
    )
    db.add_all(
        [
            User(
                username="demo",
                hashed_password=hash_password("Demo@12345"),
                has_all_countries=True,
            ),
            User(
                username="other",
                hashed_password=hash_password("Other@12345"),
                has_all_countries=True,
            ),
            User(
                username="admin",
                hashed_password=hash_password("Admin@12345"),
                is_admin=True,
            ),
            User(
                username="restricted", hashed_password=hash_password("Restrict@12345")
            ),
        ]
    )
    db.add_all(
        [
            Product(
                id=i,
                title=f"Item {i}",
                description="desc",
                price=Decimal("10.50"),
                location="JO" if i % 2 else "SA",
            )
            for i in range(1, 26)
        ]
    )
    db.add(
        Product(
            id=99,
            title="Free",
            description="not for sale",
            price=Decimal("0"),
            location="JO",
        )
    )
    db.commit()
    restricted = db.query(User).filter_by(username="restricted").one()
    db.add(UserCountry(user_id=restricted.id, country_code="JO"))
    db.commit()
    db.close()

    def override_get_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


def login(client, username="demo", password="Demo@12345") -> dict:
    token = client.post(
        "/api/v1/auth/login", json={"username": username, "password": password}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
