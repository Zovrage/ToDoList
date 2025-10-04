# Базовый образ Python
FROM python:3.12-slim

# Установка рабочей директории
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt ./

# Установка зависимостей
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY app ./app
COPY tests ./tests

# Открытие порта
EXPOSE 8000

# Возможность выбора команды запуска через аргумент
ENTRYPOINT ["/bin/sh", "-c"]
CMD ["uvicorn app.main:app --host 0.0.0.0 --port 8000"]