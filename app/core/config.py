from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "ToDoList"
    DEBUG: bool = True
    # позже добавим DATABASE_URL, SELECT_KEY, JWT_* и т.п.

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()