from pydantic import BaseModel, ConfigDict



# Базовая модель пользователя
class UserBase(BaseModel):
    username: str
    email: str
    password: str


# Создание пользователя - все поля обязательны
class UserCreate(UserBase):
    pass


# Чтение пользователя - исключаем пароль и используем ORM режим
class UserRead(BaseModel):
    id: int
    username: str
    email: str
    model_config = ConfigDict(from_attributes=True)


# Обновление пользователя - все поля необязательны
class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None