import abc
from fastapi import status
from fastapi.exceptions import HTTPException
from common.unit_of_work import UnitOfWork

class AbstractPermissionChecker:

    @abc.abstractmethod
    async def check(self, role_id: int, permissions: list[str]) -> bool:
        raise NotImplementedError

class PermissionChecker:

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def check(self, role_id: int, permissions: list[str]) -> bool:
        role = await self.uow.role_permission_repository.get_permissions_by_role_id(role_id)

        granted_permissions = {perm["name"] for perm in role["permissions"]}

        if not any(perm in granted_permissions for perm in permissions):
            return False
        
        return True