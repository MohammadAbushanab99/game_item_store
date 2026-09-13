from typing import Annotated
from fastapi import APIRouter, Depends, status
from app.api.deps import (
    AllowedCountries,
    get_country_service,
    get_current_admin,
    get_current_user,
)
from app.schemas.common import ErrorResponse
from app.schemas.country import CountryCreateRequest, CountryResponse
from app.services.country_service import CountryService

router = APIRouter(
    prefix="/countries",
    tags=["Countries"],
    dependencies=[Depends(get_current_user)],
    responses={401: {"model": ErrorResponse}},
)
CountryServiceDep = Annotated[CountryService, Depends(get_country_service)]


@router.get(
    "",
    response_model=list[CountryResponse],
    summary="List countries (used by the product filter)",
)
def list_countries(service: CountryServiceDep, allowed: AllowedCountries):
    return service.list_countries(allowed)


@router.post(
    "",
    response_model=CountryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new country (admin only)",
    dependencies=[Depends(get_current_admin)],
    responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def create_country(request: CountryCreateRequest, service: CountryServiceDep):
    return service.create_country(request)
