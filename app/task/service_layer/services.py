import abc
from task.domain.commands import (
    CreateTaskCommand,
    UpdateTaskCommand,
    UpdateTaskStatus,
    DeleteTaskCommand,
    UpdateTaskAssignee
)
from common.unit_of_work import UnitOfWork
from task.common.constants import STR_COMPLETED
from task.service_layer.exceptions import (
    TaskAlreadyCompletedError,
    TaskNotFoundError,
    YouDoNotHavePermissionError,
)
from common.permissions import AbstractPermissionChecker
from common import constants as common_constants


class AbstractTaskService(abc.ABC):

    @abc.abstractmethod
    async def get_task(self, task_id: int, current_user_id: int, current_user_role_id: int):
        raise NotImplementedError

    @abc.abstractmethod
    async def list_tasks(self, filters: dict, current_user_id: int, current_user_role_id: int):
        raise NotImplementedError

    @abc.abstractmethod
    async def create_task(self, task_data: CreateTaskCommand, current_user_id: int, current_user_role_id: int):
        raise NotImplementedError

    @abc.abstractmethod
    async def update_task(self, task_data: UpdateTaskCommand, current_user_id: int, current_user_role_id: int):
        raise NotImplementedError

    @abc.abstractmethod
    async def update_task_status(self, task_data: UpdateTaskStatus, current_user_id: int, current_user_role_id: int):
        raise NotImplementedError

    @abc.abstractmethod
    async def update_assigned_user(self, task_data: UpdateTaskAssignee, current_user_id: int, current_user_role_id: int) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_task(self, task_data: DeleteTaskCommand, current_user_id: int, current_user_role_id: int):
        raise NotImplementedError


class TaskService(AbstractTaskService):

    def __init__(self, uow: UnitOfWork, permission_checker: AbstractPermissionChecker):
        self.uow = uow
        self.permission_checker = permission_checker

    async def get_task(self, task_id: int, current_user_id: int, current_user_role_id: int) -> dict:
        task = await self.uow.task_repository.get_task_by_id(task_id)

        if task is None:
            raise TaskNotFoundError()

        has_permission = await self.permission_checker.check(
            current_user_role_id,
            [common_constants.PERMISSION_VIEW_ALL_TASKS],
        )

        is_created_by_or_assigned_to = (
            task["created_by"]["id"] == current_user_id
            or task["assigned_to"]["id"] == current_user_id
        )

        if not has_permission and not is_created_by_or_assigned_to:
            raise YouDoNotHavePermissionError()

        return task

    async def list_tasks(self, filters: dict, current_user_id: int, current_user_role_id: int) -> list[dict]:
        has_permission = await self.permission_checker.check(
            current_user_role_id,
            [common_constants.PERMISSION_VIEW_ALL_TASKS],
        )
        if not has_permission:
            filters["user_id"] = current_user_id

        return await self.uow.task_repository.get_tasks(filters)

    async def create_task(self, task_data: CreateTaskCommand, current_user_id: int, current_user_role_id: int) -> dict:
        has_permission = await self.permission_checker.check(
            current_user_role_id,
            [common_constants.PERMISSION_CREATE_TASKS],
        )

        if not has_permission:
            raise YouDoNotHavePermissionError()

        return await self.uow.task_repository.add(task_data)

    async def update_task(self, task_data: UpdateTaskCommand, current_user_id: int, current_user_role_id: int) -> dict:
        existing_task = await self.uow.task_repository.get_task_by_id(task_data.id)

        if existing_task is None:
            raise TaskNotFoundError()

        has_permission = await self.permission_checker.check(
            current_user_role_id,
            [
                common_constants.PERMISSION_UPDATE_ANY_TASK,
                common_constants.PERMISSION_UPDATE_TASK,
            ],
        )

        if not has_permission:
            raise YouDoNotHavePermissionError()

        if existing_task.get("status") == STR_COMPLETED and task_data.status.value != STR_COMPLETED:
            raise TaskAlreadyCompletedError()

        return await self.uow.task_repository.update(task_data)

    async def update_task_status(self, task_data: UpdateTaskStatus, current_user_id: int, current_user_role_id: int) -> None:
        task = await self.uow.task_repository.get_task_by_id(task_data.id)

        if task is None:
            raise TaskNotFoundError()

        has_permission = await self.permission_checker.check(
            current_user_role_id,
            [common_constants.PERMISSION_UPDATE_TASK_STATUS],
        )

        is_created_by_or_assigned_to = (
            task["created_by"]["id"] == current_user_id
            or task["assigned_to"]["id"] == current_user_id
        )

        if not has_permission:
            raise YouDoNotHavePermissionError()
        elif not is_created_by_or_assigned_to:
            raise YouDoNotHavePermissionError()

        if task.get("status") == STR_COMPLETED and task_data.status.value != STR_COMPLETED:
            raise TaskAlreadyCompletedError()

        await self.uow.task_repository.update_task_status(
            task_id=task_data.id,
            status=task_data.status.int_value,
        )

    async def update_assigned_user(self, task_data: UpdateTaskAssignee, current_user_id: int, current_user_role_id: int) -> dict:
        task = await self.uow.task_repository.get_task_by_id(task_data.id)

        if task is None:
            raise TaskNotFoundError()

        has_permission = await self.permission_checker.check(
            current_user_role_id,
            [
                common_constants.PERMISSION_ASSIGN_TASK_TO_ANY_USER,
                common_constants.PERMISSION_ASSIGN_TASK_TO_USER
            ]
        )

        if not has_permission:
            raise YouDoNotHavePermissionError()

        updated_task = await self.uow.task_repository.update_assigned_user(
            task_id=task_data.id,
            assigned_to_id=task_data.assigned_to_id,
        )

        return updated_task


    async def delete_task(self, task_data: DeleteTaskCommand, current_user_id: int, current_user_role_id: int) -> None:
        task = await self.uow.task_repository.get_task_by_id(task_data.id)

        if task is None:
            raise TaskNotFoundError()

        has_permission = await self.permission_checker.check(
            current_user_role_id,
            [common_constants.PERMISSION_DELETE_ANY_TASK],
        )

        is_task_creator = task["created_by"]["id"] == current_user_id

        if not has_permission and not is_task_creator:
            raise YouDoNotHavePermissionError()

        await self.uow.task_repository.delete_task(task_data.id)