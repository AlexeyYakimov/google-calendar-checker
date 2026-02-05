"""
Конфигурация для notifier модуля
"""

import os
from dotenv import load_dotenv

# Загрузить переменные окружения из .env файла
load_dotenv()

# Home Assistant webhook URL
WEBHOOK_URL = os.getenv(
    'WEBHOOK_URL',
    'http://homeassistant/api/webhook/-a8fA7xs4-Lx70P2l5EM-5Mwh'
)

# Таймаут для HTTP запросов (в секундах)
HTTP_TIMEOUT = int(os.getenv('HTTP_TIMEOUT', '10'))

# Часовой пояс для планировщика
TIMEZONE = os.getenv('TIMEZONE', 'Europe/Moscow')
