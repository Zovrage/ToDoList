# ToDoList

Современное веб-приложение для управления задачами (ToDo) на FastAPI с поддержкой регистрации, аутентификации, восстановления пароля через email, асинхронной работы с базой данных и красивым интерфейсом.

---

## 🚀 Возможности
- Регистрация и вход пользователей
- Восстановление пароля с отправкой ссылки на email
- Создание, просмотр, редактирование и удаление задач
- Адаптивный и современный дизайн (CSS)
- Асинхронная работа с базой данных (SQLAlchemy)
- Тесты для основных функций

---

## 🛠️ Технологии
- **Python 3.13**
- **FastAPI**
- **SQLAlchemy (async)**
- **Jinja2** (шаблоны)
- **HTTPX** (тесты)
- **pytest**
- **Pydantic**
- **Docker** (опционально)

---

## 📦 Установка и запуск

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/your-username/ToDoList.git
cd ToDoList
```

### 2. Создайте и активируйте виртуальное окружение
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. Установите зависимости
```bash
pip install -r requirements.txt
```

### 4. Настройте переменные окружения
Создайте файл `.env` в папке `app/core` или в корне проекта:
```env
SMTP_USER='your_email@gmail.com'
SMTP_PASSWORD='your_app_password'
SMTP_SERVER='smtp.gmail.com'
SMTP_PORT=465
```

### 5. Запустите приложение
```bash
uvicorn app.main:app --reload
```

Приложение будет доступно по адресу: http://127.0.0.1:8000

---

## 🐳 Запуск через Docker (опционально)
Сначала соберите образ:
```bash
docker build -t todolist .
```

Для запуска приложения:
```bash
docker run -p 8000:8000 --env-file .env todolist
```

Для запуска тестов:
```bash
docker run --rm --env-file .env todolist "pytest"
```

---

## 🐳 Запуск через Docker Compose

Сначала убедитесь, что у вас есть файл `.env` в корне проекта (можно скопировать из `.env.example`).

Для запуска приложения:
```bash
docker-compose up --build
```

Приложение будет доступно по адресу: http://localhost:8000

Для запуска тестов (контейнер будет создан временно):
```bash
docker-compose run --rm app pytest
```

Для остановки приложения:
```bash
docker-compose down
```

---

## 🧪 Запуск тестов
Локально:
```bash
pytest
```
Через Docker:
```bash
docker run --rm --env-file .env todolist "pytest"
```

---

## 📁 Структура проекта
```
app/
  main.py           # Точка входа FastAPI
  core/             # Конфигурация и переменные окружения
  database/         # Модели, миграции, CRUD
  routes/           # Роуты (auth, todo, user)
  schemas/          # Pydantic-схемы
  static/           # Стили CSS
  templates/        # HTML-шаблоны
  utils/            # Email, безопасность, шаблоны

requirements.txt    # Зависимости
pytest.ini          # Настройки тестов
Dockerfile          # Docker-образ
```
