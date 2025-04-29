
from typing import List, Optional, Dict
from . import models, schemas, exceptions

def get_task(db: Dict[int, models.Task], task_id: int) -> Optional[models.Task]:
    return db.get(task_id)

def get_tasks(db: Dict[int, models.Task], skip: int = 0, limit: int = 100) -> List[models.Task]:
    tasks = list(db.values())
    return tasks[skip : skip + limit]

def create_task(db: Dict[int, models.Task], task_data: schemas.TaskCreate, task_id: int) -> models.Task:
    if task_id in db:
         # This check prevents overwriting; real DB would handle PK constraints
         raise exceptions.DatabaseErrorException(f"Task with id {task_id} already exists.")

    db_task = models.Task(id=task_id, **task_data.model_dump())
    db[task_id] = db_task
    return db_task

def update_task(db: Dict[int, models.Task], task_id: int, task_update: schemas.TaskUpdate) -> Optional[models.Task]:
    db_task = db.get(task_id)
    if db_task is None:
        return None

    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)

    db[task_id] = db_task # Update the task in the 'database'
    return db_task


def delete_task(db: Dict[int, models.Task], task_id: int) -> Optional[models.Task]:
    if task_id in db:
        return db.pop(task_id)
    return None
