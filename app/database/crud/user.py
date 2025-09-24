from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import User
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
