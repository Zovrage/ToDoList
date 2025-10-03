import os

from pydantic_settings import BaseSettings, SettingsConfigDict

from dotenv import load_dotenv


load_dotenv()
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')

# Конфигурация приложения
class Settings(BaseSettings):
    APP_NAME: str = "ToDoList"
    DEBUG: bool = True
    SMTP_SERVER: str = SMTP_SERVER
    SMTP_PORT: int = SMTP_PORT
    SMTP_USER: str = SMTP_USER
    SMTP_PASSWORD: str = SMTP_PASSWORD


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()