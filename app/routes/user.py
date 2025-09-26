from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import os
import smtplib
import ssl
from email.message import EmailMessage
import logging
from pathlib import Path
import datetime

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app.database.db import get_session
from app.database.models import User
from app.utils.templates import templates
from app.utils.security import get_password_hash, verify_password

router = APIRouter()

# Создаём сериалайзер с секретом из окружения
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
TOKEN_SALT = "password-reset-salt"
serializer = URLSafeTimedSerializer(SECRET_KEY)



# Показ страницы регистрации
@router.get("/auth/register.html")
async def register_get(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

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
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "Пароли не совпадают"}
        )
    # Проверка уникальности email и username (раздельно)
    result_email = await session.execute(select(User).where(User.email == email))
    result_username = await session.execute(select(User).where(User.username == username))
    existing_email = result_email.scalar_one_or_none()
    existing_username = result_username.scalar_one_or_none()
    if existing_email and existing_username:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "Пользователь с таким email и именем уже существует"}
        )
    elif existing_email:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "Пользователь с таким email уже существует"}
        )
    elif existing_username:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "Пользователь с таким именем уже существует"}
        )
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


@router.post("/logout")
async def logout_post(request: Request):
    redirect = RedirectResponse(url="/auth/login.html", status_code=303)
    redirect.delete_cookie("user_id")
    return redirect


# Запрос восстановления пароля - показ формы для ввода email
@router.get("/auth/recovery.html")
async def recovery_get(request: Request):
    return templates.TemplateResponse("auth/recovery.html", {"request": request})


