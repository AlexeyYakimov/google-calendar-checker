#!/usr/bin/env python3
"""
Тест загрузки переменных окружения
"""

import os


def test_env_loading():
    """Проверить загрузку переменных окружения."""
    print("=" * 60)
    print("Тест загрузки переменных окружения")
    print("=" * 60)
    print()
    
    # Проверка .env файла
    env_exists = os.path.exists('.env')
    print(f"1. Файл .env: {'✓ существует' if env_exists else '✗ не найден'}")
    if not env_exists:
        print("   Создайте .env файл из .env.example")
    print()
    
    # Загрузка конфигураций
    print("2. Загрузка конфигурации notifier:")
    print("-" * 60)
    try:
        from notifier.config import WEBHOOK_URL, TIMEZONE, HTTP_TIMEOUT
        print(f"✓ WEBHOOK_URL: {WEBHOOK_URL}")
        print(f"✓ TIMEZONE: {TIMEZONE}")
        print(f"✓ HTTP_TIMEOUT: {HTTP_TIMEOUT}")
        
        # Проверка источника
        if os.getenv('WEBHOOK_URL'):
            print("  └─ Источник: .env файл")
        else:
            print("  └─ Источник: значения по умолчанию")
        print()
        notifier_ok = True
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        print()
        notifier_ok = False
    
    print("3. Конфигурация calendar_checker:")
    print("-" * 60)
    try:
        from calendar_checker.config import CREDENTIALS_FILE, TOKEN_FILE, DEFAULT_CALENDAR_ID
        print(f"✓ CREDENTIALS_FILE: {CREDENTIALS_FILE}")
        print(f"✓ TOKEN_FILE: {TOKEN_FILE}")
        print(f"✓ CALENDAR_ID: {DEFAULT_CALENDAR_ID}")
        
        # Проверка источника
        if os.getenv('CREDENTIALS_FILE'):
            print("  └─ Источник: .env файл")
        else:
            print("  └─ Источник: значения по умолчанию")
        print()
        calendar_ok = True
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        print()
        calendar_ok = False
    
    # Проверка конфигурации polling
    print("4. Конфигурация Polling:")
    print("-" * 60)
    try:
        from calendar_checker.config import POLL_START_HOUR, POLL_END_HOUR, POLL_INTERVAL_MINUTES
        print(f"✓ POLL_START_HOUR: {POLL_START_HOUR}")
        print(f"✓ POLL_END_HOUR: {POLL_END_HOUR}")
        print(f"✓ POLL_INTERVAL_MINUTES: {POLL_INTERVAL_MINUTES}")
        print(f"  └─ Расписание: каждые {POLL_INTERVAL_MINUTES} мин с {POLL_START_HOUR}:00 до {POLL_END_HOUR}:00")
        
        # Проверка источника
        if os.getenv('POLL_START_HOUR'):
            print("  └─ Источник: .env файл")
        else:
            print("  └─ Источник: значения по умолчанию")
        print()
        polling_ok = True
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        print()
        polling_ok = False
    
    # Проверка python-dotenv
    print("5. Проверка зависимостей:")
    print("-" * 60)
    try:
        import dotenv
        print(f"✓ python-dotenv установлен (версия: {dotenv.__version__})")
    except ImportError:
        print("✗ python-dotenv не установлен")
        print("  Установите: pip install python-dotenv")
    print()
    
    # Итог
    print("=" * 60)
    if notifier_ok and calendar_ok and polling_ok:
        print("✓ ВСЕ КОНФИГУРАЦИИ ЗАГРУЖЕНЫ УСПЕШНО!")
        print()
        if not env_exists:
            print("⚠ Рекомендация: Создайте .env файл для настройки")
            print("  cp .env.example .env")
        else:
            print("✓ Проект готов к использованию")
    else:
        print("✗ ОШИБКИ ПРИ ЗАГРУЗКЕ КОНФИГУРАЦИИ")
        print()
        print("Рекомендации:")
        print("1. Убедитесь что python-dotenv установлен")
        print("2. Проверьте правильность импортов")
        print("3. Запустите: pip install -r requirements.txt")
    print("=" * 60)


if __name__ == '__main__':
    test_env_loading()
