from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import ToDo
from app.schemas.todo import ToDoCreate, ToDoUpdate, ToDoRead





# CRUD операции для модели ToDo
async def get_all_todos(db: AsyncSession) -> list[ToDoRead]:
    result = await db.execute(select(ToDo))
    todos = result.scalars().all()
    return [ToDoRead.from_orm(todo) for todo in todos]

# Создание новой задачи
async def create_todo(db: AsyncSession, todo: ToDoCreate) -> ToDoRead:
    new_todo = ToDo(**todo.dict())
    db.add(new_todo)
    await db.commit()
    await db.refresh(new_todo)
    return ToDoRead.from_orm(new_todo)

# Обновление задачи
async def update_todo(db: AsyncSession, todo_id: int, todo: ToDoUpdate) -> ToDoRead | None:
    result = await db.execute(select(ToDo).where(ToDo.id == todo_id))
    existing_todo = result.scalar_one_or_none()
    if not existing_todo:
        return None
    for key, value in todo.dict(exclude_unset=True).items():
        setattr(existing_todo, key, value)
    await db.commit()
    await db.refresh(existing_todo)
    return ToDoRead.from_orm(existing_todo)

# Удаление задачи
async def delete_todo(db: AsyncSession, todo_id: int) -> bool:
    result = await db.execute(select(ToDo).where(ToDo.id == todo_id))
    existing_todo = result.scalar_one_or_none()
    if not existing_todo:
        return False
    await db.delete(existing_todo)
    await db.commit()
    return True







