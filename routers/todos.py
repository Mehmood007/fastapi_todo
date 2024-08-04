from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Todos

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, le=5)
    complete: bool


@router.get('/todos', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@router.post('/todos', status_code=status.HTTP_201_CREATED)
async def add_new(db: db_dependency, todo_request: TodoRequest):
    todo_model = Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()


@router.get('/todo/{todo_id}', status_code=status.HTTP_200_OK)
async def read_by_id(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model:
        return todo_model

    raise HTTPException(status_code=404, detail='No todo found')


@router.put('/todo/{todo_id}', status_code=status.HTTP_200_OK)
async def update_todo(
    db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)
):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if not todo_model:
        raise HTTPException(status_code=404, detail='No todo found')

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()

    return {'message': f'Todo {todo_model.id} updated successfully'}


@router.delete('/todo/{todo_id}', status_code=status.HTTP_200_OK)
async def delete_by_id(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if not todo_model:
        raise HTTPException(status_code=404, detail='No todo found')

    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()

    return {'message': f'Todo {todo_model.id} deleted successfully'}
