from app.schemas.auth import LoginRequest, TokenResponse
from app.use_cases.login_use_case import LoginUseCase


class AuthService:
    def __init__(self, login_use_case: LoginUseCase):
        self.login_use_case = login_use_case

    def login(self, request: LoginRequest) -> TokenResponse:
        return self.login_use_case.execute(request)
