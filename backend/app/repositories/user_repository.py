from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def find_all(self) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.username)).all())

    def find_by_username(self, username: str) -> User | None:
        return self.db.scalar(select(User).where(User.username == username))

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
