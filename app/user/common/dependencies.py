from fastapi import Depends
from common.unit_of_work import get_uow
from user.service_layer.services import UserService
from security import AuthHandler
from settings import settings
from common.permissions import PermissionChecker


def get_user_service(uow=Depends(get_uow)):
    auth_handler = AuthHandler(
        secret_key = settings.secret_key,
        algorithm= settings.jwt_algorithm
    )
    permission_checker = PermissionChecker(uow)
    return UserService(uow=uow, auth_handler=auth_handler, permission_checker=permission_checker)