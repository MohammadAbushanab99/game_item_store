from datetime import date
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query
from app.api.deps import get_current_admin, get_report_service, get_user_admin_service
from app.schemas.common import ErrorResponse
from app.schemas.report import SalesReport
from app.schemas.user import UserAccessUpdate, UserResponse
from app.services.report_service import ReportService
from app.services.user_admin_service import UserAdminService

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_current_admin)],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
UserAdminServiceDep = Annotated[UserAdminService, Depends(get_user_admin_service)]
ReportServiceDep = Annotated[ReportService, Depends(get_report_service)]


@router.get(
    "/users",
    response_model=list[UserResponse],
    summary="List users with their country access (admin only)",
)
def list_users(service: UserAdminServiceDep):
    return service.list_users()


@router.put(
    "/users/{user_id}/access",
    response_model=UserResponse,
    summary="Set which countries a user may access (admin only)",
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def update_user_access(
    request: UserAccessUpdate,
    service: UserAdminServiceDep,
    user_id: Annotated[int, Path(gt=0)],
):
    return service.update_access(user_id, request)


@router.get(
    "/reports/sales",
    response_model=SalesReport,
    summary="Sales per day and country (admin only)",
)
def sales_report(
    service: ReportServiceDep,
    date_from: Annotated[date | None, Query(description="Inclusive start date")] = None,
    date_to: Annotated[date | None, Query(description="Inclusive end date")] = None,
):
    return service.sales_report(date_from, date_to)
