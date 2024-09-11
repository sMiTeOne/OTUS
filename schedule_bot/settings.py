import configparser

config = configparser.ConfigParser()
config.read('config.ini')


# Telegram Settings
TELEGRAM_API_TOKEN = config['TELEGRAM']['API_TOKEN']

# Yandex Schedule Settings
YANDEX_API_ADDESS = config['YANDEX']['API_ADDRESS']
YANDEX_API_TOKEN = config['YANDEX']['API_TOKEN']

# Storage Settings
STORAGE_DB_NAME = config['STORAGE']['DB_NAME']
STORAGE_DB_HOST = config['STORAGE']['DB_HOST']
STORAGE_DB_PORT = config['STORAGE']['DB_PORT']
