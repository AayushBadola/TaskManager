
class TaskNotFoundException(Exception):
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with id {task_id} not found")

class DatabaseErrorException(Exception):
    def __init__(self, message: str = "A database error occurred"):
        self.message = message
        super().__init__(message)
