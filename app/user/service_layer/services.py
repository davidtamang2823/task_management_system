import abc
import typing
from datetime import datetime, timedelta, timezone
from user.domain.commands import (
    CreateUserCommand,
    AuthenticateUserCommand
)
from common.unit_of_work import UnitOfWork
from user.adapters.repositories import AbstractUserRepository
from security import AbstractAuthHandler
from user.service_layer.exceptions import UserAlreadyExistsError, UserNotFoundError, InvalidCredentialsError
from common.constants import ROLE_USER, PERMISSION_VIEW_ALL_USERS
from settings import settings
from common.permissions import AbstractPermissionChecker

class AbstractUserService(abc.ABC):

    @abc.abstractmethod
    async def list_users(self, current_user_id:int, current_user_role_id:int,  user_filters: typing.Dict):
        raise NotImplementedError

    @abc.abstractmethod
    async def create_user(self, user_data: CreateUserCommand):
        raise NotImplementedError()
    
    @abc.abstractmethod
    async def authenticate_user(self, authenticate_data: AuthenticateUserCommand):
        raise NotImplementedError()


class AbstractListUserService(abc.ABC):

    @abc.abstractmethod
    async def list_users(self, user_filters: typing.Dict[str, typing.Any]):
        raise NotImplementedError()


class UserService(AbstractUserService):

    def __init__(self, uow: UnitOfWork, auth_handler: AbstractAuthHandler, permission_checker: AbstractPermissionChecker):
        self.uow = uow
        self.auth_handler = auth_handler
        self.permission_checker = permission_checker


    async def list_users(self, current_user_id:int, current_user_role_id:int,  user_filters: typing.Dict):
        has_permission = await self.permission_checker.check(
            current_user_role_id,
            [PERMISSION_VIEW_ALL_USERS],
        )

        if not has_permission:
            user_filters["manager_id"] = current_user_id

        users = await self.uow.user_repository.get_users(user_filters)
        return users


    async def create_user(self, user_data: CreateUserCommand):
        existing_user = await self.uow.user_repository.get_by_email(user_data.email)
        if existing_user is not None:
            raise UserAlreadyExistsError()
        
        default_role = await self.uow.role_permission_repository.get_role_by_name(ROLE_USER)
        user_data.hashed_password = self.auth_handler.hash_password(user_data.password)
        user_data.role_id = default_role.get("id")

        return await self.uow.user_repository.add(user_data)
    
    async def authenticate_user(self, authenticate_data: AuthenticateUserCommand):
        user = await self.uow.user_repository.get_by_email(authenticate_data.email)

        if user is None:
            raise UserNotFoundError()

        if not self.auth_handler.verify_password(authenticate_data.password, user.get("password")):
            raise InvalidCredentialsError()

        token = self.auth_handler.create_access_token(
            header={
                "alg": settings.jwt_algorithm,
                "typ": "JWT",
            },
            payload={
                "sub": str(user.get("id")),
                "iat": datetime.now(timezone.utc),
                "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes),
                "email": user.get("email"),
                "role": user.get("role"),
            },
        )

        return {"access_token": token, "token_type": "bearer"}


class UserListService(AbstractListUserService):

    def __init__(self, uow):
        self.uow = uow

    async def list_users(self, user_filters: typing.Dict[str, typing.Any]):
        ...
