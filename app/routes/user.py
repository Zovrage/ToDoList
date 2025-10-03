from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.database.models import User
from app.utils.templates import templates
from app.utils.security import get_password_hash, verify_password



router = APIRouter()



# Показ страницы регистрации
@router.get("/auth/register.html")
async def register_get(request: Request):
    return templates.TemplateResponse(request, "auth/register.html", {})

# Создание пользователя через форму
@router.post("/create")
async def register_post(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    # Проверка совпадения паролей
    if password != confirm_password:
        return templates.TemplateResponse(request, "auth/register.html", {"error": "Пароли не совпадают"})
    # Проверка уникальности email и username (раздельно)
    result_email = await session.execute(select(User).where(User.email == email))
    result_username = await session.execute(select(User).where(User.username == username))
    existing_email = result_email.scalar_one_or_none()
    existing_username = result_username.scalar_one_or_none()
    if existing_email and existing_username:
        return templates.TemplateResponse(request, "auth/register.html", {"error": "Пользователь с таким email и именем уже существует"})
    elif existing_email:
        return templates.TemplateResponse(request, "auth/register.html", {"error": "Email уже используется"})
    elif existing_username:
        return templates.TemplateResponse(request, "auth/register.html", {"error": "Имя пользователя уже используется"})
    # Хеширование пароля
    hashed_password = get_password_hash(password)

    # Создание пользователя
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return RedirectResponse(url="/auth/login.html", status_code=303)


# Показ страницы логина
@router.get("/auth/login.html")
async def login_get(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})



# Логин пользователя через форму
@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember: str = Form(None),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Неверное имя пользователя или пароль"}
        )
    redirect = RedirectResponse(url="/todos/html", status_code=303)
    if remember:
        redirect.set_cookie("user_id", str(user.id), httponly=True, max_age=60*60*24*30)  # 30 дней
    else:
        redirect.set_cookie("user_id", str(user.id), httponly=True)
    return redirect

# Логаут пользователя
@router.post("/logout")
async def logout_post(request: Request):
    redirect = RedirectResponse(url="/auth/login.html", status_code=303)
    redirect.delete_cookie("user_id")
    return redirect
