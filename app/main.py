import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from .routes import todos_router
from .database.db import init_db




app = FastAPI(title="ToDo API")




# Подключаем роутеры API
app.include_router(todos_router)


static_dir = os.path.join(os.path.dirname(__file__), "static")
# Подключаем статические файлы (фронтенд)
app.mount("/static", StaticFiles(directory=static_dir), name="static")



# Настраиваем шаблоны Jinja2
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)


# Корневая точка для отдачи HTML страницы
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Инициализация базы данных при старте приложения
@app.on_event("startup")
async def startup():
    await init_db()

# Настройка точки входа
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)