from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.models import ToDo
from app.schemas.todo import ToDoCreate, ToDoUpdate, ToDoRead



router = APIRouter()




# Получение всех задач
@router.get("/todos/", response_model=list[ToDoRead])
async def read_todos(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ToDo))
    todos = result.scalars().all()
    return [ToDoRead.from_orm(todo) for todo in todos]


# Создание новой задачи
@router.post("/todos/", response_model=ToDoRead)
async def create_todo(todo: ToDoCreate, session: AsyncSession = Depends(get_session)):
    new_todo = ToDo(**todo.dict())
    session.add(new_todo)  # ⚡ не await
    await session.commit()
    await session.refresh(new_todo)
    return ToDoRead.from_orm(new_todo)


# Обновление задачи
@router.put("/todos/{todo_id}", response_model=ToDoRead)
async def update_todo(todo_id: int, todo: ToDoUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ToDo).where(ToDo.id == todo_id))
    existing_todo = result.scalar_one_or_none()
    if not existing_todo:
        raise HTTPException(status_code=404, detail="ToDo not found")

    for key, value in todo.dict(exclude_unset=True).items():
        setattr(existing_todo, key, value)

    session.add(existing_todo)
    await session.commit()
    await session.refresh(existing_todo)
    return ToDoRead.from_orm(existing_todo)


# Удаление задачи
@router.delete("/todos/{todo_id}", response_model=dict)
async def delete_todo(todo_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ToDo).where(ToDo.id == todo_id))
    existing_todo = result.scalar_one_or_none()
    if not existing_todo:
        raise HTTPException(status_code=404, detail="ToDo not found")

    await session.delete(existing_todo)
    await session.commit()
    return {"detail": "ToDo deleted"}
