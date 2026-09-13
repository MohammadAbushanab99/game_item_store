from app.repositories.user_country_repository import UserCountryRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse


class ListUsersUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        user_country_repository: UserCountryRepository,
    ):
        self.user_repository = user_repository
        self.user_country_repository = user_country_repository

    def execute(self) -> list[UserResponse]:
        codes_by_user = self.user_country_repository.codes_by_user()
        return [
            UserResponse(
                id=user.id,
                username=user.username,
                is_admin=user.is_admin,
                has_all_countries=user.has_all_countries,
                countries=sorted(codes_by_user.get(user.id, [])),
            )
            for user in self.user_repository.find_all()
        ]
