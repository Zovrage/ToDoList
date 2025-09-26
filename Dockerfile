# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY app ./app

# Копируем базу данных, если требуется (опционально)
COPY app/database/DataBase.db ./app/database/DataBase.db

# Открываем порт для приложения
EXPOSE 8000

# Запускаем FastAPI через uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

