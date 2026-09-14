from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.country_repository import CountryRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_country_repository import UserCountryRepository
from app.repositories.user_repository import UserRepository
from app.services.admin_service import AdminService
from app.services.auth_service import AuthService
from app.services.country_service import CountryService
from app.services.order_service import OrderService
from app.services.product_service import ProductService
from app.services.report_service import ReportService
from app.services.user_admin_service import UserAdminService
from app.use_cases.create_country_use_case import CreateCountryUseCase
from app.use_cases.create_order_use_case import CreateOrderUseCase
from app.use_cases.create_product_use_case import CreateProductUseCase
from app.use_cases.get_order_use_case import GetOrderUseCase
from app.use_cases.get_product_use_case import GetProductUseCase
from app.use_cases.import_products_use_case import ImportProductsUseCase
from app.use_cases.list_countries_use_case import ListCountriesUseCase
from app.use_cases.list_products_use_case import ListProductsUseCase
from app.use_cases.list_users_use_case import ListUsersUseCase
from app.use_cases.login_use_case import LoginUseCase
from app.use_cases.sales_report_use_case import SalesReportUseCase
from app.use_cases.update_user_access_use_case import UpdateUserAccessUseCase
from app.validators.auth_validator import AuthValidator
from app.validators.country_validator import CountryValidator
from app.validators.import_validator import ImportValidator
from app.validators.order_validator import OrderValidator
from app.validators.product_validator import ProductValidator

DbSession = Annotated[Session, Depends(get_db)]
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    if credentials is None:
        raise UnauthorizedException("Missing bearer token")
    payload = decode_access_token(credentials.credentials)
    user = UserRepository(db).find_by_id(int(payload["sub"]))
    if user is None:
        raise UnauthorizedException("User no longer exists")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_admin(user: CurrentUser) -> User:
    if not user.is_admin:
        raise ForbiddenException("Admin privileges are required for this action.")
    return user


CurrentAdmin = Annotated[User, Depends(get_current_admin)]


# Country codes the user may access, or None for unrestricted (admin / all-access).
def get_allowed_countries(user: CurrentUser, db: DbSession) -> set[str] | None:
    if user.is_admin or user.has_all_countries:
        return None
    return UserCountryRepository(db).codes_for_user(user.id)


AllowedCountries = Annotated["set[str] | None", Depends(get_allowed_countries)]


def get_auth_service(db: DbSession) -> AuthService:
    return AuthService(LoginUseCase(UserRepository(db), AuthValidator()))


def get_country_service(db: DbSession) -> CountryService:
    repo = CountryRepository(db)
    return CountryService(
        list_countries_use_case=ListCountriesUseCase(repo),
        create_country_use_case=CreateCountryUseCase(repo, CountryValidator()),
    )


def get_admin_service(db: DbSession) -> AdminService:
    product_repo = ProductRepository(db)
    country_repo = CountryRepository(db)
    return AdminService(
        create_product_use_case=CreateProductUseCase(
            product_repo, country_repo, CountryValidator()
        ),
        import_products_use_case=ImportProductsUseCase(
            product_repo, country_repo, ImportValidator()
        ),
    )


def get_report_service(db: DbSession) -> ReportService:
    return ReportService(SalesReportUseCase(OrderRepository(db)))


def get_user_admin_service(db: DbSession) -> UserAdminService:
    user_repo = UserRepository(db)
    user_country_repo = UserCountryRepository(db)
    country_repo = CountryRepository(db)
    return UserAdminService(
        list_users_use_case=ListUsersUseCase(user_repo, user_country_repo),
        update_user_access_use_case=UpdateUserAccessUseCase(
            user_repo, user_country_repo, country_repo
        ),
    )


def get_product_service(db: DbSession) -> ProductService:
    repo = ProductRepository(db)
    validator = ProductValidator()
    return ProductService(
        list_products_use_case=ListProductsUseCase(repo),
        get_product_use_case=GetProductUseCase(repo, validator),
    )


def get_order_service(db: DbSession) -> OrderService:
    order_repo = OrderRepository(db)
    validator = OrderValidator()
    return OrderService(
        create_order_use_case=CreateOrderUseCase(
            ProductRepository(db), order_repo, validator
        ),
        get_order_use_case=GetOrderUseCase(order_repo, validator),
    )
