#!/usr/bin/env python3
"""
Скрипт для проверки конфигурации проекта
"""

import os
import sys


def check_file(path, description):
    """Проверить наличие файла."""
    if os.path.exists(path):
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description} НЕ НАЙДЕН: {path}")
        return False


def check_config():
    """Проверить конфигурацию проекта."""
    print("=" * 60)
    print("Проверка конфигурации Google Calendar Checker")
    print("=" * 60)
    print()
    
    all_ok = True
    
    # Проверка credentials
    print("1. Google Calendar API:")
    all_ok &= check_file("calendar_checker/credentials.json", "Credentials")
    all_ok &= check_file("calendar_checker/token.json", "Token (опционально)")
    print()
    
    # Проверка модуля calendar_checker
    print("2. Модуль calendar_checker:")
    all_ok &= check_file("calendar_checker/__init__.py", "__init__.py")
    all_ok &= check_file("calendar_checker/auth.py", "auth.py")
    all_ok &= check_file("calendar_checker/config.py", "config.py")
    all_ok &= check_file("calendar_checker/operations.py", "operations.py")
    all_ok &= check_file("calendar_checker/scheduler.py", "scheduler.py")
    print()
    
    # Проверка модуля notifier
    print("3. Модуль notifier:")
    all_ok &= check_file("notifier/__init__.py", "__init__.py")
    all_ok &= check_file("notifier/config.py", "config.py")
    all_ok &= check_file("notifier/event_notifier.py", "event_notifier.py")
    all_ok &= check_file("notifier/webhook_sender.py", "webhook_sender.py")
    print()
    
    # Проверка точек входа
    print("4. Точки входа:")
    all_ok &= check_file("setup.py", "setup.py")
    all_ok &= check_file("run.py", "run.py")
    print()
    
    # Проверка зависимостей
    print("5. Зависимости:")
    all_ok &= check_file("requirements.txt", "requirements.txt")
    print()
    
    # Проверка .env файла
    print("6. Переменные окружения:")
    env_file_exists = check_file(".env", ".env файл (опционально)")
    if not env_file_exists:
        print("⚠ .env файл не найден - используются значения по умолчанию")
        print("  Создайте .env файл из .env.example для настройки")
    print()
    
    # Проверка конфигурации notifier
    print("7. Конфигурация Notifier:")
    try:
        from notifier.config import WEBHOOK_URL, TIMEZONE, HTTP_TIMEOUT
        print(f"✓ WEBHOOK_URL: {WEBHOOK_URL}")
        print(f"✓ TIMEZONE: {TIMEZONE}")
        print(f"✓ HTTP_TIMEOUT: {HTTP_TIMEOUT}")
        
        if 'homeassistant' in WEBHOOK_URL and 'YOUR' not in WEBHOOK_URL:
            print("⚠ Внимание: Возможно, нужно заменить 'homeassistant' на реальный IP/hostname")
        
        # Проверка источника конфигурации
        import os
        if os.getenv('WEBHOOK_URL'):
            print("  └─ Источник: переменные окружения (.env)")
        else:
            print("  └─ Источник: значения по умолчанию")
    except ImportError as e:
        print(f"✗ Ошибка импорта конфигурации: {e}")
        all_ok = False
    print()
    
    # Проверка конфигурации polling
    print("8. Конфигурация Polling:")
    try:
        from calendar_checker.config import POLL_START_HOUR, POLL_END_HOUR, POLL_INTERVAL_MINUTES
        print(f"✓ POLL_START_HOUR: {POLL_START_HOUR}")
        print(f"✓ POLL_END_HOUR: {POLL_END_HOUR}")
        print(f"✓ POLL_INTERVAL_MINUTES: {POLL_INTERVAL_MINUTES}")
        print(f"  └─ Часы работы: {POLL_START_HOUR}:00 - {POLL_END_HOUR}:00")
        
        # Проверка источника
        import os
        if os.getenv('POLL_START_HOUR'):
            print("  └─ Источник: переменные окружения (.env)")
        else:
            print("  └─ Источник: значения по умолчанию")
    except ImportError as e:
        print(f"✗ Ошибка импорта конфигурации: {e}")
        all_ok = False
    print()
    
    # Итог
    print("=" * 60)
    if all_ok:
        print("✓ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print()
        print("Можно запускать:")
        print("  python main.py           - разовая проверка")
        print("  python server.py         - сервер опроса")
        print("  python notifier_server.py - сервер уведомлений")
    else:
        print("✗ НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОЙДЕНЫ")
        print()
        print("Пожалуйста, исправьте ошибки перед запуском.")
    print("=" * 60)
    
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(check_config())
