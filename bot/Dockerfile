FROM python:3.11-slim

# Установка PostgreSQL зависимостей
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY . /app

# Установка рабочей директории
WORKDIR /app

# Запуск приложения
CMD ["python", "Bot.py"]
