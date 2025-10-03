import datetime
from datetime import UTC
import secrets

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.utils.templates import templates
from app.database.db import get_session
from app.database.models import User
from app.utils.security import get_password_hash
from app.utils.email import send_email
from app.core.config import settings
from app.database.crud.user import create_password_reset_token, get_password_reset_token, delete_password_reset_token


router = APIRouter()


@router.get("/login.html", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "auth/login.html", {})


@router.get("/register.html", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request, "auth/register.html", {})


@router.get("/recovery.html", response_class=HTMLResponse)
async def recovery_page(request: Request):
    return templates.TemplateResponse(request, "auth/recovery.html", {})


@router.post("/recovery.html", response_class=HTMLResponse)
async def recovery_post(
    request: Request,
    email: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return templates.TemplateResponse(
            request,
            "auth/recovery.html",
            {"error": "Пользователь с таким email не найден"},
        )
    # Генерируем токен и сохраняем его
    token = secrets.token_urlsafe(32)
    expires_at = datetime.datetime.now(UTC) + datetime.timedelta(hours=1)
    await create_password_reset_token(session, user.id, token, expires_at)
    # Формируем ссылку для сброса пароля динамически
    base_url = str(request.base_url).rstrip('/')
    reset_link = f"{base_url}/auth/reset-password?token={token}"
    # Отправляем ссылку на email
    try:
        send_email(
            to_email=email,
            subject="Восстановление пароля ToDoList",
            body=f"Для сброса пароля перейдите по ссылке: {reset_link}",
            smtp_server=settings.SMTP_SERVER,
            smtp_port=settings.SMTP_PORT,
            smtp_user=settings.SMTP_USER,
            smtp_password=settings.SMTP_PASSWORD,
        )
        return templates.TemplateResponse(
            request, "auth/recovery.html", {"success": "Ссылка для сброса пароля отправлена на ваш email."}
        )
    except Exception as e:
        return templates.TemplateResponse(
            request, "auth/recovery.html", {"error": f"Ошибка отправки email: {e}"}
        )


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_get(request: Request, token: str, session: AsyncSession = Depends(get_session)):
    reset_token = await get_password_reset_token(session, token)
    now = datetime.datetime.now(UTC)
    if not reset_token or to_utc_aware(reset_token.expires_at) < now:
        return templates.TemplateResponse(request, "auth/reset_password.html", {"error": "Ссылка недействительна или истекла."})
    return templates.TemplateResponse(request, "auth/reset_password.html", {"token": token})


@router.post("/reset-password", response_class=HTMLResponse)
async def reset_password_post(
    request: Request,
    token: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    reset_token = await get_password_reset_token(session, token)
    now = datetime.datetime.now(UTC)
    if not reset_token or to_utc_aware(reset_token.expires_at) < now:
        return templates.TemplateResponse(request, "auth/reset_password.html", {"error": "Ссылка недействительна или истекла."})
    if password != confirm_password:
        return templates.TemplateResponse(request, "auth/reset_password.html", {"error": "Пароли не совпадают.", "token": token})
    # Обновляем пароль пользователя
    result = await session.execute(select(User).where(User.id == reset_token.user_id))
    user = result.scalar_one_or_none()
    if not user:
        return templates.TemplateResponse(request, "auth/reset_password.html", {"error": "Пользователь не найден."})
    user.hashed_password = get_password_hash(password)
    session.add(user)
    await delete_password_reset_token(session, token)
    await session.commit()
    return templates.TemplateResponse(request, "auth/reset_password.html", {"success": "Пароль успешно изменён. Теперь вы можете войти."})


def to_utc_aware(dt):
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt
