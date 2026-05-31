from fastapi import Depends
from common.unit_of_work import UnitOfWork, get_uow
from task.service_layer.services import TaskService
from common.permissions import PermissionChecker

def get_task_service(uow: UnitOfWork = Depends(get_uow)):

    return TaskService(
        uow=uow,
        permission_checker=PermissionChecker(uow=uow)
    )
