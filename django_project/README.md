# Запуск
Из директории django_project/hasker
```
python manage.py runserver
```

# Конфигурационный файл
Конфигурация описывается в JSON-формате. Доступные параметры конфигурации:
- LOG_DIR - путь до директории с лог-файлами для анализа (по умолчанию: ./log)
- REPORT_DIR - путь до директории с результами отчетов анализа (по умолчанию: ./reports)
- REPORT_SIZE - количество записей, отображаемых в отчете анализа (по умолчанию: 1000)
- LOG_FILENAME - имя лог-файла приложения (Например, logs.txt)
- ERROR_THRESHOLD - допустимый порог ошибок в процентах (Например, 0.25)

# Запуск тестов
Тесты запускаются в директории `.\log_analyzer\tests`
### Windows
```
set PYTHONPATH=../
python test_log_analyzer.py
```

### Linux
```
PYTHONPATH=../ python test_log_analyzer.py
```
