from typing import Annotated
from fastapi import APIRouter, Depends, File, Path, Query, UploadFile, status
from app.api.deps import (
    AllowedCountries,
    get_admin_service,
    get_current_admin,
    get_current_user,
    get_product_service,
)
from app.core.exceptions import ImportValidationException
from app.schemas.common import ErrorResponse, PageResponse
from app.schemas.country import ImportResult
from app.schemas.product import ProductCreateRequest, ProductResponse
from app.services.admin_service import AdminService
from app.services.product_service import ProductService

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
router = APIRouter(
    prefix="/products",
    tags=["Products"],
    dependencies=[Depends(get_current_user)],
    responses={401: {"model": ErrorResponse}},
)
ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
AdminServiceDep = Annotated[AdminService, Depends(get_admin_service)]


@router.get(
    "",
    response_model=PageResponse[ProductResponse],
    summary="List products (paginated, optional location filter)",
    responses={400: {"model": ErrorResponse}},
)
def list_products(
    service: ProductServiceDep,
    allowed: AllowedCountries,
    page: Annotated[int, Query(ge=1, description="Page number (starts at 1)")] = 1,
    size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 12,
    location: Annotated[
        str | None, Query(description="Filter by country code, e.g. JO/SA/UAE")
    ] = None,
):
    return service.list_products(page, size, location, allowed)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a single product (admin only)",
    dependencies=[Depends(get_current_admin)],
    responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def create_product(request: ProductCreateRequest, admin_service: AdminServiceDep):
    return admin_service.create_product(request)


@router.post(
    "/import",
    response_model=ImportResult,
    summary="Bulk import products from a .xlsx or .csv file (admin only)",
    dependencies=[Depends(get_current_admin)],
    responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
async def import_products(
    admin_service: AdminServiceDep, file: Annotated[UploadFile, File()]
):
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise ImportValidationException("The file is larger than 5 MB.")
    return admin_service.import_products(file.filename, content)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product details",
    responses={404: {"model": ErrorResponse}},
)
def get_product(
    service: ProductServiceDep,
    allowed: AllowedCountries,
    product_id: Annotated[int, Path(gt=0)],
):
    return service.get_product(product_id, allowed)
