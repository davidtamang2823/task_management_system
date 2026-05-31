import abc
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from user.domain import models as user_domain_models
from user.adapters import orm as user_orm

class AbstractUserRepository(abc.ABC):


    @abc.abstractmethod
    async def get_users(self, user_filters: dict) -> list[dict]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_email(self, email: str):
        raise NotImplementedError()
    
    @abc.abstractmethod
    async def add(self, user_data: user_domain_models.User):
        raise NotImplementedError()


class UserRepository(AbstractUserRepository):

    def __init__(self, session):
        self.session = session

    async def get_users(self, user_filters: dict) -> list[dict]:
        stmt = (
            select(user_orm.User)
            .options(selectinload(user_orm.User.role))
        )

        if manager_id := user_filters.get("manager_id"):
            stmt = stmt.where(user_orm.User.manager_id == manager_id)

        result = await self.session.execute(stmt)
        users = result.scalars().all()

        return [self._to_dict(user) for user in users]


    async def get_by_email(self, email: str):
        stmt = (
            select(user_orm.User)
            .where(user_orm.User.email == email)
            .options(selectinload(user_orm.User.role))
        )
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        return self._to_dict(user)

    async def add(self, user_data: user_domain_models.User):
        user = user_orm.User(
            email=user_data.email,
            password=user_data.hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_active=True,
            role_id=user_data.role_id,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user, ["role"])

        return self._to_dict(user)
    
    @staticmethod
    def _to_dict(user: user_orm.User) -> dict:
        return {
            "id": user.id,
            "email": user.email,
            "password": user.password,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "role_id": user.role_id,
            "role": user.role.name if user.role else None,
            "manager_id": user.manager_id,
        }