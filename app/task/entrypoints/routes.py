from fastapi import APIRouter, Request, Depends, status, HTTPException

from common.unit_of_work import UnitOfWork, get_uow
from task.domain.commands import (
    CreateTaskCommand,
    UpdateTaskCommand,
    UpdateTaskStatus,
    DeleteTaskCommand,
    UpdateTaskAssignee
)
from task.service_layer.services import TaskService
from task.service_layer.exceptions import (
    TaskNotFoundError,
    TaskAlreadyCompletedError,
    YouDoNotHavePermissionError,
)
from task.common.dependencies import get_task_service

task_router = APIRouter(prefix="/tasks", tags=["Tasks"])


@task_router.get("/")
async def list_tasks(
    request: Request,
    task_service: TaskService = Depends(get_task_service),
):
    tasks = await task_service.list_tasks(
        filters={},
        current_user_id=request.state.user_id,
        current_user_role_id=request.state.role_id,
    )
    return tasks


@task_router.get("/{task_id}")
async def get_task(
    task_id: int,
    request: Request,
    task_service: TaskService = Depends(get_task_service),
):
    try:
        return await task_service.get_task(
            task_id=task_id,
            current_user_id=request.state.user_id,
            current_user_role_id=request.state.role_id,
        )
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except YouDoNotHavePermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@task_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(
    request: Request,
    task_service: TaskService = Depends(get_task_service),
):
    try:
        body = await request.json()
        task_data = CreateTaskCommand(**body, created_by_id=request.state.user_id)
        return await task_service.create_task(
            task_data=task_data,
            current_user_id=request.state.user_id,
            current_user_role_id=request.state.role_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except YouDoNotHavePermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@task_router.put("/{task_id}")
async def update_task(
    task_id: int,
    request: Request,
    task_service: TaskService = Depends(get_task_service),
):
    try:
        body = await request.json()
        task_data = UpdateTaskCommand(**body, id=task_id)
        return await task_service.update_task(
            task_data=task_data,
            current_user_id=request.state.user_id,
            current_user_role_id=request.state.role_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except TaskAlreadyCompletedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except YouDoNotHavePermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@task_router.patch("/{task_id}/status")
async def update_task_status(
    task_id: int,
    request: Request,
    task_service: TaskService = Depends(get_task_service),
):
    try:
        body = await request.json()
        task_data = UpdateTaskStatus(**body, id=task_id)
        await task_service.update_task_status(
            task_data=task_data,
            current_user_id=request.state.user_id,
            current_user_role_id=request.state.role_id,
        )
        return {"detail": "Task status updated successfully."}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except YouDoNotHavePermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@task_router.patch("/{task_id}/assign")
async def update_assigned_user(
    task_id: int,
    request: Request,
    task_service: TaskService = Depends(get_task_service),
):
    try:
        body = await request.json()
        task_data = UpdateTaskAssignee(id=task_id, **body)
        return await task_service.update_assigned_user(
            task_data=task_data,
            current_user_id=request.state.user_id,
            current_user_role_id=request.state.role_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except YouDoNotHavePermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

@task_router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    task_id: int,
    request: Request,
    task_service: TaskService = Depends(get_task_service),
):
    try:
        await task_service.delete_task(
            task_data=DeleteTaskCommand(id=task_id),
            current_user_id=request.state.user_id,
            current_user_role_id=request.state.role_id,
        )
        return {"detail": "Task deleted successfully."}
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except YouDoNotHavePermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )