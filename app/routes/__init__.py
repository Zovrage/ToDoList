from fastapi import APIRouter

from app.routes.todos import router as todos_router



router = APIRouter()




router.include_router(todos_router, prefix='/todos', tags=['todos'])
