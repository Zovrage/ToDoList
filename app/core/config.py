from pydantic_settings import BaseSettings, SettingsConfigDict

# Конфигурация приложения
class Settings(BaseSettings):
    APP_NAME: str = "ToDoList"
    DEBUG: bool = True
    BOT_TOKEN: str = "dummy"
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = "maydzi01@gmail.com"
    SMTP_PASSWORD: str = "vdwj tbut ohcl tvat"
    # позже добавим DATABASE_URL, SELECT_KEY, JWT_* и т.п.

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()