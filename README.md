# Warehold

Тестовое задание в Effective Mobile: REST API с использованием FastAPI для управления процессами на складе.

## Установка

Создайте файл `prod.env` если для докера и `.env` если для локального развертывания (можно оба одновременно) и вставьте туда переменные окружения от вашего PostgreSQL, например (.env, для локального):
```bash
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres
DB_NAME=db
DB_HOST=localhost # DB_HOST=db (для компоуз файла этого репозитория)
```

Примечание: `DB_HOST` должен соответствовать названию нетворка в `docker-compose.yml` в `prod.env`, для локального развертывания по умолчанию `localhost`

### Docker Compose
Запуск контейнеров:
```bash
docker-compose up --build
```
### Локальный запуск 
Создаем окружение, устанавливаем зависимости:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Создаем бд скриптом, запускаем сервер:
```bash
cd application
python3 create_db.py
uvicorn main:app --reload
```