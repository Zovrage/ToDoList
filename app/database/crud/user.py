from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import datetime

from app.database.models import User, PasswordResetToken
from app.schemas.user import UserRead, UserCreate, UserUpdate





# CRUD операции для модели User
async def get_all_users(db: AsyncSession) -> list[UserRead]:
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [UserRead.from_orm(user) for user in users]

# Создание нового пользователя
async def create_user(db: AsyncSession, user: UserCreate) -> UserRead:
    new_user = User(**user.dict())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return UserRead.from_orm(new_user)


# Получение пользователя по ID
async def get_user_by_id(db: AsyncSession, user_id: int) -> UserRead | None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None
    return UserRead.from_orm(user)

# Удаление пользователя
async def delete_user(db: AsyncSession, user_id: int) -> bool:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return False
    await db.delete(user)
    await db.commit()
    return True

# Обновление пользователя
async def update_user(db: AsyncSession, user_id: int, user: UserUpdate) -> UserRead | None:
    result = await db.execute(select(User).where(User.id == user_id))
    existing_user = result.scalar_one_or_none()
    if not existing_user:
        return None
    for key, value in user.dict(exclude_unset=True).items():
        setattr(existing_user, key, value)
    await db.commit()
    await db.refresh(existing_user)
    return UserRead.from_orm(existing_user)

# --- Password Reset Token CRUD ---
async def create_password_reset_token(db: AsyncSession, user_id: int, token: str, expires_at: datetime.datetime) -> PasswordResetToken:
    reset_token = PasswordResetToken(user_id=user_id, token=token, expires_at=expires_at)
    db.add(reset_token)
    await db.commit()
    await db.refresh(reset_token)
    return reset_token

async def get_password_reset_token(db: AsyncSession, token: str) -> PasswordResetToken | None:
    result = await db.execute(select(PasswordResetToken).where(PasswordResetToken.token == token))
    return result.scalar_one_or_none()

async def delete_password_reset_token(db: AsyncSession, token: str) -> None:
    result = await db.execute(select(PasswordResetToken).where(PasswordResetToken.token == token))
    reset_token = result.scalar_one_or_none()
    if reset_token:
        await db.delete(reset_token)
        await db.commit()
