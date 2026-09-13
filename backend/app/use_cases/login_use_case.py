from app.core.config import settings
from app.core.security import create_access_token
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse
from app.validators.auth_validator import AuthValidator


class LoginUseCase:
    def __init__(self, user_repository: UserRepository, validator: AuthValidator):
        self.user_repository = user_repository
        self.validator = validator

    def execute(self, request: LoginRequest) -> TokenResponse:
        user = self.user_repository.find_by_username(request.username)
        user = self.validator.validate_credentials(user, request.password)
        token = create_access_token(user.id, user.username, user.is_admin)
        return TokenResponse(
            access_token=token,
            expires_in=settings.jwt_expire_minutes * 60,
            is_admin=user.is_admin,
        )
