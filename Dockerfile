# Используем официальный образ Python
FROM python:3.12-slim

# Не создаём pyc и включаем немедленный вывод
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Рабочая директория
WORKDIR /app

# Копируем зависимости отдельно, чтобы использовать кэш слоёв
COPY requirements.txt ./

# Устанавливаем системные зависимости для сборки Python-зависимостей, затем удаляем их
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Создаём непривилегованного пользователя и задаём права
RUN useradd --create-home --shell /bin/false appuser \
    && mkdir -p /app

# Копируем исходный код и базу данных, сразу задаём владельца
COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser app/database/DataBase.db ./app/database/DataBase.db

# Переключаемся на непривилегованного пользователя
USER appuser

# Открываем порт для приложения
EXPOSE 8000

# Запускаем FastAPI через uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]