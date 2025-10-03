from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Хэширует простой пароль
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Проверяет, соответствует ли простой пароль хэшированному
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
