from typing import Annotated
from fastapi import APIRouter, Depends, Path, status
from app.api.deps import AllowedCountries, CurrentUser, get_order_service
from app.schemas.common import ErrorResponse
from app.schemas.order import OrderResponse, PurchaseRequest
from app.services.order_service import OrderService

router = APIRouter(
    prefix="/orders", tags=["Orders"], responses={401: {"model": ErrorResponse}}
)
OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Check out a cart of items -> creates one order (bill) and returns it",
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
    },
)
def purchase(
    request: PurchaseRequest,
    user: CurrentUser,
    service: OrderServiceDep,
    allowed: AllowedCountries,
):
    return service.purchase(user.id, request, allowed)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get one of my orders (used by the receipt page)",
    responses={404: {"model": ErrorResponse}},
)
def get_order(
    order_id: Annotated[int, Path(gt=0)], user: CurrentUser, service: OrderServiceDep
):
    return service.get_order(user.id, order_id)
