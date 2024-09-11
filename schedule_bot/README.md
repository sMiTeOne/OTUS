# Развертывание
1. Запустить базу данных Tarantool
```
docker-compose up -d
```
2. Наполнить базу данных данными
```
python init.py
```

# Конфигурация
Конфигурация бота хранится в `config.ini`. Параметры:
TELEGRAM
- API_TOKEN - API-токен телеграмм-бота
YANDEX
API_ADDRESS - адрес API Yandex.Расписания
API_TOKEN - API-токен Yandex.Расписания
STORAGE
- DB_NAME - название базы данных
- DB_HOST - адрес базы данных
- DB_PORT - порт базы данных
