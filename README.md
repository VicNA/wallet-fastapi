# Wallet API

## Описание

Проект реализует REST API для управления кошельками пользователей с поддержкой конкурентных операций. Позволяет изменять баланс (пополнение/снятие) и получать текущий баланс. Приложение написано на **Python 3.13** с использованием **FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL** и **asyncpg**. Контейнеризация через **Docker** и **docker-compose**. Вся система запускается **одной командой** – соответствует требованию задания.

## Основные возможности

- Получение баланса кошелька
- Пополнение кошелька (DEPOSIT)
- Снятие средств (WITHDRAW)
- Защита от отрицательного баланса
- Атомарные операции на уровне БД
- Обработка конкурентных запросов (race condition)
- Асинхронный стек (FastAPI + SQLAlchemy)

## Стек технологий

- **Язык**: Python 3.13
- **Фреймворк**: FastAPI
- **ORM**: SQLAlchemy (асинхронный режим с `asyncpg` для PostgreSQL и `aiosqlite` для тестов)
- **База данных**:
  - Продакшен: PostgreSQL
  - Тесты: SQLite в памяти
- **Тестирование**: `pytest`, `pytest-asyncio`, `httpx`
- **Валидация**: Pydantic
- **Логирование**: Python `logging`
- **Контейнеризация**: Docker (опционально, с `docker-compose` для PostgreSQL)

## Установка

### Требования

- Python 3.13
- Docker (опционально, для запуска базы данных)

### Установка зависимостей

1. Склонируйте репозиторий:

   ```bash
   git clone https://github.com/VicNA/wallet-fastapi.git
   cd wallet-fastapi
   ```

2. Создайте виртуальное окружение и активируйте его:

   ```bash
   python -m venv .venv       # Создать через venv
   source .venv/bin/activate  # Linux/MacOS
   .venv\Scripts\activate     # Windows
   ```

3. Установите зависимости:

   ```bash
   pip install -r requirements.txt  # Установить через venv
   ```

4. Запустить через docker compose:

    ```bash
    docker compose up --build -d
    ```

### Swagger UI: http://localhost:8000/api/docs
