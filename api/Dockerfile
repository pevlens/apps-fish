# Используем облегчённый образ Python для production
FROM python:3.10.12-slim

# Устанавливаем системные зависимости (например, для сборки psycopg2)
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Устанавливаем переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Задаём рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Копируем исходный код проекта
COPY . .

# Открываем порт (можно указать другой, если требуется)
EXPOSE 5000

# Запускаем приложение с помощью Gunicorn
CMD ["python", "api.py"]
