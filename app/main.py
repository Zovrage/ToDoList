from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from app.routes import todos_router
from app.database.db import init_db




app = FastAPI(title="ToDo API")




# Подключаем роутеры API
app.include_router(todos_router)


# Подключаем статические файлы (фронтенд)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Настраиваем шаблоны Jinja2
templates = Jinja2Templates(directory="app/templates")


# Корневая точка для отдачи HTML страницы
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Инициализация базы данных при старте приложения
@app.on_event("startup")
async def startup():
    await init_db()

