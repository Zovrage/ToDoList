import datetime
from datetime import UTC
import secrets

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.database.db import ASYNC_SESSION
from app.database.models import User, PasswordResetToken
from app.utils.security import get_password_hash


@pytest.mark.asyncio
async def test_register_page():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/auth/register.html")
        assert response.status_code == 200
        assert "register" in response.text.lower() or "регистрация" in response.text.lower()

@pytest.mark.asyncio
async def test_register_user_and_create_todo():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Регистрация пользователя через форму
        response = await ac.post("/users/create", data={
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpass123",
            "confirm_password": "testpass123"
        }, follow_redirects=False)
        # Проверяем успешную регистрацию или ошибку о существующем пользователе
        if response.status_code in (302, 303):
            # Получаем user_id из куки (если установлен)
            cookies = response.cookies
            user_id = cookies.get("user_id")
            # Создаём задачу через форму (если user_id есть)
            if user_id:
                response = await ac.post("/todos/create", data={
                    "title": "Test Task",
                    "description": "Test Description"
                }, cookies={"user_id": user_id}, follow_redirects=False)
                assert response.status_code in (302, 303)
                # Проверяем, что задача появилась на странице
                response = await ac.get("/todos/html", cookies={"user_id": user_id})
                assert response.status_code == 200
                assert "Test Task" in response.text
        else:
            # Если пользователь уже существует, ожидаем статус 200 и сообщение об ошибке
            assert response.status_code == 200
            assert "уже существует" in response.text or "уже используется" in response.text

@pytest.mark.asyncio
async def test_password_recovery_and_reset():
    email = "resetuser@example.com"
    username = "resetuser"
    # Создаём пользователя напрямую в базе, если его нет
    async with ASYNC_SESSION() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                first_name="Reset",
                last_name="User",
                username=username,
                email=email,
                hashed_password=get_password_hash("oldpassword")
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
    # Запрашиваем восстановление пароля
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/recovery.html", data={"email": email})
        assert response.status_code == 200
        # Сообщение может быть в HTML, ищем по подстроке
        assert ("сброса пароля отправлена" in response.text.lower())
    # Создаём токен вручную (эмулируем письмо)
    token = secrets.token_urlsafe(32)
    expires_at = datetime.datetime.now(UTC) + datetime.timedelta(hours=1)
    async with ASYNC_SESSION() as session:
        reset_token = PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at)
        session.add(reset_token)
        await session.commit()
    # Проверяем GET /auth/reset-password?token=...
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/auth/reset-password?token={token}")
        assert response.status_code == 200
        assert ("сброс пароля" in response.text.lower())
    # Проверяем POST /auth/reset-password (успех)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/reset-password", data={
            "token": token,
            "password": "newpassword",
            "confirm_password": "newpassword"
        })
        assert response.status_code == 200
        assert ("пароль успешно измен" in response.text.lower())
    # Проверяем POST /auth/reset-password (невалидный токен)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/reset-password", data={
            "token": "badtoken",
            "password": "newpassword",
            "confirm_password": "newpassword"
        })
        assert response.status_code == 200
        assert ("ссылка недействительна" in response.text.lower() or "истекла" in response.text.lower())
    # Проверяем POST /auth/reset-password (несовпадающие пароли)
    # Снова создаём токен
    token2 = secrets.token_urlsafe(32)
    expires_at2 = datetime.datetime.now(UTC) + datetime.timedelta(hours=1)
    async with ASYNC_SESSION() as session:
        reset_token2 = PasswordResetToken(user_id=user.id, token=token2, expires_at=expires_at2)
        session.add(reset_token2)
        await session.commit()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/reset-password", data={
            "token": token2,
            "password": "newpassword1",
            "confirm_password": "newpassword2"
        })
        assert response.status_code == 200
        assert ("пароли не совпадают" in response.text.lower())
