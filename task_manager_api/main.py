from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from typing import List, Dict
from . import crud, models, schemas, exceptions, database

app = FastAPI(title="Task Manager API", version="0.1.0")

DbDependency = Depends(database.get_db)

@app.exception_handler(exceptions.TaskNotFoundException)
async def task_not_found_exception_handler(request: Request, exc: exceptions.TaskNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": str(exc)},
    )

@app.exception_handler(exceptions.DatabaseErrorException)
async def database_error_exception_handler(request: Request, exc: exceptions.DatabaseErrorException):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": str(exc)},
    )

@app.post("/tasks/", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Dict[int, models.Task] = DbDependency) -> models.Task:
    next_id = database.get_next_id()
    try:
        created_task = crud.create_task(db=db, task_data=task, task_id=next_id)
        return created_task
    except exceptions.DatabaseErrorException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@app.get("/tasks/", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Dict[int, models.Task] = DbDependency) -> List[models.Task]:
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks

@app.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Dict[int, models.Task] = DbDependency) -> models.Task:
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise exceptions.TaskNotFoundException(task_id=task_id)
    return db_task

@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Dict[int, models.Task] = DbDependency) -> models.Task:
    updated_task = crud.update_task(db=db, task_id=task_id, task_update=task_update)
    if updated_task is None:
        raise exceptions.TaskNotFoundException(task_id=task_id)
    return updated_task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Dict[int, models.Task] = DbDependency) -> None:
    deleted_task = crud.delete_task(db=db, task_id=task_id)
    if deleted_task is None:
        raise exceptions.TaskNotFoundException(task_id=task_id)
    return None

@app.get("/")
async def root():
    return {"message": "Welcome to the Task Manager API"}

