# Market with FastAPI

<img src="https://img.shields.io/badge/Python-3.9 | 3.10 | 3.11 | 3.12-blue">
<br>
<img src="https://img.shields.io/badge/FAST API-blue">
<img src="https://img.shields.io/badge/Celery-blue">
<img src="https://img.shields.io/badge/Flower-blue">
<img src="https://img.shields.io/badge/SQAlchemy-blue">
<img src="https://img.shields.io/badge/Pydentic-blue">
<img src="https://img.shields.io/badge/Redis-blue">
<img src="https://img.shields.io/badge/FastApi Cache-blue">
<img src="https://img.shields.io/badge/Alembic-blue">
<img src="https://img.shields.io/badge/JWT-blue">
<img src="https://img.shields.io/badge/PostgreSQL-blue">
<img src="https://img.shields.io/badge/Docker-blue">
<img src="https://img.shields.io/badge/Systemd-blue">
<img src="https://img.shields.io/badge/Uvicorn-blue">

## Установка

### Системные требования:
1. Python 3.9 и выше;
2. Linux (должно работать на Windows, но могут быть сложности с установкой);
3. Redis
4. Systemd (для запуска через systemd);
5. Docker (для запуска с Docker).

### Протестировать на своем локальном сервере:
1. Клонируйте репозиторий;
2. Перейдите (`cd`) в клонированный каталог и создайте виртуальное окружение Python (Virtual environment, venv);
3. Активируйте venv и установите все зависимости из `requirements.txt`;
4. Скопируйте `example.env` под именем `.env`, откройте его и заполните переменные;
5. Запустите через командную строку redis: `redis-server`
6. Внутри активированного venv: `app.main:app --host 127.0.0.1 --port 8000`.

### Загрузка на сервер
1. Выполните шаги 1-4 из раздела "Протестировать на своем локальном сервере" выше;
2. Скопируйте `tasker_api.example.service` в `tasker_api.service`, откройте и отредактируйте переменные `WorkingDirectory`,
 `ExecStart` и `Description`;
3. Скопируйте (или создайте симлинк) файла службы в каталог `/etc/systemd/system/`;
4. Активируйте сервис и запустите его: `sudo systemctl enable tasker_api`;
5. Проверьте, что сервис запустился: `systemctcl status tasker_api` (можно без root-прав).

### Docker + Docker Compose
1. Возьмите файл `env_example` там же, переименуйте как `.env` (с точкой в начале), откройте и заполните переменные;
2. Запустите бота: `docker compose up -d`;
3. Проверьте, что контейнер поднялся: `docker compose ps`

