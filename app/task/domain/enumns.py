from enum import Enum
from task.common import constants as task_constants


class TaskStatus(str, Enum):
    PENDING = task_constants.STR_PENDING
    IN_PROGRESS = task_constants.STR_IN_PROGRESS
    COMPLETED = task_constants.STR_COMPLETED

    @property
    def int_value(self):
        return task_constants.TASK_STATUS_STR_TO_INT[self.value]