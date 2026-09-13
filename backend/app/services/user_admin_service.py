from app.schemas.user import UserAccessUpdate, UserResponse
from app.use_cases.list_users_use_case import ListUsersUseCase
from app.use_cases.update_user_access_use_case import UpdateUserAccessUseCase


class UserAdminService:
    def __init__(
        self,
        list_users_use_case: ListUsersUseCase,
        update_user_access_use_case: UpdateUserAccessUseCase,
    ):
        self.list_users_use_case = list_users_use_case
        self.update_user_access_use_case = update_user_access_use_case

    def list_users(self) -> list[UserResponse]:
        return self.list_users_use_case.execute()

    def update_access(self, user_id: int, request: UserAccessUpdate) -> UserResponse:
        return self.update_user_access_use_case.execute(user_id, request)
