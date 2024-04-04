# Берем нужный базовый образ
FROM python:3.11-slim

WORKDIR /app

# Копируем все файлы из текущей директории в /app контейнера
COPY . .

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем все зависимости
RUN pip install -r requirements.txt --no-cache-dir

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

RUN mkdir imgs
RUN mkdir db

VOLUME /app/imgs
VOLUME /app/db

ENTRYPOINT ["sh", "run.sh"]