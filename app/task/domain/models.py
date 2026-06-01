import datetime
from common.models import CommonBaseModel
from task.domain.enumns import TaskStatus

class TaskStatusSchema(CommonBaseModel):
    status: TaskStatus

class Task(CommonBaseModel):
    title: str
    description: str
    due_date: datetime.date
    status: TaskStatus | None = None
    assigned_to_id: int
    created_by_id: int

