#!/usr/bin/env python3
"""
Первичная настройка - получение OAuth токена от Google Calendar API

Запустите этот скрипт один раз для авторизации:
    python setup.py

После успешной авторизации токен сохранится в calendar_checker/token.json
"""

import os
import sys

print("=" * 60)
print("Google Calendar Checker - Первичная настройка")
print("=" * 60)
print()

# Проверка credentials.json
credentials_path = "calendar_checker/credentials.json"
if not os.path.exists(credentials_path):
    print("❌ Ошибка: credentials.json не найден!")
    print()
    print("Пожалуйста, выполните следующие шаги:")
    print("1. Перейдите в Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    print("2. Создайте проект и включите Google Calendar API")
    print("3. Создайте OAuth 2.0 Client ID")
    print("4. Скачайте credentials.json")
    print(f"5. Поместите его в: {credentials_path}")
    print()
    sys.exit(1)

print(f"✓ Найден credentials.json")
print()

# Попытка аутентификации
print("Запуск процесса аутентификации...")
print("Сейчас откроется браузер для авторизации Google.")
print()

try:
    from calendar_checker import get_calendar_service
    
    service = get_calendar_service()
    
    print()
    print("=" * 60)
    print("✅ УСПЕШНО!")
    print("=" * 60)
    print()
    print("Токен сохранен в: calendar_checker/token.json")
    print()
    print("Теперь можно запустить сервис:")
    print("    python run.py")
    print()
    
except Exception as e:
    print()
    print("=" * 60)
    print("❌ ОШИБКА!")
    print("=" * 60)
    print()
    print(f"Ошибка аутентификации: {e}")
    print()
    sys.exit(1)
