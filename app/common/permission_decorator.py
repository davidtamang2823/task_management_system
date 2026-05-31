import functools
import typing
from fastapi import Request, status
from fastapi.exceptions import HTTPException

from unitofwork import UnitOfWork


def require_permission(permissions_name: typing.List[str]):
    def decorator(func: typing.Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            role_id: int = getattr(request.state, "role_id", None)
            uow: UnitOfWork = kwargs.get("uow")

            if role_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized.",
                )

            role = await uow.role_permission_repository.get_permissions_by_role_id(role_id)

            if role is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Role not found.",
                )

            granted_permissions = {perm["name"] for perm in role["permissions"]}

            if not any(perm in granted_permissions for perm in permissions_name):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission for this operation.",
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator