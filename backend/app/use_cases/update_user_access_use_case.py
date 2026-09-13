from app.core.exceptions import AppException, NotFoundException
from app.repositories.country_repository import CountryRepository
from app.repositories.user_country_repository import UserCountryRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserAccessUpdate, UserResponse


class UpdateUserAccessUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        user_country_repository: UserCountryRepository,
        country_repository: CountryRepository,
    ):
        self.user_repository = user_repository
        self.user_country_repository = user_country_repository
        self.country_repository = country_repository

    def execute(self, user_id: int, request: UserAccessUpdate) -> UserResponse:
        user = self.user_repository.find_by_id(user_id)
        if user is None:
            raise NotFoundException(f"User {user_id} not found")
        codes = [c.strip().upper() for c in request.countries]
        valid = self.country_repository.all_codes()
        unknown = [c for c in codes if c not in valid]
        if unknown:
            raise AppException(
                f"Unknown country code(s): {', '.join(sorted(set(unknown)))}."
            )
        user.has_all_countries = request.has_all_countries
        self.user_repository.save(user)
        stored = [] if request.has_all_countries else codes
        self.user_country_repository.set_for_user(user_id, stored)
        return UserResponse(
            id=user.id,
            username=user.username,
            is_admin=user.is_admin,
            has_all_countries=user.has_all_countries,
            countries=sorted(set(stored)),
        )
