from typing import Annotated
from fastapi import APIRouter, Depends
from app.api.deps import get_auth_service
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.common import ErrorResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in and get a JWT access token",
    responses={401: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
)
def login(
    request: LoginRequest, service: Annotated[AuthService, Depends(get_auth_service)]
):
    return service.login(request)
