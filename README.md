# Проект распознавания текста на изображении №27
# Садия проекта: ***MVP***

Этот проект демонстрирует распознавание текста на фотографии доски и интегрируется с Telegram и Zulip для отправки извлеченной информации.

## Спецификация

### Функционал

- **Распознавание текста на изображениях:** Извлекает текст из изображений с использованием различных моделей OCR (страница, многоколоночная страница, рукописный текст, таблицы).
- **Интеграция с Telegram:**
  - Отправляет распознанный текст указанным пользователям Telegram.
  - Позволяет прикреплять исходное изображение.
  - Хранит информацию о пользователях в локальной базе данных для упрощения взаимодействия.
- **Интеграция с Zulip:**
  - Отправляет распознанный текст указанным пользователям или потокам Zulip.
  - Позволяет указывать тему для сообщений в потоках.
  - Позволяет прикреплять исходное изображение.
- **Пакетная обработка:** Распознает текст из нескольких изображений в директории.
- **Периодическое сканирование:** Автоматически сканирует директорию на наличие новых изображений и обрабатывает их.

### Целевая аудитория:
- Преподаватели и лекторы, которые хотят делиться своими презентациями, лекциями и семинарами с аудиторией, коллегами или студентами других учебных заведений.
- Ученики и студенты, которые хотят сохранить информацию с доски в электронном виде, чтобы повторить материал, подготовиться к экзаменам или выполнить домашнее задание.
- Участники конференций, симпозиумов или воркшопов, которые хотят получить доступ к материалам, представленным на доске, или обсудить их с другими участниками.

### Какие юзкейсы могут быть у нашего сервиса?

- ***Учебная среда:***
Вы можете мгновенно получать и распространять лекционные или семинарские материалы с доски, не тратя время на записи и копирование.
- ***Конференции:***
Вы можете без труда запоминать и делиться ключевыми моментами выступлений, которые были представлены на доске. Просто сфотографируйте доску, и наше приложение преобразует все важные данные для анализа или обмена со слушателями.
- ***Деловые Встречи:***
Вы можете легко фиксировать и организовывать идеи, которые были вынесены на доску во время совещания. Сфотографируйте доску, и наше приложение создаст текстовый документ с этими идеями для последующего обсуждения.



## Технические характеристики
### Технические требования:
- Python 3.10+
- Docker и Docker Compose

### Требования к данным:
- Размер изображения не должен превышать 20 мегапикселей (длина × ширина).
- Формат файла .jpg, .png .jpeg.
- Размер файла не должен превышать 20МБ.
- На водящих изображениях текст должен быть хорошо виден.

### Метрики качества:
- Точность распознавания результатов составяет 0.9412244558 (94%) при использовании сторонней нейросети. 
- Пользователь получил сообщение с извлеченной информацией в Telegram/Zulip.

## Требования для MVP
- Веб-интерфейс.
- Загрузка изображения для последующего его анализа.
- Извлечение текстовой(рукописной и печатной) информации с загруженного фото.  
- Отправка извлеченной информации в Telegram.
- Отправка извлеченной информации в Zulip.
- Автоматическое распознавание адреса электронной почты и ника в Telegram на загруженном фото для дальнейшей отправки.
- Анализ сразу нескольких файлов одновременно.
- Возможность автоматического сканирования директории с изображениями с указанной периодичностью.

## Требования для MUP
- Требования для MVP.
- Оптимизация использования API, занимаемой памяти и скорости сборки.
- Интеграция с языковой моделью.
- Возможность использовать только локальные модели.

## Содержание репозитория
**Приложения:**
- `Start.py`, `pages/1_Manual_OCR.py`, `pages/2_Batch_processing`: Файлы основного приложения с веб-интерфейсом Streamlit.
- `reg_bot/bot.py`: Телеграм-бот для регистрации и управления пользователями.
- `background_service/bg.py`: Сервис для автоматического сканирования папки с фото.

