from task.domain.models import Task, TaskStatusSchema
from common.models import CommonBaseModel

class CreateTaskCommand(Task):
    ...

class UpdateTaskCommand(Task):
    id: int
    created_by_id: int | None = None

class DeleteTaskCommand(CommonBaseModel):
    id: int

class UpdateTaskStatus(TaskStatusSchema):
    id: int

class UpdateTaskAssignee(CommonBaseModel):
    id: int
    assigned_to_id: int