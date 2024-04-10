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

VOLUME /app/imgs
VOLUME /app/db

RUN mkdir temp
RUN mkdir /root/.streamlit
RUN echo "[general]" >> /root/.streamlit/credentials.toml
RUN echo "email = \"\"" >>/root/.streamlit/credentials.toml

# ["bash", "run.sh"]
ENTRYPOINT ["streamlit", "run", "Start.py", "--server.port=8501", "--server.address=0.0.0.0"]