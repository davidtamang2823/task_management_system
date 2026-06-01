import abc
import typing
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from task.domain import models as task_domain_model
from task.adapters.orm import Task
from task.common import constants as task_constants


class AbstractTaskRepository(abc.ABC):

    @abc.abstractmethod
    async def get_task_by_id(self, task_id: int) -> dict | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_tasks(self, filters: typing.Dict) -> list[dict]:
        raise NotImplementedError

    @abc.abstractmethod
    async def add(self, task: task_domain_model.Task) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, task: task_domain_model.Task) -> dict | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def update_task_status(self, task_id: int, status: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def update_assigned_user(self, task_id: int, assigned_to_id: int) -> dict | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_task(self, task_id: int) -> None:
        raise NotImplementedError


class TaskRepository(AbstractTaskRepository):

    def __init__(self, session: AsyncSession):
        self.session = session


    def _to_orm(self, task_orm_obj: task_domain_model.Task) -> Task:
        return Task(
            title=task_orm_obj.title,
            description=task_orm_obj.description,
            due_date=task_orm_obj.due_date,
            status=task_orm_obj.status.int_value if task_orm_obj.status else task_constants.INT_PENDING,
            assigned_to_id=task_orm_obj.assigned_to_id,
            created_by_id=task_orm_obj.created_by_id,
        )

    def _to_dict(self, task_orm_obj: Task) -> dict:
        return {
            "id": task_orm_obj.id,
            "title": task_orm_obj.title,
            "description": task_orm_obj.description,
            "due_date": task_orm_obj.due_date,
            "status": task_constants.TASK_STATUS_INT_TO_STR.get(task_orm_obj.status),
            "assigned_to": {
                "id": task_orm_obj.assigned_to.id,
                "first_name": task_orm_obj.assigned_to.first_name,
                "last_name": task_orm_obj.assigned_to.last_name,
                "email": task_orm_obj.assigned_to.email,
            } if task_orm_obj.assigned_to else None,
            "created_by": {
                "id": task_orm_obj.created_by.id,
                "first_name": task_orm_obj.created_by.first_name,
                "last_name": task_orm_obj.created_by.last_name,
                "email": task_orm_obj.created_by.email,
            } if task_orm_obj.created_by else None,
        }


    async def get_task_by_id(self, task_id: int) -> dict | None:
        stmt = (
            select(Task)
            .where(Task.id == task_id)
            .options(
                selectinload(Task.assigned_to),
                selectinload(Task.created_by),
            )
        )
        result = await self.session.execute(stmt)
        task = result.scalar_one_or_none()

        if task is None:
            return None

        return self._to_dict(task)

    async def get_tasks(self, filters: typing.Dict) -> list[dict]:
        stmt = (
            select(Task)
            .options(
                selectinload(Task.assigned_to),
                selectinload(Task.created_by),
            )
        )

        if status := filters.get("status"):
            stmt = stmt.where(Task.status == status)

        if user_id := filters.get("user_id"):
            stmt = stmt.where(
                (Task.assigned_to_id == user_id) | (Task.created_by_id == user_id)
            )

        if due_date := filters.get("due_date"):
            stmt = stmt.where(Task.due_date == due_date)

        if due_date_from := filters.get("due_date_from"):
            stmt = stmt.where(Task.due_date >= due_date_from)

        if due_date_to := filters.get("due_date_to"):
            stmt = stmt.where(Task.due_date <= due_date_to)

        result = await self.session.execute(stmt)
        tasks = result.scalars().all()

        return [self._to_dict(task) for task in tasks]


    async def add(self, task: task_domain_model.Task) -> dict:
        task_orm_obj = self._to_orm(task)
        self.session.add(task_orm_obj)
        await self.session.flush()
        await self.session.refresh(task_orm_obj, attribute_names=["assigned_to", "created_by"])
        return self._to_dict(task_orm_obj)

    async def update(self, task: task_domain_model.Task) -> dict | None:
        stmt = (
            select(Task)
            .where(Task.id == task.id)
            .options(
                selectinload(Task.assigned_to),
                selectinload(Task.created_by),
            )
        )
        result = await self.session.execute(stmt)
        task_orm_obj = result.scalar_one_or_none()

        if task_orm_obj is None:
            return None

        task_orm_obj.title = task.title
        task_orm_obj.description = task.description
        task_orm_obj.due_date = task.due_date
        task_orm_obj.status = task.status.int_value if task.status else task_constants.INT_PENDING
        task_orm_obj.assigned_to_id = task.assigned_to_id

        await self.session.flush()
        await self.session.refresh(task_orm_obj, attribute_names=["assigned_to", "created_by"])
        return self._to_dict(task_orm_obj)

    async def update_task_status(self, task_id: int, status: int) -> None:
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(status=status)
        )
        await self.session.execute(stmt)

    async def update_assigned_user(self, task_id: int, assigned_to_id: int) -> dict | None:
        stmt = (
            select(Task)
            .where(Task.id == task_id)
            .options(
                selectinload(Task.assigned_to),
                selectinload(Task.created_by),
            )
        )
        result = await self.session.execute(stmt)
        task_orm_obj = result.scalar_one_or_none()

        if task_orm_obj is None:
            return None

        task_orm_obj.assigned_to_id = assigned_to_id

        await self.session.flush()
        await self.session.refresh(task_orm_obj, attribute_names=["assigned_to", "created_by"])
        return self._to_dict(task_orm_obj)


    async def delete_task(self, task_id: int) -> None:
        stmt = delete(Task).where(Task.id == task_id)
        await self.session.execute(stmt)