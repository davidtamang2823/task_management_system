from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from user.adapters.repositories import UserRepository
from role_permission.adapters.repositories import RolePermissionRepository
from task.adapters.repositories import TaskRepository


class UnitOfWork:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.session.commit()
        else:
            await self.session.rollback()
    
    @property
    def user_repository(self):
        return UserRepository(self.session)
    
    @property
    def role_permission_repository(self):
        return RolePermissionRepository(self.session)
    
    @property
    def task_repository(self):
        return TaskRepository(self.session)

async def get_uow(session=Depends(get_session)):
    async with UnitOfWork(session) as uow:
        yield uow