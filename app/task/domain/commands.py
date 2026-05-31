from task.domain.models import Task, TaskStatus

class CreateTaskCommand(Task):
    ...

class UpdateTaskCommand(Task):
    id: int

class DeleteTaskCommand(Task):
    id: int

class UpdateTaskStatus(TaskStatus):
    id: int