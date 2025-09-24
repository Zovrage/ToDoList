from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.models import ToDo, User
from app.utils.templates import templates

router = APIRouter()

# Показ всех задач
@router.get("/html")
async def todos_html(request: Request, session: AsyncSession = Depends(get_session)):
    user_id = request.cookies.get("user_id")
    user = None
    todos = []
    if user_id:
        user = await session.get(User, int(user_id))
        if user:
            result = await session.execute(select(ToDo).where(ToDo.user_id == user.id))
            todos = result.scalars().all()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": user, "todos": todos}
    )

# Создание задачи через форму
@router.post("/create")
async def create_todo_html(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    session: AsyncSession = Depends(get_session)
):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/auth/login.html", status_code=303)
    new_todo = ToDo(title=title, description=description, user_id=int(user_id))
    session.add(new_todo)
    await session.commit()
    return RedirectResponse(url="/todos/html", status_code=303)

# Обновление задачи через форму
@router.post("/update/{todo_id}")
async def update_todo_html(
    todo_id: int,
    title: str = Form(...),
    description: str = Form(""),
    completed: str = Form(None),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(ToDo).where(ToDo.id == todo_id))
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=404, detail="ToDo not found")
    todo.title = title
    todo.description = description
    todo.completed = completed == "true"
    session.add(todo)
    await session.commit()
    return RedirectResponse(url="/todos/html", status_code=303)

# Удаление задачи через форму
@router.post("/delete/{todo_id}")
async def delete_todo_html(
    todo_id: int,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(ToDo).where(ToDo.id == todo_id))
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=404, detail="ToDo not found")
    await session.delete(todo)
    await session.commit()
    return RedirectResponse(url="/todos/html", status_code=303)
