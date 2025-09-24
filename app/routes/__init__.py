from fastapi import APIRouter

from app.routes.todo import router as todo_router
from app.routes.user import router as user_router
from app.routes.auth import router as auth_router


router = APIRouter()




router.include_router(todo_router, prefix='/todos', tags=['todos'])
router.include_router(user_router, prefix='/users', tags=['users'])
router.include_router(auth_router, prefix='/auth', tags=['auth'])
