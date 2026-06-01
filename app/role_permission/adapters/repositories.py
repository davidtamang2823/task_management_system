import abc
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from role_permission.adapters import orm as role_perm_orm

class AbstractRolePermissionRepository(abc.ABC):

    @abc.abstractmethod
    async def get_role_by_name(self, role_name: str):
        raise NotImplementedError

    @abc.abstractmethod
    async def get_permissions_by_role_id(self, role_id: int) -> dict | None:
        raise NotImplementedError


class RolePermissionRepository(AbstractRolePermissionRepository):


    def __init__(self, session):
        self.session = session

    async def get_role_by_name(self, role_name: str):
        stmt = (
            select(role_perm_orm.Role)
            .where(role_perm_orm.Role.name == role_name)
        )
        result = await self.session.execute(stmt)
        role = result.scalar_one_or_none()

        if role is None:
            return None

        return self._role_to_dict(role)


    async def get_permissions_by_role_id(self, role_id: int) -> dict | None:
        stmt = (
            select(role_perm_orm.Role)
            .where(role_perm_orm.Role.id == role_id)
            .options(selectinload(role_perm_orm.Role.permissions))
        )
        result = await self.session.execute(stmt)
        role = result.scalar_one_or_none()

        if role is None:
            return None

        return self._role_to_dict_with_permissions(role)


    def _role_to_dict(self, role: role_perm_orm.Role):
        return {
            "id": role.id,
            "name": role.name
        }
    
    def _permission_to_dict(self, permission: role_perm_orm.Permission) -> dict:
        return {
            "id": permission.id,
            "name": permission.name,
            "display_name": permission.display_name,
        }

    def _role_to_dict_with_permissions(self, role: role_perm_orm.Role) -> dict:
        return {
            "id": role.id,
            "name": role.name,
            "permissions": [
                self._permission_to_dict(permission)
                for permission in role.permissions
            ],
        }