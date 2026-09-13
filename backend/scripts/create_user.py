import sys
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


def create_user(username: str, password: str, is_admin: bool = False) -> None:
    db = SessionLocal()
    try:
        repo = UserRepository(db)
        if repo.find_by_username(username):
            print(f"User '{username}' already exists")
            return
        repo.save(
            User(
                username=username,
                hashed_password=hash_password(password),
                is_admin=is_admin,
            )
        )
        role = "admin" if is_admin else "user"
        print(f"User '{username}' created ({role})")
    finally:
        db.close()


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--admin"]
    is_admin = "--admin" in sys.argv[1:]
    if len(args) != 2:
        print("Usage: python -m scripts.create_user <username> <password> [--admin]")
        sys.exit(1)
    create_user(args[0], args[1], is_admin)
