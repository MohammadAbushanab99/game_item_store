from app.core.exceptions import UnauthorizedException
from app.core.security import verify_password
from app.models.user import User


class AuthValidator:
    def validate_credentials(self, user: User | None, password: str) -> User:
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid username or password")
        return user