**Модули:**
- `zulip_integration.py`: Функции для взаимодействия с API Zulip.
- `utilities.py`: Общие утилиты для обработки изображений, OCR и управления временными файлами.
- `telegram_integration.py`: Функции для взаимодействия с API Telegram Bot.
- `ai_integration.py`: Функции для взаимодействия с LLM.
- `local_ocr.py`: Функции для взаимодействия с локальной OCR.

**Дополнительные файлы:**
- `requirements.txt`, `reg_bot/requirements.txt`, `background_service/requirements.txt`: Список необходимых зависимостей для соответствующих сервисов.
- `docker-compose.yml`: Конфигурация Docker Compose для сборки и запуска сервиса.
- `docker-compose-gpu.yml`: Конфигурация Docker Compose для сборки и запуска сервиса с использованием GPU и локальными моделями.
- `README.md`: Документация разработчика.
- `Dockerfile_web`, `Dockerfile_web_gpu`, `Dockerfile_reg_bot`, `Dockerfile_background_service`: Докерфайлы для сборки образов отдельных сервисов.
- `.gitignore`, `.dockerignore`: Файлы для исключения из системы контроля версий и сборок Docker.
- `cfg/.env`: Шаблон файла окружения с необходимыми переменными конфигурации.

## Настройка

1. **Переменные окружения:** Заполните файл `.env` в директории `cfg` со следующими переменными:
    - `YC_OCR_ENDPOINT`: URL Yandex Cloud OCR API. См. [документацию Yandex Vision OCR](https://yandex.cloud/ru/docs/vision/ocr/api-ref/)
    - `YANDEX_API_KEY`: Ваш ключ API Yandex Cloud. См. [документацию Yandex Cloud](https://yandex.cloud/ru/docs/iam/concepts/authorization/api-key)
    - `TELEGRAM_BOT_TOKEN`: Ваш токен Telegram бота. См. [инструкция по получению Токена для Телеграм бота](https://www.cossa.ru/instahero/321374/)
    - `SCAN_PERIOD`: Временной интервал в секундах для периодического сканирования.
    - `USE_LOCAL`: Режим использования локальным нейросетей.
2. **Настройка Zulip:** Получите файл `zuliprc` с конфигурацией вашего бота Zulip и поместите его в директорию `cfg`. См. [документацию Zulip API](https://zulip.com/api/configuring-python-bindings#download-a-zuliprc-file) для получения подробной информации.

# Установка проекта на новое устройство

## С использованием сторонних нейросетей 

1. Скопируйте репозиторий:

`git clone https://git.miem.hse.ru/aimartinich/boardcv`

2. Произведите [настройку](https://wiki.miem.tv/doc/dokumentaciya-polzovatelya-pxh24njMFZ#h-nastrojka).
3. Для запуска приложения выполните команду `docker compose up -d`.
4. Перейдите адресу `http://localhost:8501` в браузере для открытия интерфейса.
5. Для остановки приложения выполните команду `docker compose down` находясь в директории с приложением.

## С использованием локальных нейросетей


1. Скопируйте репозиторий:

`git clone https://git.miem.hse.ru/aimartinich/boardcv`


2. Произведите [настройку](https://wiki.miem.tv/doc/dokumentaciya-polzovatelya-pxh24njMFZ#h-nastrojka).
3. Установите NVIDIA Container Toolkit. См. [документацию](https://github.com/ollama/ollama/blob/main/docs/docker.md#nvidia-gpu).
4. Установите CUDA драйвера для видеокарты. См. [документацию NVIDIA](https://developer.nvidia.com/cuda-downloads).
5. Для запуска приложения выполните команду `docker compose -f docker-compose-gpu.yml up -d`.
6. Перейдите адресу `http://localhost:8501` в браузере для открытия интерфейса.
7. Для остановки приложения выполните команду `docker compose down` находясь в директории с приложением.