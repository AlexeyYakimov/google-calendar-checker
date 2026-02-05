"""
Configuration constants for the Google Calendar Checker
"""

import os
from dotenv import load_dotenv

# Загрузить переменные окружения из .env файла
load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Get the directory where this config file is located
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

# File paths for credentials and tokens (can be overridden via env vars)
CREDENTIALS_FILE = os.getenv(
    'CREDENTIALS_FILE',
    os.path.join(_MODULE_DIR, 'credentials.json')
)
TOKEN_FILE = os.getenv(
    'TOKEN_FILE',
    os.path.join(_MODULE_DIR, 'token.json')
)

# Default calendar ID
DEFAULT_CALENDAR_ID = os.getenv('CALENDAR_ID', 'primary')

# Timezone for "today" and cache session (same as notifier)
TIMEZONE = os.getenv('TIMEZONE', 'Europe/Moscow')

# Polling configuration
POLL_START_HOUR = int(os.getenv('POLL_START_HOUR', '9'))
POLL_END_HOUR = int(os.getenv('POLL_END_HOUR', '19'))
POLL_INTERVAL_MINUTES = int(os.getenv('POLL_INTERVAL_MINUTES', '30'))
