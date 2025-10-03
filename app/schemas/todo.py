from pydantic import BaseModel, ConfigDict


# Базовая модель задачи
class ToDoBase(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False


# Создание задачи - все поля обязательны, кроме description
class ToDoCreate(ToDoBase):
    pass


# Обновление задачи - все поля необязательны
class ToDoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


# Чтение задачи - включает id и использует ORM режим
class ToDoRead(ToDoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