# Отправка email для восстановления пароля
@router.post("/send_recovery_email")
async def send_recovery_email(
        request: Request,
        email: str = Form(...),
        session: AsyncSession = Depends(get_session)
):
    # Проверяем существование пользователя
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        return templates.TemplateResponse(
            "auth/recovery.html",
            {"request": request, "error": "Пользователь с таким email не найден"}
        )

    # Генерируем подписанный токен (внутри — email)
    token = serializer.dumps(email, salt=TOKEN_SALT)

    # Формируем ссылку для восстановления (используем base_url)
    base = str(request.base_url).rstrip('/')
    reset_url = f"{base}/auth/reset_password.html?token={token}&email={email}"

    # --- Добавлено: всегда сохраняем ссылку в файл логов для отладки/контейнера ---
    try:
        log_path = Path(os.getenv("RESET_LINK_LOG", "password_reset_links.log"))
        log_path_parent = log_path.parent
        if not log_path_parent.exists() and str(log_path_parent) != '.':
            log_path_parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.utcnow().isoformat()}Z\t{email}\t{reset_url}\n")
        resolved_log_path = str(log_path.resolve())
    except Exception:
        logging.exception("Failed to write reset link to file")
        resolved_log_path = None
    # --- /Добавлено ---

    # Настройки SMTP берутся из переменных окружения
    smtp_host = os.getenv("SMTP_HOST", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", 25))
    smtp_user = os.getenv("SMTP_USER")  # может быть None для localhost без auth
    smtp_password = os.getenv("SMTP_PASSWORD")
    email_from = os.getenv("EMAIL_FROM", smtp_user or f"noreply@{request.url.hostname or 'example.com'}")
    subject = "Восстановление пароля"
    text_body = f"Здравствуйте,\n\nЧтобы восстановить пароль, перейдите по ссылке:\n{reset_url}\n\nЕсли вы не запрашивали восстановление, просто проигнорируйте это письмо."
    html_body = f"""
    <html>
      <body>
        <p>Здравствуйте,</p>
        <p>Чтобы восстановить пароль, перейдите по ссылке ниже:</p>
        <p><a href="{reset_url}">Сменить пароль</a></p>
        <p>Если вы не запрашивали восстановление — проигнорируйте это сообщение.</p>
      </body>
    </html>
    """

    # Составляем сообщение
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = email
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    debug_show_link = os.getenv("DEBUG_EMAIL", "0").lower() in ("1", "true", "yes")
    send_error = None

    # Отправляем письмо по SMTP
    try:
        if smtp_port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
                if smtp_user and smtp_password:
                    server.login(smtp_user, smtp_password)
                server.send_message(msg)
        else:
            # Используем обычный SMTP + STARTTLS если доступен
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.ehlo()
                try:
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                    server.ehlo()
                except Exception:
                    # starttls может не поддерживаться на локальном smtp
                    pass
                if smtp_user and smtp_password:
                    server.login(smtp_user, smtp_password)
                server.send_message(msg)
    except Exception as e:
        # Логируем ошибку и запоминаем её для отображения/файлового fallback
        logging.exception("Failed to send recovery email")
        send_error = str(e)

    # Всегда логируем ссылку (полезно в контейнерах/CI)
    logging.info("Password reset link for %s: %s", email, reset_url)

    # Если отправка упала — записываем ссылку в файл и показываем её в шаблоне (fallback для локальной отладки)
    if send_error:
        try:
            log_path = Path(os.getenv("RESET_LINK_LOG", "password_reset_links.log"))
            with log_path.open("a", encoding="utf-8") as f:
                f.write(f"{email}\t{reset_url}\n")
        except Exception:
            logging.exception("Failed to write reset link to file")

    # После попытки отправки формируем контекст — теперь всегда передаём reset_log_path когда он есть
    context = {"request": request, "success": "Если ваш email зарегистрирован — ссылка для восстановления отправлена (проверьте почту или логи)."}
    if resolved_log_path:
        context["reset_log_path"] = resolved_log_path
    if debug_show_link or send_error:
        context["debug_link"] = reset_url
        if send_error:
            # Краткое уведомление об ошибке SMTP
            context["error"] = f"Не удалось отправить письмо через SMTP: {send_error}. Ссылка показана ниже."
        logging.info("Password reset link (shown to user): %s", reset_url)

    return templates.TemplateResponse("auth/recovery.html", context)


# Восстановление пароля - показ формы (должен открываться по ссылке из email с токеном)
@router.get("/auth/reset_password.html")
async def reset_password_get(request: Request, token: str = None, email: str = None):
    # Передаём token и email в шаблон, чтобы форма была предзаполнена
    return templates.TemplateResponse("auth/reset_password.html", {"request": request, "token": token, "email": email})


# Восстановление пароля - обработка формы
@router.post("/reset_password")
async def reset_password_post(
        request: Request,
        email: str = Form(...),
        new_password: str = Form(...),
        confirm_password: str = Form(...),
        token: str = Form(None),
        session: AsyncSession = Depends(get_session)
):
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "auth/reset_password.html",
            {"request": request, "error": "Пароли не совпадают", "token": token}
        )

    if not token:
        return templates.TemplateResponse(
            "auth/reset_password.html",
            {"request": request, "error": "Отсутствует токен восстановления", "token": None}
        )

    # Проверяем токен (таймаут 2 часа)
    try:
        token_email = serializer.loads(token, salt=TOKEN_SALT, max_age=60 * 60 * 2)
    except SignatureExpired:
        return templates.TemplateResponse(
            "auth/reset_password.html",
            {"request": request, "error": "Токен истёк. Повторите запрос восстановления.", "token": None}
        )
    except BadSignature:
        return templates.TemplateResponse(
            "auth/reset_password.html",
            {"request": request, "error": "Неверный токен восстановления.", "token": None}
        )

    # Сверяем email из токена с введённым email
    if token_email != email:
        return templates.TemplateResponse(
            "auth/reset_password.html",
            {"request": request, "error": "Email не соответствует токену восстановления.", "token": None}
        )

    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        return templates.TemplateResponse(
            "auth/reset_password.html",
            {"request": request, "error": "Пользователь с таким email не найден"}
        )

    # Обновляем пароль
    user.hashed_password = get_password_hash(new_password)
    session.add(user)
    await session.commit()

    return RedirectResponse(url="/auth/login.html", status_code=303)