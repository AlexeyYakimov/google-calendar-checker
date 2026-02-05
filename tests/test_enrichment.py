#!/usr/bin/env python3
"""
Тестовый скрипт для проверки обогащения событий
"""

from calendar_checker import get_calendar_service, get_today_events


def test_enrichment():
    """Тест функции обогащения событий."""
    print("=" * 60)
    print("Тест обогащения событий")
    print("=" * 60)
    print()
    
    # Получить сервис
    print("Инициализация Google Calendar service...")
    service = get_calendar_service()
    print("✓ Сервис инициализирован")
    print()
    
    # Тест 1: Без обогащения
    print("Тест 1: Получение событий БЕЗ обогащения")
    print("-" * 60)
    events_normal = get_today_events(service, enrich=False)
    
    if events_normal:
        event = events_normal[0]
        print()
        print("Пример события (без обогащения):")
        print(f"  ID: {event.get('id')}")
        print(f"  Название: {event.get('summary', 'Без названия')}")
        print(f"  Поле duration_minutes: {event.get('duration_minutes', 'ОТСУТСТВУЕТ')}")
    print()
    
    # Тест 2: С обогащением
    print("=" * 60)
    print("Тест 2: Получение событий С обогащением (enrich=True)")
    print("-" * 60)
    events_enriched = get_today_events(service, enrich=True)
    
    if events_enriched:
        event = events_enriched[0]
        print()
        print("Пример события (с обогащением):")
        print(f"  ID: {event.get('id')}")
        print(f"  Название: {event.get('summary', 'Без названия')}")
        print(f"  Поле duration_minutes: {event.get('duration_minutes', 'ОТСУТСТВУЕТ')}")
        
        duration = event.get('duration_minutes')
        if duration:
            print(f"  ✓ Длительность успешно рассчитана: {duration} минут")
        else:
            print(f"  ⚠ Длительность не рассчитана (возможно, событие на весь день)")
    print()
    
    # Итог
    print("=" * 60)
    print("Результат:")
    if events_normal and events_enriched:
        has_duration_before = 'duration_minutes' in events_normal[0]
        has_duration_after = 'duration_minutes' in events_enriched[0]
        
        if not has_duration_before and has_duration_after:
            print("✓ ТЕСТ ПРОЙДЕН!")
            print("  - Без enrich=True: поле duration_minutes отсутствует")
            print("  - С enrich=True: поле duration_minutes присутствует")
        else:
            print("✗ ТЕСТ НЕ ПРОЙДЕН")
            print(f"  - duration_minutes без enrich: {has_duration_before}")
            print(f"  - duration_minutes с enrich: {has_duration_after}")
    else:
        print("⚠ Недостаточно событий для теста")
    print("=" * 60)


if __name__ == '__main__':
    test_enrichment()
