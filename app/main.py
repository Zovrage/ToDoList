import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager


from app.routes import router
from app.database.db import init_db
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)



# Подключаем роутеры API
app.include_router(router)

# Подключаем статические файлы (фронтенд)
app.mount("/static", StaticFiles(directory="app/static"), name="static")



# Корневая точка для отдачи HTML страницы
@app.get("/")
async def root():
    return RedirectResponse(url="/todos/html")



if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8000)