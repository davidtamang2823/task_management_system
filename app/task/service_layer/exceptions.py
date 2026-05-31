class TaskAlreadyCompletedError(Exception):

    def __init__(self):
        super().__init__("Task is already completed. Cannot change its status.")

class TaskNotFoundError(Exception):

    def __init__(self):
        super().__init__("Task not found.")

class YouDoNotHavePermissionError(Exception):

    def __init__(self):
        super().__init__("You do not have permission.")