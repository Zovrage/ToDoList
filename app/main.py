import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse


from app.routes import router
from app.database.db import init_db
from app.core.config import Settings




app = FastAPI(title=Settings.APP_NAME)



# Подключаем роутеры API
app.include_router(router)

# Подключаем статические файлы (фронтенд)
app.mount("/static", StaticFiles(directory="app/static"), name="static")



# Корневая точка для отдачи HTML страницы
@app.get("/")
async def root():
    return RedirectResponse(url="/todos/html")


# Инициализация базы данных при старте приложения
@app.on_event("startup")
async def startup():
    await init_db()


if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8000)